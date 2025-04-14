import json
import logging
import aiohttp
from redbot.core import commands
from trafilatura import extract
from aiuser.common.utilities import contains_youtube_link

logger = logging.getLogger("red.bz_cogs.aiuser")

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
SERPER_ENDPOINT = "https://google.serper.dev/search"

async def search_google(query: str, api_key: str, ctx: commands.Context):
    return await SearchQuery(query, api_key, ctx).execute_search()

class SearchQuery:
    def __init__(self, query: str, api_key: str, ctx: commands.Context):
        self.api_key = api_key
        self.query = query
        self.guild = ctx.guild.name

    async def execute_search(self):
        result = await self.gpt_4o_search()
        if result is not None:
            return result
        return await self.execute_serper_search()

    async def gpt_4o_search(self):
        payload = json.dumps({
            "model": "gpt-4o-search-preview",
            "web_search_options": {
                "search_context_size": "medium"
            },
            "messages": [{
                "role": "user",
                "content": self.query
            }]
        })
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(OPENAI_ENDPOINT, data=payload) as response:
                    if response.status == 401 or response.status == 403:
                        logger.debug("No access to gpt-4o-search-preview, falling back to Serper")
                        return None
                    response.raise_for_status()
                    data = await response.json()
                    return await self.process_gpt_4o_results(data)

        except Exception as e:
            logger.debug(f"Failed gpt-4o-search-preview request: {str(e)}", exc_info=True)
            return None

    async def process_gpt_4o_results(self, data: dict):
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        annotations = message.get("annotations", [])

        if content:
            return f"Use the following relevant information to generate your response: {content}"

        valid_urls = [
            ann["url_citation"]["url"]
            for ann in annotations
            if ann.get("type") == "url_citation" and not contains_youtube_link(ann["url_citation"]["url"])
        ]

        if not valid_urls:
            return "No relevant information was found using gpt-4o-search."

        link = valid_urls[0]
        try:
            text_content = await self.scrape_page(link)
            return f"Use the following relevant information to generate your response: {text_content}"

        except Exception:
            logger.debug(f"Failed scraping URL {link}", exc_info=True)
            return f"Use the following relevant information to generate your response: {content or 'No additional details available.'}"

    async def execute_serper_search(self):
        payload = json.dumps({"q": self.query})
        headers = {'X-API-KEY': self.api_key, 'Content-Type': 'application/json'}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(SERPER_ENDPOINT, data=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return await self.process_serper_results(data)

        except Exception:
            logger.exception("Failed request to serper.io")
            return "An error occurred while searching Google."

    async def process_serper_results(self, data: dict):
        answer_box = data.get("answerBox")
        if answer_box and "snippet" in answer_box:
            return f"Use the following relevant information to generate your response: {answer_box['snippet']}"

        organic_results = [result for result in data.get(
            "organic", []) if not contains_youtube_link(result.get("link", ""))]
        if not organic_results:
            return "No relevant information was found using a Google search."

        first_result = organic_results[0]
        link = first_result.get("link")

        try:
            text_content = await self.scrape_page(link)
            return f"Use the following relevant information to generate your response: {text_content}"

        except Exception:
            logger.debug(f"Failed scraping URL {link}", exc_info=True)
            knowledge_graph = data.get("knowledgeGraph", {})
            return f"Use the following relevant information to generate your response: {self.format_knowledge_graph(knowledge_graph) if knowledge_graph else first_result.get('snippet')}"

    async def scrape_page(self, link: str):
        headers = {
            "Cache-Control": "no-cache",
            "Referer": "https://www.google.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        logger.info(f"Requesting {link} from query \"{self.query}\" in {self.guild}")
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(link) as response:
                response.raise_for_status()
                html_content = await response.text()
                text_content = extract(html_content)

                if len(text_content) > 5000:
                    text_content = text_content[:5000] + "..."

                return text_content

    def format_knowledge_graph(self, knowledge_graph: dict) -> str:
        title = knowledge_graph.get("title", "")
        type = knowledge_graph.get("type", "")
        description = knowledge_graph.get("description", "")
        text_content = f"{title} - ({type}) \n {description}"

        attributes = knowledge_graph.get("attributes", {})
        for attribute, value in attributes.items():
            text_content += f" \n {attribute}: {value}"

        return text_content
