# response/response_handler.py
import logging
import discord
from redbot.core import commands
from typing import Optional, Any
from aiuser.messages_list.messages import create_messages_list, MessagesList
from aiuser.response.chat.response import create_chat_response
from aiuser.response.image.generator_factory import get_image_generator
from aiuser.response.image.response import create_image_response
from aiuser.response.is_image_request import is_image_request
from aiuser.types.abc import MixinMeta

logger = logging.getLogger("red.bz_cogs.aiuser")


async def dispatch_response(cog: MixinMeta, ctx: commands.Context, messages_list: Optional[Any] = None):
    """Decide which response to send based on the context"""
    async with ctx.typing():
        try:
            is_dm = isinstance(ctx.channel, discord.DMChannel)
            if messages_list is None:
                if is_dm:
                    messages_list = MessagesList(cog, ctx)
                    await messages_list._init()
                else:
                    messages_list = await create_messages_list(cog, ctx)

            if not messages_list and not is_dm and hasattr(ctx, "message") and await is_image_request(cog, ctx.message):
                if await process_image_response(cog, ctx):
                    return

            return await create_chat_response(cog, ctx, messages_list)

        except Exception as e:
            logger.exception("Error in dispatch_response")
            try:
                await ctx.send(f":warning: Error in generating response!\n{e}")
            except Exception:
                pass
            return None


async def process_image_response(cog: MixinMeta, ctx: commands.Context) -> bool:
    """Process and send an image response"""
    await ctx.react_quietly("🧐")
    try:
        generator = await get_image_generator(ctx, cog.config)
        success = await create_image_response(cog, ctx, generator)
        return success
    except Exception:
        return False
    finally:
        await ctx.message.remove_reaction("🧐", ctx.me)
