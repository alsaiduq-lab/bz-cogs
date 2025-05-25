from redbot.core import app_commands
from ..config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT


def owner_check():
    async def predicate(inter):
        cog = inter.client.get_cog("AIUser")
        if inter.guild:
            return inter.user.guild_permissions.administrator
        owners = await inter.client.application_info().owner
        owner_ids = {owners.id} if hasattr(owners, "id") else {m.id for m in owners.members}
        accepted_ids = set(await cog.config.accepted_ids() or [])
        return (inter.user.id in owner_ids) or (inter.user.id in accepted_ids)

    return app_commands.check(predicate)


async def get_owner_ids(inter):
    owners = await inter.client.application_info().owner
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
