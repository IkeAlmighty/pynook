from dataclasses import dataclass
from runtime.values.core import NkValue, NkId

@dataclass(frozen=True)
class NkInt(NkValue): 
    value: int
    members = {
        "__id__": NkId("882b5545-cb21-4875-94ac-134ab8e055e5")
    }

