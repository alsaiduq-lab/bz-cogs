from aiuser.functions.search.brave_query import search_brave, suggest_brave
from aiuser.functions.tool_call import ToolCall
from aiuser.functions.types import (Function, Parameters,
                                  ToolCallSchema)

class BraveSearchToolCall(ToolCall):
    schema = ToolCallSchema(function=Function(
        name="search_brave",
        description="Searches Brave using the query for any unknown information or most current information",
        parameters=Parameters(
            properties={
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            required=["query"]
        )))
    function_name = schema.function.name
    async def _handle(self, arguments):
        api_tokens = await self.bot.get_shared_api_tokens("brave_search")
        api_key = api_tokens.get("api_key")
        if not api_key:
            return "No Brave Search API key configured."

        return await search_brave(arguments["query"], api_key, self.ctx)

class BraveSuggestToolCall(ToolCall):
    schema = ToolCallSchema(function=Function(
        name="suggest_brave",
        description="Gets search suggestions from Brave for a given query",
        parameters=Parameters(
            properties={
                "query": {
                    "type": "string",
                    "description": "The query to get suggestions for",
                }
            },
            required=["query"]
        )))
    function_name = schema.function.name
    async def _handle(self, arguments):
        api_tokens = await self.bot.get_shared_api_tokens("brave_search")
        api_key = api_tokens.get("api_key")
        if not api_key:
            return "No Brave Search API key configured."

        return await suggest_brave(arguments["query"], api_key, self.ctx)
