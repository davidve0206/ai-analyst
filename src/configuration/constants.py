"""
Constants about the company and data provided, which can be used in the application.

This file is mean to be modified by the user to reflect their own company and data.
"""

from pydantic import BaseModel

financials_description = """Financial data of the company, including invoices, units and costs.
        
Some of the key columns include:
- ENTITY_CURRENCY: The currency in which the entity that made the sale operates.
- CURRENCY: The currency in which the invoice is issued.
- SOLD_TO_CITY: The city of the customer who made the purchase.
- SOLD_TO_COUNTRY: The country of the customer who made the purchase.
- INVOICE_MONTH: The month in which the invoice was issued.
- INVOICE_YEAR: The year in which the invoice was issued.
- SALES_FUNCTIONAL_CURRENCY: Sales amount, per invoice, in the currency of the entity.
- GROSS_AMOUNT: The gross amount of the invoice, in EUR (the company's reporting currency).
- SoldToID: The ID of the customer who made the purchase.

To load to dataframe, use encoding="ISO-8859-1"
"""


class LocalDataSource(BaseModel):
    name: str  # Include the extension in the name, e.g. "financials.csv"
    description: str


DATA_PROVIDED = LocalDataSource(
    name="financials_final.csv",
    description=financials_description,
)
