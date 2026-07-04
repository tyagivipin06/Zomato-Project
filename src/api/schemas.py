from pydantic import BaseModel
from typing import List

class LocationsResponse(BaseModel):
    locations: List[str]

class CuisinesResponse(BaseModel):
    cuisines: List[str]
