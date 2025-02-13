import logging
import aiohttp
from redbot.core import commands
from trafilatura import extract
from aiuser.common.utilities import contains_youtube_link
logger = logging.getLogger("red.bz_cogs.aiuser")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
BRAVE_SUGGEST_ENDPOINT = "https://api.search.brave.com/res/v1/suggest/search"

async def search_brave(query: str, api_key: str, ctx: commands.Context):
    return await BraveQuery(query, api_key, ctx).execute_search()

async def suggest_brave(query: str, api_key: str, ctx: commands.Context):
    return await BraveQuery(query, api_key, ctx).execute_suggest()

class BraveQuery:
    def __init__(self, query: str, api_key: str, ctx: commands.Context):
        self.api_key = api_key
        self.query = query
        self.guild = ctx.guild.name

    async def execute_search(self):
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
        }
        params = {'q': self.query}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(BRAVE_ENDPOINT, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return await self.process_search_results(data)
        except Exception:
            logger.exception("Failed request to Brave Search API")
            return "An error occurred while searching Brave."

    async def execute_suggest(self):
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': self.api_key
        }
        params = {
            'q': self.query,
            'country': 'US',
            'count': '5'
        }
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(BRAVE_SUGGEST_ENDPOINT, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return self.process_suggest_results(data)
        except Exception:
            logger.exception("Failed request to Brave Suggest API")
            return "An error occurred while getting suggestions from Brave."

    async def process_search_results(self, data: dict):
        if "featured_snippet" in data:
            snippet = data["featured_snippet"].get("description")
            if snippet:
                return f"Use the following relevant information to generate your response: {snippet}"
        web_results = data.get("web", {}).get("results", [])
        filtered_results = [result for result in web_results
                          if not contains_youtube_link(result.get("url", ""))]
        if not filtered_results:
            return "No relevant information was found using Brave search."
        first_result = filtered_results[0]
        url = first_result.get("url")
        try:
            text_content = await self.scrape_page(url)
            return f"Use the following relevant information to generate your response: {text_content}"
        except Exception:
            logger.debug(f"Failed scraping URL {url}", exc_info=True)
            return f"Use the following relevant information to generate your response: {first_result.get('title', '')} - {first_result.get('description', '')}"

    def process_suggest_results(self, data: dict):
        suggestions = data.get('suggestions', [])
        if not suggestions:
            return "No suggestions found."
        suggestion_list = [sugg.get('value', '') for sugg in suggestions if sugg.get('value')]
        return '\n'.join(suggestion_list)

    async def scrape_page(self, url: str):
        headers = {
            "Cache-Control": "no-cache",
            "Referer": "https://search.brave.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        logger.info(f"Requesting {url} from Brave query \"{self.query}\" in {self.guild}")
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                text_content = extract(html_content)
                if len(text_content) > 5000:
                    text_content = text_content[:5000] + "..."
                return text_content
