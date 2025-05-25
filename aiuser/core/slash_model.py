import discord  # type: ignore
from redbot.core import app_commands  # type: ignore
from discord.app_commands import Group  # type: ignore
from typing import Optional
from aiuser.settings.utilities import get_available_models


@app_commands.command(
    name="aiuser_model",
    description="Manage or list AI models. Use subcommands: set, get, list.",
)
async def aiuser_model(inter: discord.Interaction):
    await inter.response.send_message(
        "**Subcommands:**\n"
        "`/aiuser_model set <model>` — Set the model for this server or your DMs\n"
        "`/aiuser_model get` — Show the current model\n"
        "`/aiuser_model list` — List available models from this endpoint",
        ephemeral=True,
    )


aiuser_model_group = Group(name="aiuser_model", description="Manage or list AI models.")


@aiuser_model_group.command(name="set", description="Set the AI model for this server or your DMs.")
@app_commands.describe(model="The model to set. Use 'unset' to clear.")
async def set_model(inter: discord.Interaction, model: Optional[str]):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if model is None:
        await inter.response.send_message("Model cannot be empty. Use 'unset' to clear the model.", ephemeral=True)
        return

    model_to_set = None if model.lower() == "unset" else model

    if inter.guild:
        await cog.config.guild(inter.guild).model.set(model_to_set)
        await inter.response.send_message(f"Set **server** model to: `{model_to_set or 'unset'}`", ephemeral=True)
    else:
        await cog.config.user(inter.user).dm_model.set(model_to_set)
        await inter.response.send_message(f"Set **your DM** model to: `{model_to_set or 'unset'}`", ephemeral=True)


@aiuser_model_group.command(name="get", description="Get the current AI model for this server or your DMs.")
async def get_model(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if inter.guild:
        model = await cog.config.guild(inter.guild).model()
        await inter.response.send_message(f"Current **server** model: `{model or 'unset'}`", ephemeral=True)
    else:
        model = await cog.config.user(inter.user).dm_model()
        await inter.response.send_message(f"Your current **DM** model: `{model or 'unset'}`", ephemeral=True)


@aiuser_model_group.command(name="list", description="List available models from the current endpoint.")
async def list_models(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog or not hasattr(cog, "openai_client"):
        await inter.response.send_message("Cog or OpenAI client not loaded!", ephemeral=True)
        return
    models = await get_available_models(cog.openai_client)
    if not models:
        await inter.response.send_message("No models available.", ephemeral=True)
        return
    desc = "\n".join(f"{m}" for m in models)
    embed = discord.Embed(
        title="Available models",
        description=desc[:4090] + "..." if len(desc) > 4090 else desc,
        color=discord.Color.blurple(),
    )
    await inter.response.send_message(embed=embed, ephemeral=True)
