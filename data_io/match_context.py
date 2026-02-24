import json
import logging
from functools import lru_cache
from data.stadium_lookup import STADIUMS_BY_VENUE, Stadium
from engine.weather import get_match_weather

log = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    """Lowercase alphanumeric — good enough for fuzzy venue matching."""
    return "".join(c.lower() for c in text if c.isalnum() or c.isspace())


@lru_cache(maxsize=32)
def resolve_stadium(venue_name: str) -> Stadium:
    """
    Try to match a Cricsheet venue string to one of our known stadiums.

    Order: exact key → substring match → fallback with dummy coordinates.
    The lru_cache means we only pay the fuzzy-match cost once per venue.
    """
    # Exact hit — covers most cases
    if venue_name in STADIUMS_BY_VENUE:
        return STADIUMS_BY_VENUE[venue_name]

    # Some Cricsheet files use slightly different names for the same ground
    norm = _normalize(venue_name)
    for stadium in STADIUMS_BY_VENUE.values():
        s_norm = _normalize(stadium.name)
        if norm in s_norm or s_norm in norm:
            log.debug("Fuzzy matched '%s' → '%s'", venue_name, stadium.name)
            return stadium

    log.warning("No stadium match for '%s' — using generic dimensions", venue_name)
    return Stadium(
        name=f"{venue_name} (Unknown)",
        location="Unknown",
        width_m=140.0, length_m=145.0,
        straight_boundary_m=72.0, square_boundary_m=68.0,
        lat=0.0, lon=0.0,
    )


def extract_game_details(match_data: dict, stadium: Stadium) -> dict:
    """Pull match metadata + weather into a single dict for the UI panels."""
    info = match_data.get("info", {})
    innings = match_data.get("innings", [])

    match_date = info.get("dates", ["2008-01-01"])[0]

    weather = get_match_weather(stadium.lat, stadium.lon, match_date) or {
        "air_temp": None, "humidity": None, "wind": None,
        "rain": None, "summary": "Unavailable", "source": "N/A",
    }

    # Grab the first powerplay block we can find
    powerplay = None
    for inning in innings:
        pps = inning.get("powerplays", [])
        if pps:
            powerplay = pps[0]
            break

    target = None
    if innings and "target" in innings[-1]:
        target = innings[-1].get("target")

    return {
        "date": match_date,
        "city": info.get("city", "Unknown City"),
        "venue": info.get("venue"),
        "match_type": info.get("match_type"),
        "toss_winner": info.get("toss", {}).get("winner"),
        "toss_decision": info.get("toss", {}).get("decision"),
        "winner": info.get("outcome", {}).get("winner"),
        "result_by": info.get("outcome", {}).get("by", {}),
        "player_of_match": info.get("player_of_match", []),
        "overs": info.get("overs", 20),
        "target": target,
        "powerplay": powerplay,
        "weather": weather,
    }


def load_match_and_stadium(file_path: str):
    """
    One-shot loader: reads the JSON, resolves the stadium, and hydrates
    the game-details dict (including weather).  Returns a triple.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            match_data = json.load(f)
    except Exception as exc:
        log.error("Failed to load match file: %s", exc)
        return None, None, None

    venue = match_data.get("info", {}).get("venue", "Unknown Venue")
    stadium = resolve_stadium(venue)
    details = extract_game_details(match_data, stadium)

    return match_data, stadium, details