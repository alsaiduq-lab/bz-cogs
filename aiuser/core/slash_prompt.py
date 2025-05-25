import discord
from redbot.core import app_commands
from discord.app_commands import Group
from aiuser.config.defaults import DEFAULT_PROMPT, DEFAULT_DM_PROMPT


@app_commands.command(
    name="aiuser_prompt",
    description="Show or set the prompt for this AI. Use subcommands: show, set.",
)
async def aiuser_prompt(inter: discord.Interaction):
    await inter.response.send_message(
        "See the subcommands:\n/aiuser_prompt show - Show current prompt\n/aiuser_prompt set - Set a new prompt\n",
        ephemeral=True,
    )


aiuser_prompt_group = Group(name="aiuser_prompt", description="Show or set the AI prompt.")


def get_config_section(cog, inter):
    if inter.guild:
        return cog.config.guild(inter.guild)
    else:
        return cog.config.user(inter.user)


@aiuser_prompt_group.command(name="show", description="Show the current prompt.")
async def prompt_show(inter: discord.Interaction):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return
    config_section = get_config_section(cog, inter)
    if inter.guild:
        val = await config_section.custom_text_prompt() or await cog.config.custom_text_prompt() or DEFAULT_PROMPT
        await inter.response.send_message(f"**Server prompt:**\n{val}", ephemeral=True)
    else:
        val = await cog.config.dm_prompt() or await cog.config.custom_text_prompt() or DEFAULT_DM_PROMPT
        await inter.response.send_message(f"**DM prompt:**\n{val}", ephemeral=True)


@aiuser_prompt_group.command(name="set", description="Set a new prompt.")
@app_commands.describe(prompt="The new prompt text. Leave blank to reset to default.")
async def prompt_set(inter: discord.Interaction, prompt: str = None):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return
    config_section = get_config_section(cog, inter)
    if inter.guild:
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
