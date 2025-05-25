import discord
from redbot.core import app_commands
from .slash import owner_check
from aiuser.config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT

from discord.app_commands import Group

aiuser_prompt_group = Group(
    name="aiuser_prompt",
    description="Show or set the prompt for this AI.",
)


def get_config_section(cog, inter):
    if inter.guild:
        return cog.config.guild(inter.guild)
    else:
        return cog.config.dm_prompt


@aiuser_prompt_group.command(name="show", description="Show the current prompt.")
async def prompt_show(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if inter.guild:
        val = (
            await cog.config.guild(inter.guild).custom_text_prompt()
            or await cog.config.custom_text_prompt()
            or DEFAULT_PROMPT
        )
        await inter.response.send_message(f"**Server prompt:**\n{val}", ephemeral=True)
    else:
        val = await cog.config.dm_prompt() or await cog.config.custom_text_prompt() or DEFAULT_DM_PROMPT
        await inter.response.send_message(f"**DM prompt:**\n{val}", ephemeral=True)


@aiuser_prompt_group.command(name="set", description="Set a new prompt.")
@owner_check()
@app_commands.describe(prompt="The new prompt text. Leave blank to reset to default.")
async def prompt_set(inter: discord.Interaction, prompt: str = None):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if inter.guild:
        config_section = cog.config.guild(inter.guild)
        if not prompt:
            await config_section.custom_text_prompt.set(None)
            await inter.response.send_message("Prompt reset to default.", ephemeral=True)
        else:
            await config_section.custom_text_prompt.set(prompt)
            await inter.response.send_message(f"Prompt set:\n{prompt}", ephemeral=True)
    else:
        if not prompt:
            await cog.config.dm_prompt.set(None)
            await inter.response.send_message("DM prompt reset to default.", ephemeral=True)
        else:
            await cog.config.dm_prompt.set(prompt)
            await inter.response.send_message(f"DM prompt set:\n{prompt}", ephemeral=True)


@aiuser_prompt_group.command(name="lobotomize", description="Reset the prompt to default.")
@owner_check()
async def prompt_lobotomize(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if inter.guild:
        await cog.config.guild(inter.guild).custom_text_prompt.set(None)
        await inter.response.send_message("Server prompt has been reset to default. Lobotomy complete.", ephemeral=True)
    else:
        await cog.config.dm_prompt.set(None)
        await inter.response.send_message("DM prompt has been reset to default. Lobotomy complete.", ephemeral=True)


@app_commands.command(name="lobotomize", description="Reset the prompt to default.")
@owner_check()
async def global_lobotomize(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if inter.guild:
        await cog.config.guild(inter.guild).custom_text_prompt.set(None)
        await inter.response.send_message("Server prompt has been reset to default.", ephemeral=True)
    else:
        await cog.config.dm_prompt.set(None)
        await inter.response.send_message("DM prompt has been reset to default.", ephemeral=True)
