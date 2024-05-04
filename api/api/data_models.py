from pydantic import BaseModel
from typing import Optional


class ClothingItemInput(BaseModel):
    ProductId: Optional[str]
    MaterialId_1: Optional[str]
    MaterialId_2: Optional[str]
    MaterialId_1_share: Optional[float]
    MaterialId_2_share: Optional[float]
    CountryDyeingCode: Optional[str]
    CountryFabricCode: Optional[str]
    CountryMakingCode: Optional[str]
    FabricProcess: Optional[str]
    Mass: Optional[float]
    AirTransportRatio: Optional[float]
