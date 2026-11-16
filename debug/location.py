from dataclasses import dataclass

@dataclass(frozen=True)
class Location:
    filepath: str | None
    pos: int
    row: int
    col: int
