from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True, slots=True)
class BallEvent:
    """
    One delivery in a cricket match — everything that happened on a single ball.

    Frozen because events are historical facts. Once a ball is bowled, it never
    changes. Slotted because we hold thousands of these per match and the memory
    savings matter.
    """
    # Who's playing and when
    match_id: Optional[int]
    date: Optional[str]
    innings: int
    batting_team: str
    bowling_team: str

    # Where in the innings we are
    over: int
    ball: int               # 0-based legal delivery index within the over

    # The three people at the crease
    batter: str
    bowler: str
    non_striker: str

    # What the scoreboard says
    runs_batter: int
    runs_extras: int
    runs_total: int

    # Delivery classification — only one of wide/noball can be True
    is_legal: bool
    is_wide: bool
    is_noball: bool
    is_bye: bool
    is_legbye: bool

    # Dismissal
    is_wicket: bool
    dismissal_kind: Optional[str] = None
    player_out: Optional[str] = None
    fielders: List[str] = field(default_factory=list)