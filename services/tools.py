from typing import Literal

from pydantic_ai import RunContext

from utils.http_utils import execute_tool
from llm_service.models.model import skyblock_agent
from llm_service.models.wiki_searcher_agent import get_relevant_pages


def load():
    print("Getting ready...")


@skyblock_agent.tool(strict=True)
async def search_skyblock_wiki(ctx: RunContext[None], query: str):
    """
    The official source of truth for ALL Hypixel Skyblock information.

    CRITICAL: Hypixel Skyblock is complex and changes frequently.
    Do NOT rely on your internal training data. You MUST use this tool
    to answer any question related to items, mechanics, stats, mayors,
    locations, or anything related to the game.

    """
    results = await execute_tool("search_skyblock_wiki", query=query)
    response, usage = await get_relevant_pages(query, results)
    if usage: ctx.usage.incr(usage)
    return response


@skyblock_agent.tool(strict=True)
async def get_player_status(ctx: RunContext[None], player_name: str = None):
    """
    Returns player's rank, online status, last active time, location, and the list of SkyBlock profiles including the selected one.
    Use this tool for account identity and status checks.
    """
    return await execute_tool("get_player_status", player_name=player_name or ctx.deps["player"])


@skyblock_agent.tool(strict=True)
async def get_profile_overview(ctx: RunContext[None], player_name: str = None, profile_name: str = None):
    """
    Returns a SkyBlock profile overview: profile gamemode, skyblock level, purse & bank, active pet, magical power & selected power stone, skills, and average skill level.
    """
    return await execute_tool(
        "get_profile_overview",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name
    )


@skyblock_agent.tool(strict=True)
async def get_profile_networth(ctx: RunContext[None], player_name: str = None, profile_name: str = None):
    """
    Returns detailed networth of a SkyBlock profile: value per category (inventory, armor, storage, etc.) and total estimated value.
    """
    return await execute_tool(
        "get_profile_networth",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name
    )


@skyblock_agent.tool(strict=True)
async def get_profile_section(
    ctx: RunContext[None],
    category: Literal["mining", "garden", "foraging", "fishing", "slayers", "dungeons", "misc"],
    player_name: str = None,
    profile_name: str = None
):
    """
    Returns detailed information about a specific category of a SkyBlock profile (mining, garden, foraging, fishing, slayers, dungeons, misc).
    Provides relevant stats, gear, and progression data for the selected category.
    """
    return await execute_tool(
        "get_profile_section",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name,
        category=category
    )


@skyblock_agent.tool_plain(strict=True)
async def get_skyblock_events():
    """
    Returns current SkyBlock events, including SkyBlock date, mayor and minister, ongoing elections, upcoming special mayor elections, and Jacob's contest dates.
    """
    return await execute_tool("get_skyblock_events")


@skyblock_agent.tool(strict=True)
async def get_inventory_contents(ctx: RunContext[None], player_name: str = None, profile_name: str = None):
    """
    Returns a SkyBlock profile's equipped armor, equipments, and inventory contents.
    """
    return await execute_tool(
        "get_inventory_contents",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name
    )


@skyblock_agent.tool(strict=True)
async def search_storage(
        ctx: RunContext[None],
        item_name: str,
        player_name: str = None,
        profile_name: str = None,
        is_pet: bool = False,
        include_prices: bool = False
):
    """
    Searches a player's storage and sacks for an item or pet, returning its details.
    Includes value breakdown if include_prices is True.
    """
    return await execute_tool(
        "search_storage",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name,
        name=item_name,
        is_pet=is_pet,
        include_prices=include_prices
    )


@skyblock_agent.tool(strict=True)
async def get_accessory_upgrades(
    ctx: RunContext[None],
    player_name: str = None,
    profile_name: str = None,
    page: int = 0,
    soulbound: bool = False
):
    """
    Returns a paginated list of a player's missing accessories, sorted by coins per magical power (MP).
    If soulbound is True, only returns items that cannot be bought.
    Page starts at 0 by default.
    """
    return await execute_tool(
        "get_accessory_upgrades",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name,
        page=page,
        soulbound=soulbound
    )


@skyblock_agent.tool(strict=True)
async def get_museum_donations(
    ctx: RunContext[None],
    player_name: str = None,
    profile_name: str = None,
    page: int = 0,
    soulbound: bool = False
):
    """
    Returns a paginated list of missing museum donations, sorted by coins per XP.
    If soulbound is True, only returns items that cannot be bought. Page starts at 0 by default.
    """
    return await execute_tool(
        "get_museum_donations",
        player_name=player_name or ctx.deps["player"],
        profile_name=profile_name,
        page=page,
        soulbound=soulbound
    )


@skyblock_agent.tool_plain(strict=True)
async def get_item_price(item_name: str):
    """
    Returns the buy and sell prices of an item in the Bazaar or its lowest BIN in the Auction House, depending on where it can be sold.
    """
    return await execute_tool("get_item_price", item_name=item_name)