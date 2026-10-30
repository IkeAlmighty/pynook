from dataclasses import dataclass
from runtime.values.core import NkValue, NkId

@dataclass(frozen=True)
class NkString(NkValue):
    value: str
    members = {
        "__id__": NkId("4693a742-bf91-49a8-9301-93900432a18e")
    }

