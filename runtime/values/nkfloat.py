from dataclasses import dataclass
from runtime.values.core import NkValue, NkId

@dataclass(frozen=True)
class NkFloat(NkValue):
    value: float
    members = {
        "__id__": NkId("1ce035b4-21e2-45ba-a1a6-13b9696f87de")
    }

