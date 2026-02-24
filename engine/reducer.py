from engine.state import MatchState, PlayerStats, BowlerStats
from engine.events import BallEvent


def apply_ball(state: MatchState, event: BallEvent) -> MatchState:
    """
    Pure reducer: (old state + ball event) → new state.  Never mutates —
    always returns a fresh MatchState so we can seek to any ball cheaply.
    """
    new_balls = state.legal_balls + (1 if event.is_legal else 0)
    new_score = state.score + event.runs_total
    new_wkts = state.wickets + (1 if event.is_wicket else 0)

    # --- batter stats ---
    b = state.batter_stats.copy()
    prev = b.get(event.batter, PlayerStats())
    b[event.batter] = PlayerStats(
        runs=prev.runs + event.runs_batter,
        balls=prev.balls + (0 if event.is_wide else 1),  # wides don't count
        fours=prev.fours + (1 if event.runs_batter == 4 else 0),
        sixes=prev.sixes + (1 if event.runs_batter == 6 else 0),
    )
    if event.non_striker not in b:
        b[event.non_striker] = PlayerStats()

    # --- bowler stats ---
    # Byes/legbyes aren't charged to the bowler, but wides/noballs are.
    bl = state.bowler_stats.copy()
    prev_bl = bl.get(event.bowler, BowlerStats())
    cost = event.runs_total - (event.runs_extras if (event.is_bye or event.is_legbye) else 0)
    # Run-outs aren't the bowler's wicket
    credited_wkt = 1 if (event.is_wicket and event.dismissal_kind != "run out") else 0
    bl[event.bowler] = BowlerStats(
        balls=prev_bl.balls + (1 if event.is_legal else 0),
        runs_conceded=prev_bl.runs_conceded + cost,
        wickets=prev_bl.wickets + credited_wkt,
    )

    # Did the innings just end?
    all_out = new_wkts >= 10
    overs_done = new_balls >= (state.overs_limit * 6)
    chased = state.target is not None and new_score >= state.target

    return MatchState(
        score=new_score,
        wickets=new_wkts,
        legal_balls=new_balls,
        batting_team=event.batting_team,
        bowling_team=event.bowling_team,
        current_batter=event.batter,
        current_non_striker=event.non_striker,
        current_bowler=event.bowler,
        batter_stats=b,
        bowler_stats=bl,
        overs_limit=state.overs_limit,
        target=state.target,
        extras_total=state.extras_total + event.runs_extras,
        wides=state.wides + (1 if event.is_wide else 0),
        noballs=state.noballs + (1 if event.is_noball else 0),
        byes=state.byes + (1 if event.is_bye else 0),
        legbyes=state.legbyes + (1 if event.is_legbye else 0),
        is_innings_complete=state.is_innings_complete or all_out or overs_done or chased,
    )