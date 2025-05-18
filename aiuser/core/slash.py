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


async def app_install(bot, cog):
    (cog.bot if hasattr(cog, "bot") else bot).tree.add_command(chat_slash_command)
