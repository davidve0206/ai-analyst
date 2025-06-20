"""
Constants for the Wide World Importers database project, which is used in development.
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
# WideWorldImporters Database Catalog

The WideWorldImporters database contains all the transaction information and daily data for sales and purchases, as well as sensor data for vehicles and cold rooms.

---

## Schemas

WideWorldImporters uses schemas for different purposes: storing data, controlling access, and enabling integration with data warehouses.

### Data Schemas

These schemas contain the core data. Many common tables are located in the `Application` schema.

| Schema      | Description |
|-------------|-------------|
| **Application** | Application-wide users, contacts, and parameters. Contains reference tables used across multiple schemas. |
| **Purchasing**  | Stock item purchases from suppliers and supplier details. |
| **Sales**       | Stock item sales to customers, including customer and salesperson details. |
| **Warehouse**   | Stock inventory and transactions. |

### Secure-access Schemas

Used by external apps to access the database without direct access to data tables.

| Schema     | Description |
|------------|-------------|
| **Website** | All website database access. |
| **Reports** | Used by Reporting Services (not used in initial release). |
| **PowerBI** | Used by Power BI dashboards via Enterprise Gateway (not used in initial release). |

### Development Schemas

Special-purpose schemas for integration and sequencing.

| Schema       | Description |
|--------------|-------------|
| **Integration** | Objects and procedures for ETL to `WideWorldImportersDW`. |
| **Sequences**   | Stores sequences used by all tables. |

---

## Tables

### Application Schema

General configuration and reference data.

| Table               | Description |
|---------------------|-------------|
| `SystemParameters`  | System-wide configurable parameters. |
| `People`            | Users and contacts, with login data if applicable. |
| `Cities`            | References to cities for all addresses; includes spatial location. |
| `StateProvinces`    | Includes spatial boundaries of states/provinces. |
| `Countries`         | Includes spatial boundaries of countries/regions. |
| `DeliveryMethods`   | Delivery options (truck, courier, pickup, etc.). |
| `PaymentMethods`    | Payment options (cash, check, EFT, etc.). |
| `TransactionTypes`  | Types of transactions (invoice, credit note, etc.). |

### Purchasing Schema

Supplier and purchase order data.

| Table                 | Description |
|-----------------------|-------------|
| `Suppliers`           | Supplier organizations. |
| `SupplierCategories`  | Categories (e.g. novelties, toys). |
| `SupplierTransactions`| Supplier-related financial transactions. |
| `PurchaseOrders`      | Supplier purchase order details. |
| `PurchaseOrderLines`  | Purchase order line items. |

### Sales Schema

Customer and sales data.

| Table                 | Description |
|-----------------------|-------------|
| `Customers`           | Customer entities (orgs or individuals). |
| `CustomerCategories`  | Customer types (e.g. supermarkets). |
| `BuyingGroups`        | Grouped customers for bulk buying. |
| `CustomerTransactions`| Customer financial transactions. |
| `SpecialDeals`        | Pricing deals, fixed or discounted. |
| `Orders`              | Customer orders. |
| `OrderLines`          | Order line items. |
| `Invoices`            | Invoice records. |
| `InvoiceLines`        | Invoice line items. |

### Warehouse Schema

Stock and environmental sensor data.

| Table                   | Description |
|-------------------------|-------------|
| `StockItems`            | Stock item data. |
| `StockItemHoldings`     | Frequently updated stock details. |
| `StockGroups`           | Categorization (e.g. toys, food). |
| `StockItemStockGroups`  | Many-to-many mapping of stock and groups. |
| `Colors`                | Optional color tagging. |
| `PackageTypes`          | Packaging methods (box, pallet, etc.). |
| `StockItemTransactions` | All stock item movement records. |
| `VehicleTemperatures`   | Temperature sensor data from vehicles. |
| `ColdRoomTemperatures`  | Temperature sensor data from cold rooms. |

---

## Design Considerations

### Schema Design

- Schemas group commonly queried tables to reduce complexity.
- Schema definitions are code-generated from metadata in `WWI_Preparation` for consistency.

### Table Design

- All tables have single-column primary keys.
- Extended descriptions exist for all schemas, tables, columns, and constraints (except memory-optimized tables).
- Foreign keys are indexed unless a suitable existing index is present.
- Sequences (not IDENTITY columns) are used for auto-numbering.
- `TransactionID` sequence is shared across `CustomerTransactions`, `SupplierTransactions`, and `StockItemTransactions`.

---

## Security Schemas

- External applications do not access data schemas directly.
- Views and stored procedures in secure-access schemas (`Website`, `Reports`, `PowerBI`) control access.
- Example: Power BI dashboards access the database through a read-only user limited to `SELECT` and `EXECUTE` on the PowerBI schema.

---

## Stored Procedures

Stored procedures are organized by schema.

### Website Schema

Procedures used by web front-end applications.

| Procedure                  | Purpose |
|----------------------------|---------|
| `ActivateWebsiteLogon`     | Grants web access to a person. |
| `ChangePassword`           | Changes user passwords. |
| `InsertCustomerOrders`     | Inserts customer orders and lines. |
| `InvoiceCustomerOrders`    | Processes order invoices. |
| `RecordColdRoomTemperatures` | Inserts cold room sensor data (TVP). |
| `RecordVehicleTemperature` | Updates vehicle temperatures from JSON. |
| `SearchForCustomers`       | Finds customers by name. |
| `SearchForPeople`          | Finds people by name. |
| `SearchForStockItems`      | Finds stock by name/comments. |
| `SearchForStockItemsByTags`| Finds stock by tags. |
| `SearchForSuppliers`       | Finds suppliers by name. |

### Integration Schema

Used by ETL processes to fetch data for export."""
