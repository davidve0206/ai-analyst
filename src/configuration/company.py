"""
Constants for the Wide World Importers database project, which is used in development.

This file includes information about the company, the database and the report structure,
which are configuration constants used throughout the project but don't need to be changed
through the frontend.
"""

REPORT_STRUCTURE = """
1. **Executive Summary**
    - This section provides a high-level summary of the KPIs for the reporting period, as well as any other key findings or insights.
    - Current value of KPIs and comparison to last period.
    - No chars or tables.
2. **Overview**
    - Quick snapshot of the value of the KPIs for the last available period.
    - Comparison with the previous period.
    - Key insights or highlights about performance.
3. **Trends and Context**
    - Short-term trend chart or table (last 3–5 periods) for each KPI.
    - High-level explanation of what drives changes in each KPI (e.g., volume, price, cost impact, broader market events).
    - Other relevant operational metrics directly influencing the KPIs.
"""

COMPANY_DESCRIPTION = """
Wide World Importers (WWI) is a wholesale novelty goods importer and distributor operating from the San Francisco bay area.

As a wholesaler, WWI's customers are mostly companies who resell to individuals. WWI sells to retail customers across the United States including specialty stores, supermarkets, computing stores, tourist attraction shops, and some individuals. WWI also sells to other wholesalers via a network of agents who promote the products
on WWI's behalf. While all of WWI's customers are currently based in the United States, the company is intending to push for expansion into other countries/regions.

WWI buys goods from suppliers including novelty and toy manufacturers, and other novelty wholesalers. They stock the goods in their WWI warehouse and reorder from suppliers as needed to fulfil customer orders. They also purchase large volumes
of packaging materials, and sell these in smaller quantities as a convenience for the customers.
"""

FISCAL_YEAR_END = "October 31"

DATABASE_CATALOG = """
# WideWorldImportersDW Database Catalog

**Date:** 02/28/2023  
**Applies to:**  
- SQL Server: Not supported  
- Azure SQL Database  
- Azure Synapse Analytics  
- Analytics Platform System (PDW)

Explanations for the schemas, tables, and stored procedures in the WideWorldImportersDW database.

The `WideWorldImportersDW` database is used for data warehousing and analytical processing. The transactional data about sales and purchases is generated in the `WideWorldImporters` database and loaded into `WideWorldImportersDW` using a daily ETL process.

The data in `WideWorldImportersDW` mirrors the data in `WideWorldImporters`, but the tables are organized differently. While `WideWorldImporters` uses a traditional normalized schema, `WideWorldImportersDW` uses a star schema approach. Besides the fact and dimension tables, the database includes several staging tables used in the ETL process.

---

## Schemas

The different types of tables are organized in three schemas:

| Schema      | Description                                      |
|-------------|--------------------------------------------------|
| Dimension   | Dimension tables.                                |
| Fact        | Fact tables.                                     |
| Integration | Staging tables and other objects needed for ETL. |

---

## Tables

The dimension and fact tables are listed below. The tables in the `Integration` schema are used only for the ETL process and are not listed.

### Dimension Tables

`WideWorldImportersDW` has the following dimension tables, along with their source tables from the `WideWorldImporters` database:

| Table          | Source Tables                                                                 |
|----------------|--------------------------------------------------------------------------------|
| City           | Application.Cities, Application.StateProvinces, Application.Countries         |
| Customer       | Sales.Customers, Sales.BuyingGroups, Sales.CustomerCategories                  |
| Date           | New table with information about dates, including financial year (Nov 1 start) |
| Employee       | Application.People                                                             |
| StockItem      | Warehouse.StockItems, Warehouse.Colors, Warehouse.PackageType                 |
| Supplier       | Purchasing.Suppliers, Purchasing.SupplierCategories                            |
| PaymentMethod  | Application.PaymentMethods                                                     |
| TransactionType| Application.TransactionTypes                                                   |

### Fact Tables

The following fact tables are used in `WideWorldImportersDW`:

| Table          | Source Tables                                                  | Sample Analytics                                                                 |
|----------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Order          | Sales.Orders and Sales.OrderLines                              | Sales people, picker/packer productivity, on-time pick orders, back orders       |
| Sale           | Sales.Invoices and Sales.InvoiceLines                          | Sales dates, delivery dates, profitability over time/by salesperson              |
| Purchase       | Purchasing.PurchaseOrderLines                                  | Expected vs actual lead times                                                    |
| Transaction    | Sales.CustomerTransactions, Purchasing.SupplierTransactions    | Measuring issue dates vs finalization dates and amounts                          |
| Movement       | Warehouse.StockTransactions                                    | Movements over time                                                               |
| Stock Holding  | Warehouse.StockItemHoldings                                    | On-hand stock levels and value                                                    |
"""
