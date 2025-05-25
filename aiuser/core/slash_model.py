import discord
from redbot.core import app_commands

from ..utils.utilities import get_available_models

aiuser_model_group = app_commands.Group(
    name="aiuser_model",
    description="Manage or list AI models."
)

@aiuser_model_group.command(
    name="set",
    description="Set the AI model for user apps.",
)
@app_commands.describe(model="The model to set for DMs/user apps.")
async def set_model(inter: discord.Interaction, model: str):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    await cog.config.dm_model.set(model)
    await inter.response.send_message(f"Set DM model to: {model}", ephemeral=True)

@aiuser_model_group.command(
    name="get",
    description="Get the current AI model for user apps.",
)
async def get_model(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    val = await cog.config.dm_model()
    await inter.response.send_message(f"Current DM model: {val or 'gpt-4o'}", ephemeral=True)

@aiuser_model_group.command(
    name="list",
    description="List available models from the current endpoint.",
)
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
        title="Available AI Models",
        description=desc[:4090] + "..." if len(desc) > 4090 else desc,
        color=discord.Color.blurple(),
    )
    await inter.response.send_message(embed=embed, ephemeral=True)

# To add in your main loader:
# tree.tree.add_command(aiuser_model_group)

