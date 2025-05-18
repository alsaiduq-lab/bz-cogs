try:
    from discord.app_commands import installs as app_installs
except ImportError:
    app_installs = None


import discord
from redbot.core import app_commands
from aiuser.core.handlers import handle_slash_command


@app_commands.command(name="chat", description="Talk directly to this bot's AI. Ask it anything you want!")
@app_commands.describe(text="The prompt you want to send to the AI.")
@app_commands.checks.cooldown(1, 30)
@app_commands.checks.cooldown(1, 5, key=None)
async def chat_slash_command(inter: discord.Interaction, text: str):
    if not (1 <= len(text) <= 2000):
        await inter.response.send_message("Text must be between 1 and 2000 characters.", ephemeral=True)
        return
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return
    await handle_slash_command(cog, inter, text)


@app_commands.context_menu(name="Chat with AI")
@app_commands.checks.cooldown(1, 30)
@app_commands.checks.cooldown(1, 5, key=None)
async def chat_user_app(inter: discord.Interaction, message: discord.Message):
    cog = inter.client.get_cog("AIUser")
    if not cog:
        await inter.response.send_message("Cog not loaded!", ephemeral=True)
        return
    text = message.content or ""
    if not (1 <= len(text) <= 2000):
        await inter.response.send_message("Message must be between 1 and 2000 characters.", ephemeral=True)
        return
    await handle_slash_command(cog, inter, text)


async def app_install(bot, cog):
    (cog.bot if hasattr(cog, "bot") else bot).tree.add_command(chat_slash_command)
    (cog.bot if hasattr(cog, "bot") else bot).tree.add_command(chat_user_app)

    if app_installs is not None:
        try:
            for cmd in [chat_slash_command, chat_user_app]:
                cmd.allowed_contexts = app_installs.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
                cmd.allowed_installs = app_installs.AppInstallationType(guild=True, user=True)
        except Exception as exc:
            import logging

            logging.getLogger("red.aiuser").exception(
                "Failed to set allowed_contexts/installs for aiuser commands", exc_info=exc
            )
