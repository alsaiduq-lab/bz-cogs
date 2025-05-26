import re
import discord
from redbot.core import commands, app_commands, Config
from ..config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT, DEFAULT_REMOVE_PATTERNS


async def patched_response_handler(ctx: commands.Context, config: Config, response: str) -> str:
    if ctx.guild is not None:
        patterns = await config.guild(ctx.guild).removelist_regexes()
        botname = ctx.message.guild.me.nick or ctx.bot.user.display_name
        authors = {msg.author.display_name async for msg in ctx.channel.history(limit=10) if msg.author != ctx.guild.me}
    else:
        patterns = DEFAULT_REMOVE_PATTERNS
        botname = ctx.bot.user.display_name
        authors = {ctx.message.author.display_name}

    expanded_patterns = []
    for pattern in patterns:
        p = pattern
        if "{botname}" in p:
            p = p.replace(r"{botname}", botname)
        if "{authorname}" in p:
            for author in authors:
                expanded_patterns.append(p.replace(r"{authorname}", author))
        else:
            expanded_patterns.append(p)

    cleaned = response.strip(" \n")
    for pattern in expanded_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip(" \n")
    return cleaned


def owner_check():
    async def predicate(inter):
        cog = inter.client.get_cog("AIUser")
        if inter.guild:
            return inter.user.guild_permissions.administrator
        appinfo = await inter.client.application_info()
        owners = appinfo.owner
        owner_ids = {owners.id} if hasattr(owners, "id") else {m.id for m in owners.members}
        accepted_ids = set(await cog.config.accepted_ids() or [])
        return (inter.user.id in owner_ids) or (inter.user.id in accepted_ids)

    return app_commands.check(predicate)


async def get_owner_ids(inter):
    appinfo = await inter.client.application_info()
    owners = appinfo.owner
    if hasattr(owners, "id"):
        return {owners.id}
    return {m.id for m in owners.members}


async def get_prompt(cog, ctx):
    if ctx.guild:
        return (
            await cog.config.guild(ctx.guild).custom_text_prompt()
            or await cog.config.custom_text_prompt()
            or DEFAULT_PROMPT
        )
    else:
        return await cog.config.dm_prompt() or await cog.config.custom_text_prompt() or DEFAULT_DM_PROMPT
