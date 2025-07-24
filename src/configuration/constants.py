"""
Constants about the company and data provided, which can be used in the application.

This file is mean to be modified by the user to reflect their own company and data.
"""

from pathlib import Path
from pydantic import BaseModel

from src.configuration.settings import DATA_DIR

financials_description = """Detailed per-invoice data of the company.
        
Some of the key columns include:
- ENTITY_CURRENCY: The currency in which the entity that made the sale operates.
- CURRENCY: The currency in which the invoice is issued.
- SOLD_TO_CITY: The city of the customer who made the purchase, ALL IN CAPS (ex. "LJUNGBY").
- SOLD_TO_COUNTRY: The country of the customer who made the purchase, ALL IN CAPS (ex. "GERMANY").
- INVOICE_MONTH: The month in which the invoice was issued, with values 1-12.
- INVOICE_YEAR: The year in which the invoice was issued.
- SALES_FUNCTIONAL_CURRENCY: Net sales amount, per invoice, in the currency of the entity (ENTITY_CURRENCY).
- GROSS_AMOUNT: The gross amount of the invoice, in the company's reporting currency - EUR.
- DISCOUNT_AMOUNT: Discount amount applied to the invoice, in the company's reporting currency - EUR.
- SoldToID: The ID of the customer who made the purchase.

To load to dataframe, use encoding="ISO-8859-1"
"""


class LocalDataSource(BaseModel):
    name: str  # Include the extension in the name, e.g. "financials.csv"
    description: str
    location: Path = DATA_DIR

    @property
    def path(self) -> Path:
        """Returns the path to the data source."""
        return self.location / self.name


INTERNAL_DATA = LocalDataSource(
    name="financials_final.csv",
    description=financials_description,
)
