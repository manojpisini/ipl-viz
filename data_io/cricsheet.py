import json
from pathlib import Path
from engine.events import BallEvent


def load_match(path: Path) -> dict:
    """Read a raw Cricsheet JSON file and hand back the dict as-is."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_ball_events(match_json: dict) -> list[BallEvent]:
    """
    Walk the Cricsheet innings→overs→deliveries tree and flatten it into a
    linear event stream.  This is the *rich* version — it also grabs fielder
    names and tracks legal-ball indices per over.
    """
    events = []

    info = match_json.get("info", {})
    teams = info.get("teams", [])

    for inn_idx, innings in enumerate(match_json.get("innings", [])):
        bat_team = innings.get("team")
        bowl_team = next((t for t in teams if t != bat_team), "Unknown")

        for over_data in innings.get("overs", []):
            over_no = over_data["over"]
            legal_idx = 0

            for delivery in over_data["deliveries"]:
                batter = delivery["batter"]
                bowler = delivery["bowler"]
                non_striker = delivery["non_striker"]

                r = delivery["runs"]
                bat_runs, extras_runs, total = r["batter"], r["extras"], r["total"]

                ex = delivery.get("extras", {})
                is_wide = "wides" in ex
                is_noball = "noballs" in ex
                is_bye = "byes" in ex
                is_legbye = "legbyes" in ex
                is_legal = not (is_wide or is_noball)

                # Wicket data — rarely more than one per delivery, but the
                # spec allows it (e.g. obstructing-the-field during a run-out)
                w_list = delivery.get("wickets", [])
                got_wicket = bool(w_list)
                dismissal_kind = None
                player_out = None
                fielders = []

                if got_wicket:
                    w = w_list[0]
                    dismissal_kind = w.get("kind")
                    player_out = w.get("player_out")
                    fielders = [f["name"] for f in w.get("fielders", [])]

                events.append(BallEvent(
                    match_id=info.get("event", {}).get("match_number"),
                    date=info.get("dates", [None])[0],
                    innings=inn_idx + 1,
                    batting_team=bat_team,
                    bowling_team=bowl_team,
                    over=over_no,
                    ball=legal_idx,
                    batter=batter,
                    bowler=bowler,
                    non_striker=non_striker,
                    runs_batter=bat_runs,
                    runs_extras=extras_runs,
                    runs_total=total,
                    is_legal=is_legal,
                    is_wide=is_wide,
                    is_noball=is_noball,
                    is_bye=is_bye,
                    is_legbye=is_legbye,
                    is_wicket=got_wicket,
                    dismissal_kind=dismissal_kind,
                    player_out=player_out,
                    fielders=fielders,
                ))

                if is_legal:
                    legal_idx += 1

    return events