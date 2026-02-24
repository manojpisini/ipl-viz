from engine.events import BallEvent


def parse_match_events(match_data):
    """
    Flatten Cricsheet's nested innings→overs→deliveries structure into a
    linear list of BallEvents.  This is the simpler parser used by main.py;
    see data_io.cricsheet.extract_ball_events for the richer version that
    also pulls fielder names.
    """
    events = []

    info = match_data.get("info", {})
    match_id = 1
    date = info.get("dates", ["Unknown"])[0]
    teams = info.get("teams", ["Team A", "Team B"])

    for inn_idx, inning in enumerate(match_data.get("innings", [])):
        bat_team = inning.get("team")
        bowl_team = teams[1] if teams[0] == bat_team else teams[0]

        for over_data in inning.get("overs", []):
            over_num = over_data.get("over")

            for ball_idx, delivery in enumerate(over_data.get("deliveries", [])):
                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {})

                is_wide = "wides" in extras
                is_noball = "noballs" in extras
                is_bye = "byes" in extras
                is_legbye = "legbyes" in extras
                is_legal = not (is_wide or is_noball)

                wickets = delivery.get("wickets", [])
                got_wicket = len(wickets) > 0
                kind = wickets[0].get("kind") if got_wicket else None
                out_batter = wickets[0].get("player_out") if got_wicket else None

                events.append(BallEvent(
                    match_id=match_id,
                    date=date,
                    innings=inn_idx + 1,
                    batting_team=bat_team,
                    bowling_team=bowl_team,
                    over=over_num,
                    ball=ball_idx,
                    batter=delivery.get("batter"),
                    bowler=delivery.get("bowler"),
                    non_striker=delivery.get("non_striker"),
                    runs_batter=runs.get("batter", 0),
                    runs_extras=runs.get("extras", 0),
                    runs_total=runs.get("total", 0),
                    is_legal=is_legal,
                    is_wide=is_wide,
                    is_noball=is_noball,
                    is_bye=is_bye,
                    is_legbye=is_legbye,
                    is_wicket=got_wicket,
                    dismissal_kind=kind,
                    player_out=out_batter,
                ))

    return events