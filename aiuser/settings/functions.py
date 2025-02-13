
import discord
from redbot.core import checks, commands

from aiuser.abc import MixinMeta, aiuser
from aiuser.common.constants import (FUNCTION_CALLING_SUPPORTED_MODELS,
                                     OPENROUTER_URL)


class FunctionCallingSettings(MixinMeta):
    @aiuser.group()
    @checks.is_owner()
    async def functions(self, _):
        """ Settings to manage function calling

            (All subcommands are per server)
        """
        pass

    @functions.command(name="toggle")
    async def toggle_function_calling(self, ctx: commands.Context):
        """Toggle functions calling

        Requires a model that is whitelisted or supported for function calling
        If enabled, the LLM will call functions to generate responses when needed
        This will generate additional API calls and token usage!

        """

        current_value = not await self.config.guild(ctx.guild).function_calling()
        custom_endpoint = await self.config.custom_openai_endpoint()

        if current_value and (not custom_endpoint or custom_endpoint.startswith(OPENROUTER_URL)):
            model = await self.config.guild(ctx.guild).model()
            if model not in FUNCTION_CALLING_SUPPORTED_MODELS:
                return await ctx.send(f":warning: Currently selected model, `{model}` is not whitelisted for function calling. Set a compatible model first!")

        await self.config.guild(ctx.guild).function_calling.set(current_value)

        embed = discord.Embed(
            title="Functions Calling now set to:",
            description=f"{current_value}",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    @functions.command(name="location")
    async def set_location(self, ctx: commands.Context, latitude: float, longitude: float):
        """ Set the location where the bot will canonically be in

            Used for some functions.

            **Arguments**
            - `latitude` decimal latitude
            - `longitude` decimal longitude
        """
        await self.config.guild(ctx.guild).function_calling_default_location.set([latitude, longitude])
        embed = discord.Embed(
            title="Location now set to:",
            description=f"{latitude}, {longitude}",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    async def toggle_function_helper(self, ctx: commands.Context, tool_names: list, embed_title: str):
        enabled_tools: list = await self.config.guild(ctx.guild).function_calling_functions()

        if tool_names[0] not in enabled_tools:
            enabled_tools.extend(tool_names)
        else:
            for tool in tool_names:
                enabled_tools.remove(tool)

        await self.config.guild(ctx.guild).function_calling_functions.set(enabled_tools)

        embed = discord.Embed(
            title=f"{embed_title} function calling now set to:",
            description=f"{tool_names[0] in enabled_tools}",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    @commands.group(name="search")
    async def search_group(self, ctx: commands.Context):
        """Search function commands"""
        if ctx.invoked_subcommand is None:
            enabled_tools = await self.config.guild(ctx.guild).enabled_functions()
            from aiuser.functions.search.brave_call import BraveSearchToolCall, BraveSuggestToolCall
            from aiuser.functions.search.serper_call import SearchToolCall
            brave_key = (await self.bot.get_shared_api_tokens("brave_search")).get("api_key")
            serper_key = (await self.bot.get_shared_api_tokens("serper")).get("api_key")
            brave_status = "✅" if BraveSearchToolCall.function_name in enabled_tools else "❌"
            serper_status = "✅" if SearchToolCall.function_name in enabled_tools else "❌"
            brave_suggest_status = "✅" if BraveSuggestToolCall.function_name in enabled_tools else "❌"
            message = "Search Provider Status:\n"
            message += f"Brave Search: {brave_status} {'(No API key)' if not brave_key else ''}\n"
            message += f"Brave Suggest: {brave_suggest_status} {'(No API key)' if not brave_key else ''}\n"
            message += f"Serper: {serper_status} {'(No API key)' if not serper_key else ''}\n\n"
            message += f"Use `{ctx.clean_prefix}search brave` or `{ctx.clean_prefix}search serper` to toggle providers."
            await ctx.send(message)

    @search_group.command(name="brave")
    async def toggle_brave_search(self, ctx: commands.Context):
        """Enable/disable searching using Brave Search"""
        if not (await self.bot.get_shared_api_tokens("brave_search")).get("api_key"):
            return await ctx.send(
                f"Brave Search API key not set! Set it using `{ctx.clean_prefix}set api brave_search api_key,APIKEY`."
            )
        from aiuser.functions.search.brave_call import BraveSearchToolCall, BraveSuggestToolCall
        tool_names = [BraveSearchToolCall.function_name, BraveSuggestToolCall.function_name]
        await self.toggle_function_helper(ctx, tool_names, "Brave Search")

    @search_group.command(name="serper")
    async def toggle_serper_search(self, ctx: commands.Context):
        """Enable/disable searching using Serper.dev"""
        if not (await self.bot.get_shared_api_tokens("serper")).get("api_key"):
            return await ctx.send(
                f"Serper.dev key not set! Set it using `{ctx.clean_prefix}set api serper api_key,APIKEY`."
            )
        from aiuser.functions.search.serper_call import SearchToolCall
        tool_names = [SearchToolCall.function_name]
        await self.toggle_function_helper(ctx, tool_names, "Serper")


    @functions.command(name="scrape")
    async def toggle_scrape_function(self, ctx: commands.Context):
        """
        Enable/disable the functionality for the LLM to open URLs in messages

        (May not be called if the link generated an Discord embed)
        """
        from aiuser.functions.scrape.tool_call import ScrapeToolCall

        tool_names = [ScrapeToolCall.function_name]

        await self.toggle_function_helper(ctx, tool_names, "Scrape")

    @functions.command(name="weather")
    async def toggle_weather_function(self, ctx: commands.Context):
        """ Enable/disable a group of functions to getting weather using Open-Meteo

            See [Open-Meteo terms](https://open-meteo.com/en/terms) for their free API
        """
        from aiuser.functions.weather.tool_call import (
            IsDaytimeToolCall, LocalWeatherToolCall, LocationWeatherToolCall)

        tool_names = [IsDaytimeToolCall.function_name,
                      LocalWeatherToolCall.function_name, LocationWeatherToolCall.function_name]

        await self.toggle_function_helper(ctx, tool_names, "Weather")

    @functions.command(name="noresponse")
    async def toggle_ignore_function(self, ctx: commands.Context):
        """
        Enable/disable the functionality for the LLM to choose to not respond and ignore messages.

        Temperamental, may require additional prompting to work better.
        """
        from aiuser.functions.noresponse.tool_call import NoResponseToolCall

        tool_names = [NoResponseToolCall.function_name]

        await self.toggle_function_helper(ctx, tool_names, "No response")

    @functions.command(name="wolframalpha")
    async def toggle_wolfram_alpha_function(self, ctx: commands.Context):
        """ Enable/disable the functionality for the LLM to ask Wolfram Alpha about math, exchange rates, or the weather."""
        from aiuser.functions.wolframalpha.tool_call import WolframAlphaFunctionCall

        if (not (await self.bot.get_shared_api_tokens("wolfram_alpha")).get("app_id")):
            return await ctx.send(f"Wolfram Alpha app id not set! Set it using `{ctx.clean_prefix}set api wolfram_alpha app_id,APPID`.")

        tool_names = [WolframAlphaFunctionCall.function_name]

        await self.toggle_function_helper(ctx, tool_names, "Wolfram Alpha")
