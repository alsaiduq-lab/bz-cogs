import discord
from redbot.core import app_commands
from aiuser.core.handlers import handle_slash_command
from aiuser.config.defaults import (
    DEFAULT_PROMPT,
    DEFAULT_DM_PROMPT,
)


async def get_prompt(cog, ctx):
    if ctx.guild:
        return (
            await cog.config.guild(ctx.guild).custom_text_prompt()
            or await cog.config.custom_text_prompt()
            or DEFAULT_PROMPT
        )
    else:
        return await cog.config.dm_prompt() or await cog.config.custom_text_prompt() or DEFAULT_DM_PROMPT


@app_commands.command(
    name="chat",
    description="Talk directly to this bot's AI. Ask it anything you want!",
)
@app_commands.describe(text="The prompt you want to send to the AI.")
@app_commands.checks.cooldown(1, 30)
@app_commands.checks.cooldown(1, 5, key=None)
async def chat_slash_command(inter: discord.Interaction, text: str):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return
    if not (1 <= len(text) <= 2000):
        await inter.response.send_message("Text must be between 1 and 2000 characters.", ephemeral=True)
        return
    await handle_slash_command(cog, inter, text)


@app_commands.command(
    name="dm_prompt",
    description="Get or set the AI persona prompt for DMs/user apps (admins only).",
)
@app_commands.describe(prompt="Optionally set a new DM prompt (leave blank to show current)")
@app_commands.checks.has_permissions(administrator=True)
async def dm_prompt_slash_command(inter: discord.Interaction, prompt: str = None):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return

    if not prompt:
        val = await cog.config.dm_prompt()
        if not val:
            val = DEFAULT_DM_PROMPT
        await inter.response.send_message(f"Current DM prompt:\n```{val}```", ephemeral=True)
        return

    await cog.config.dm_prompt.set(prompt)
    await inter.response.send_message(f"Set DM prompt to:\n```{prompt}```", ephemeral=True)


async def app_install(bot, cog):
    tree = cog.bot if hasattr(cog, "bot") else bot
    tree.tree.add_command(chat_slash_command)
    tree.tree.add_command(dm_prompt_slash_command)


try:
    from discord.app_commands import installs as app_installs

    for cmd in [chat_slash_command, dm_prompt_slash_command]:
        cmd.allowed_contexts = app_installs.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
        cmd.allowed_installs = app_installs.AppInstallationType(guild=True, user=True)
except Exception:
    pass
