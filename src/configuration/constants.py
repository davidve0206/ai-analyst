"""
Constants about the company and data provided, which can be used in the application.

This file is mean to be modified by the user to reflect their own company and data.
"""

from pydantic import BaseModel

financials_description = """Financial data of the company, including invoices, units and costs.
        
Some of the key columns include:
- ENTITY_CURRENCY: The currency in which the entity that made the sale operates.
- SALES_FUNCTIONAL_CURRENCY: Sales amount, per invoice, in the currency of the entity.
- GROSS_AMOUNT: The gross amount of the invoice, in EUR (the company's reporting currency).
- SoldToID: The ID of the customer who made the purchase.
"""


class LocalDataSource(BaseModel):
    name: str  # Include the extension in the name, e.g. "financials.csv"
    description: str


DATA_PROVIDED: list[LocalDataSource] = [
    LocalDataSource(
        name="financials_final.csv",
        description=financials_description,
    ),
]
