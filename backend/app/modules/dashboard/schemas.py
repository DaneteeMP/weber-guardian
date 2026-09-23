"""Dashboard contracts (Pydantic). Counts only, scoped like everything else."""
from pydantic import BaseModel


class CountryCount(BaseModel):
    country: str
    count: int


class DashboardStats(BaseModel):
    total_customers: int
    total_equipment: int
    total_offers: int
    total_offer_lines: int
    countries: list[CountryCount]
