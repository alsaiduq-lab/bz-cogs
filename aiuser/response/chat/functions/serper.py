import json
import logging

import aiohttp
import discord
from bs4 import BeautifulSoup

from aiuser.common.utilities import contains_youtube_link

logger = logging.getLogger("red.bz_cogs.aiuser")
GOOGLE_SEARCH_ENDPOINT = "https://google.serper.dev/search"


async def search_google(query: str, api_key: str, guild: discord.Guild = None):
    if not api_key:
        raise ValueError("No API key provided for serper.io")

    payload = json.dumps({"q": query})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

    logger.info(f"Searching Google for \"{query}\" in {guild.name}")

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(GOOGLE_SEARCH_ENDPOINT, data=payload) as response:
                response.raise_for_status()

                data = await response.json()
                return await process_search_results(data)

    except:
        logger.exception("Failed request to serper.io")
        return "An error occurred during the search."


async def process_search_results(data: dict):
    answer_box = data.get("answerBox")
    if answer_box and "snippet" in answer_box:
        return f"Use the following relevant information to generate your response: {answer_box['snippet']}"

    organic_results = [result for result in data.get(
        "organic", []) if not contains_youtube_link(result.get("link", ""))]
    if not organic_results:
        return "No relevant information found on Google"

    first_result = organic_results[0]
    link = first_result.get("link")

    try:
        text_content = await scrape_page(link)
        return f"Use the following relevant information to generate your response: {text_content}"

    except:
        logger.debug(f"Failed scraping URL {link}", exc_info=True)
        knowledge_graph = data.get("knowledgeGraph", {})
        return f"Use the following relevant information to generate your response: {format_knowledge_graph(knowledge_graph) if knowledge_graph else first_result.get('snippet')}"


async def scrape_page(link: str):
    headers = {
        "Cache-Control": "no-cache",
        "Referer": "https://www.google.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    logger.debug(f"Requesting {link} to scrape")
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(link) as response:
            response.raise_for_status()
            html_content = await response.text()
            text_content = find_best_text(html_content)

            if len(text_content) > 2000:
                text_content = text_content[:2000]

            return text_content


def find_best_text(html_content: str):
    def get_text_content(tag):
        return tag.get_text(separator=" ", strip=True) if tag else ""

    soup = BeautifulSoup(html_content, 'html.parser')
    paragraph_tags = soup.find_all('p') or []

    paragraph_text = ""
    for tag in paragraph_tags:
        tag_content = get_text_content(tag)
        paragraph_text = paragraph_text + tag_content if len(tag_content) > 100 else paragraph_text

    if not paragraph_text or len(paragraph_text) < 300:
        return soup.get_text(separator=" ", strip=True)

    return paragraph_text


def format_knowledge_graph(knowledge_graph: dict) -> str:
    title = knowledge_graph.get("title", "")
    type = knowledge_graph.get("type", "")
    description = knowledge_graph.get("description", "")
    text_content = f"{title} - ({type}) \n {description}"

    attributes = knowledge_graph.get("attributes", {})
    for attribute, value in attributes.items():
        text_content += f" \n {attribute}: {value}"

    return text_content
