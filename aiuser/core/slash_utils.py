import re
from redbot.core import app_commands, commands
from ..config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT, DEFAULT_REMOVE_PATTERNS
from aiuser.messages_list.messages import create_messages_list
from aiuser.response.chat.response import create_chat_response
from aiuser.types.abc import MixinMeta


def clean_response(response: str) -> str:
    if not response or not isinstance(response, str):
        return ""
    cleaned = response.strip(" \n")
    for pattern in DEFAULT_REMOVE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip(" \n")
    return cleaned


async def patched_response_handler(cog: MixinMeta, ctx: commands.Context, messages_list=None) -> str:
    """Handle slash command response using the same logic as regular messages"""
    messages_list = messages_list or await create_messages_list(cog, ctx)

    try:
        raw_response = await create_chat_response(cog, ctx, messages_list)
        if raw_response and isinstance(raw_response, str):
            return clean_response(raw_response)
        return ""
    except Exception:
        raw_response = await create_chat_response(cog, ctx, messages_list)
        if raw_response and isinstance(raw_response, str):
            return clean_response(raw_response)
        return ""


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
