from dataclasses import dataclass

@dataclass(frozen=True)
class Location:
    file: str | None
    pos: int
    row: int
    col: int
