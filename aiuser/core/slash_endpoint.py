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

    if url == "openrouter":
        url = "https://openrouter.ai/api/v1/"
    elif url == "ollama":
        url = "http://localhost:11434/v1/"
    elif url in ["clear", "reset", "openai"]:
        url = None
    else:
        url = url or "https://api.openai.com/v1/"

    previous_config_url = await cog.config.custom_openai_endpoint()
    await cog.config.custom_openai_endpoint.set(url)

    cog.openai_client = await setup_openai_client(cog.bot, cog.config)
    if not cog.openai_client:
        await cog.config.custom_openai_endpoint.set(previous_config_url)
        await inter.followup.send(
            ":warning: Could not initialize OpenAI client for this endpoint. Endpoint reverted.",
            ephemeral=True,
        )
        return

    try:
        await cog.openai_client.models.list()
    except Exception as e:
        logger.error(f"Failed to test endpoint '{url}': {e}", exc_info=True)
        await cog.config.custom_openai_endpoint.set(previous_config_url)
        await inter.followup.send(
            ":warning: Invalid endpoint. Please check logs for more information.",
            ephemeral=True,
        )
        return

    success_message = f"✅ Endpoint set to `{url or 'Official OpenAI'}` and tested successfully."
    if url != previous_config_url:
        success_message += "\nNote: Guild model defaults may need to be updated based on this new endpoint."

    embed = discord.Embed(title="Endpoint Updated", description=success_message, color=discord.Color.green())
    await inter.followup.send(embed=embed, ephemeral=True)
