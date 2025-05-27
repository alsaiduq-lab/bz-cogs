import os
import discord
from redbot.core import app_commands
from ..openai_utils import setup_openai_client
from .slash_utils import owner_check
from typing import Optional
import logging
import httpx

logger = logging.getLogger("red.bz_cogs.aiuser")

ENDPOINTS = {
    "openai": "https://api.openai.com/v1/",
    "openrouter": "https://openrouter.ai/api/v1/",
    "ollama": "http://localhost:11434/v1/",
    "grok": "https://api.grok.x.ai/v1/",
}
API_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "grok": "XAI_API_KEY",
}


@app_commands.command(
    name="aiuser_endpoint",
    description="Set or update the OpenAI API endpoint.",
)
@app_commands.describe(
    url="Custom OpenAI API compatible endpoint URL, or 'openai', 'openrouter', 'ollama', 'grok'.",
    api_key="(Optional) API key for this endpoint.",
)
@owner_check()
async def aiuser_endpoint(inter: discord.Interaction, url: Optional[str], api_key: Optional[str] = None):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("AIUser Cog not loaded!", ephemeral=True)
        return

    if not hasattr(cog, "bot") or not hasattr(cog, "config") or not hasattr(cog, "openai_client"):
        err_msg = "AIUser Cog is missing critical attributes (bot, config, or openai_client)."
        logger.error(err_msg)
        await inter.response.send_message(err_msg, ephemeral=True)
        return

    if not inter.response.is_done():
        await inter.response.defer(ephemeral=True, thinking=True)

    input_url = url or ""
    url = (url or "openai").strip().lower()

    if url in ("", "openai"):
        endpoint_type = "openai"
        api_url = ENDPOINTS["openai"]
    elif url == "openrouter":
        endpoint_type = "openrouter"
        api_url = ENDPOINTS["openrouter"]
    elif url == "ollama":
        endpoint_type = "ollama"
        api_url = ENDPOINTS["ollama"]
    elif url == "grok":
        endpoint_type = "grok"
        api_url = ENDPOINTS["grok"]
    else:
        url_lower = url.lower()
        if "openrouter" in url_lower:
            endpoint_type = "openrouter"
        elif "ollama" in url_lower:
            endpoint_type = "ollama"
        elif "grok" in url_lower or "x.ai" in url_lower:
            endpoint_type = "grok"
        else:
            endpoint_type = "custom"
        api_url = input_url

    env_var = API_ENV_VARS.get(endpoint_type)
    effective_api_key = api_key or (os.getenv(env_var) if env_var else None)

    error_msg = None
    try:
        if endpoint_type == "openai":
            cog.endpoint_url = api_url
            cog.openai_client = await setup_openai_client(cog.bot, cog.config)
            if not cog.openai_client:
                error_msg = "Client setup returned None."
        elif endpoint_type == "ollama" or endpoint_type == "openrouter":
            cog.endpoint_url = api_url
            headers = {}
            if effective_api_key:
                headers["Authorization"] = f"Bearer {effective_api_key}"
            async with httpx.AsyncClient(timeout=8) as client:
                r = await client.get(api_url + "models", headers=headers)
                if r.status_code != 200:
                    error_msg = f"{endpoint_type.title()} error: {r.text}"
        elif endpoint_type == "grok":
            cog.endpoint_url = api_url
            headers = {"Authorization": f"Bearer {effective_api_key}"} if effective_api_key else {}
            async with httpx.AsyncClient(timeout=8) as client:
                r = await client.get(api_url + "models", headers=headers)
        elif endpoint_type == "custom":
            cog.endpoint_url = api_url
    except Exception as e:
        logger.error(f"Failed to setup endpoint '{api_url}': {e}", exc_info=True)
        error_msg = f":warning: Failed to initialize client for `{input_url or api_url}`. Error: {e}"

    if error_msg:
        await inter.followup.send(error_msg, ephemeral=True)
        return

    msg = f"✅ Endpoint set to `{api_url}` ({endpoint_type}) successfully.\n"
    if api_key:
        msg += "API key updated for this endpoint.\n"
    elif effective_api_key:
        msg += "API key pulled from environment.\n"
    else:
        msg += "No API key was set or found in environment.\n"

    msg += "You may need to set your model for this endpoint using `/aiuser model`."
    embed = discord.Embed(title="Endpoint Updated", description=msg, color=discord.Color.green())
    await inter.followup.send(embed=embed, ephemeral=True)
