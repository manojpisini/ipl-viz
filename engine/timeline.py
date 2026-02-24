from typing import List, Optional
from engine.events import BallEvent


class Timeline:
    """
    Drives ball-by-ball playback.  Accumulates real-time delta and fires
    one event whenever enough time has elapsed at the current speed setting.

    Speed is in "events per second" — 1.0 means one ball/second, 4.0 means
    four balls/second.  Seeking resets the accumulator so you don't get a
    stale partial-tick after jumping.
    """

    def __init__(self, events: List[BallEvent]):
        self.events = events
        self.index = 0
        self.playing = False
        self.speed = 1.0
        self.accumulator = 0.0
        self.total_events = len(events)

    def update(self, dt: float) -> Optional[BallEvent]:
        if not self.playing or self.index >= self.total_events:
            return None

        self.accumulator += dt * self.speed

        # One ball fires when we cross the 1-second threshold
        if self.accumulator >= 1.0:
            self.accumulator = 0.0
            ev = self.events[self.index]
            self.index += 1
            return ev

        return None

    def seek(self, index: int):
        self.index = max(0, min(index, self.total_events))
        self.accumulator = 0.0

    def toggle_play(self):
        self.playing = not self.playing

    def set_speed(self, speed: float):
        self.speed = max(0.1, min(speed, 50.0))

    @property
    def progress(self) -> float:
        if self.total_events == 0:
            return 0.0
        return self.index / self.total_events