import re
import discord
import asyncio
from redbot.core import app_commands, Config
from ..config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT, DEFAULT_REMOVE_PATTERNS


async def patched_response_handler(inter: discord.Interaction, config: Config, response: str) -> str:
    cleaned = response.strip(" \n")
    try:
        if inter.guild is None:
            patterns = DEFAULT_REMOVE_PATTERNS
        else:
            patterns = await config.guild(inter.guild).removelist_regexes()
            botname = inter.guild.me.nick or inter.client.user.display_name
            patterns = [p.replace(r"{botname}", botname) for p in patterns]
            authors = {
                msg.author.display_name async for msg in inter.channel.history(limit=10) if msg.author != inter.guild.me
            }
            expanded_patterns = []
            for pattern in patterns:
                if "{authorname}" in pattern:
                    for author in authors:
                        expanded_patterns.append(pattern.replace(r"{authorname}", author))
                else:
                    expanded_patterns.append(pattern)
            patterns = expanded_patterns

        for pattern in patterns:
            try:
                pattern_compiled = re.compile(pattern, flags=re.DOTALL | re.IGNORECASE)
                cleaned = pattern_compiled.sub("", cleaned).strip(" \n")
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

        cleaned = re.sub(r"(?i)<\s*think\s*>[\s\S]*?(?=$)", "", cleaned, flags=re.DOTALL).strip()
    except Exception:
        pass
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
