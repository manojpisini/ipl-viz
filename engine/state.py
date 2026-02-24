from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass(frozen=True, slots=True)
class PlayerStats:
    """Batter's running totals for a single innings."""
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0


@dataclass(frozen=True, slots=True)
class BowlerStats:
    """Bowler's running figures for a single innings."""
    balls: int = 0
    runs_conceded: int = 0
    wickets: int = 0


@dataclass(frozen=True, slots=True)
class MatchState:
    """
    Complete snapshot of a match innings at a specific point in time.

    Every field is immutable — the reducer creates a fresh instance on each
    delivery instead of mutating in-place. This makes seek/replay trivial:
    just replay events from the start to any target ball.
    """
    score: int = 0
    wickets: int = 0
    legal_balls: int = 0

    batting_team: str = "BAT"
    bowling_team: str = "BOWL"

    current_batter: str = ""
    current_non_striker: str = ""
    current_bowler: str = ""

    # Per-player breakdowns — shallow-copied on each transition
    batter_stats: Dict[str, PlayerStats] = field(default_factory=dict)
    bowler_stats: Dict[str, BowlerStats] = field(default_factory=dict)

    overs_limit: int = 20
    target: Optional[int] = None

    extras_total: int = 0
    wides: int = 0
    noballs: int = 0
    byes: int = 0
    legbyes: int = 0

    is_innings_complete: bool = False

    @property
    def overs_str(self) -> str:
        return f"{self.legal_balls // 6}.{self.legal_balls % 6}"

    @property
    def run_rate(self) -> float:
        if self.legal_balls == 0:
            return 0.0
        return round(self.score / (self.legal_balls / 6), 2)

    @property
    def req_run_rate(self) -> Optional[float]:
        if self.target is None:
            return None
        rem_runs = self.target - self.score
        rem_balls = (self.overs_limit * 6) - self.legal_balls
        if rem_balls <= 0:
            return 0.0
        return round((rem_runs / rem_balls) * 6, 2)

    @property
    def total_fours(self) -> int:
        return sum(p.fours for p in self.batter_stats.values())

    @property
    def total_sixes(self) -> int:
        return sum(p.sixes for p in self.batter_stats.values())