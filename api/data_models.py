from pydantic import BaseModel
from typing import Optional, List

# Define the data model for products
class Material(BaseModel):
    id: str
    share: float
    country: Optional[str] = None

class Product(BaseModel):
    mass: float
    materials: List[Material]
    product: str
    countrySpinning: str
    countryFabric: str
    countryDyeing: str
    countryMaking: str
    fabricProcess: str

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
