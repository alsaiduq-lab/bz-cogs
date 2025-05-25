import discord
from redbot.core import app_commands
from aiuser.core.openai_utils import setup_openai_client
from .slash_utils import owner_check
from typing import Optional
import logging

logger = logging.getLogger("red.bz_cogs.aiuser")


@app_commands.command(
    name="aiuser_endpoint",
    description="Set or update the OpenAI API endpoint.",
)
@app_commands.describe(url="Custom OpenAI API compatible endpoint URL, or 'openai', 'openrouter', 'ollama'.")
@owner_check()
async def aiuser_endpoint(inter: discord.Interaction, url: Optional[str]):
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

    orig_input_url = url
    if url == "openrouter":
        url = "https://openrouter.ai/api/v1/"
    elif url == "ollama":
        url = "http://localhost:11434/v1/"
    elif url in ("openai", None, "", "clear", "reset"):
        url = "https://api.openai.com/v1/"

    prev_url = await cog.config.custom_openai_endpoint()
    await cog.config.custom_openai_endpoint.set(url)

    try:
        cog.openai_client = await setup_openai_client(cog.bot, cog.config)
        if not cog.openai_client:
            raise ConnectionError("Client setup returned None.")
    except Exception as e_setup:
        logger.error(f"Failed to setup client for endpoint '{url}': {e_setup}", exc_info=True)
        await cog.config.custom_openai_endpoint.set(prev_url)
        await inter.followup.send(
            f":warning: Failed to initialize client for `{orig_input_url or 'default'}`. Endpoint reverted. Error: {e_setup}",
            ephemeral=True,
        )
        return

    try:
        await cog.openai_client.models.list()
    except Exception as e_test:
        logger.error(f"Failed to test endpoint '{url}': {e_test}", exc_info=True)
        await cog.config.custom_openai_endpoint.set(prev_url)
        await inter.followup.send(
            f":warning: New endpoint `{orig_input_url or 'default'}` failed test. Endpoint reverted. Error: {e_test}",
            ephemeral=True,
        )
        return

    success_message = f"✅ Endpoint set to `{url or 'Official OpenAI'}` and tested successfully.\n"
    success_message += "You may need to set your model for this endpoint using `/aiuser model` (in server or DM)."

    if url != prev_url:
        success_message += "\nNote: Guild/user model defaults are not automatically changed based on this new endpoint."

    embed = discord.Embed(title="Endpoint Updated", description=success_message, color=discord.Color.green())
    await inter.followup.send(embed=embed, ephemeral=True)
