import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from engine.paths import get_resource_path

log = logging.getLogger(__name__)

IPL_JSON_DIR = get_resource_path("data/ipl_json")
CACHE_FILENAME = ".index.json"

logging.basicConfig(level=logging.WARNING)


def list_seasons() -> List[str]:
    """Scan the data directory for year-named folders (e.g. '2008', '2024')."""
    if not IPL_JSON_DIR.exists():
        log.warning("Data directory missing: %s", IPL_JSON_DIR)
        return []
    return sorted(p.name for p in IPL_JSON_DIR.iterdir() if p.is_dir() and p.name.isdigit())


def list_matches_for_season(season: str, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Return match metadata for every file in a season folder.

    First run is slow — it parses every JSON to pull out match info.  After
    that we stash a .index.json cache so subsequent launches skip the parse.
    The cache is invalidated whenever the folder's mtime is newer (i.e. you
    dropped in new match files).
    """
    season_dir = IPL_JSON_DIR / season
    if not season_dir.exists():
        return []

    cache_path = season_dir / CACHE_FILENAME

    # Fast path: if the cache is still fresh, use it
    if use_cache and _cache_is_fresh(season_dir, cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            log.warning("Corrupt cache for season %s — rebuilding", season)

    # Slow path: parse every JSON in the folder
    json_files = [f for f in season_dir.glob("*.json") if f.name != CACHE_FILENAME]
    matches = [m for f in json_files if (m := _parse_match_meta(f))]
    matches.sort(key=lambda m: (m.get("date", ""), m.get("match_number", 999)))

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(matches, f)
    except OSError as exc:
        log.warning("Couldn't write season cache: %s", exc)

    return matches


# ---------------------------------------------------------------------------

def _cache_is_fresh(season_dir: Path, cache_path: Path) -> bool:
    if not cache_path.exists():
        return False
    # If someone added new match files the dir mtime will bump
    return season_dir.stat().st_mtime < cache_path.stat().st_mtime


def _parse_match_meta(file_path: Path) -> Optional[Dict[str, Any]]:
    """Pull just the metadata we need for the match-selection list."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        info = data.get("info", {})
        event = info.get("event", {})

        dates = info.get("dates", [])
        date_str = dates[0] if dates else "Unknown Date"
        teams = " vs ".join(info.get("teams", ["Unknown", "Unknown"]))
        venue = info.get("venue", "Unknown Venue")
        match_num = event.get("match_number")
        stage = event.get("stage", "League")

        label = f"Match {match_num} – {stage}" if match_num else f"{stage} Match"

        return {
            "file": str(file_path),
            "filename": file_path.name,
            "label": label,
            "teams": teams,
            "date": date_str,
            "venue": venue,
            "stage": stage,
            "match_number": match_num if isinstance(match_num, int) else 999,
        }
    except Exception as exc:
        log.debug("Skipping %s: %s", file_path.name, exc)
        return None