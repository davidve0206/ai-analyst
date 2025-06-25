# Model Evaluation Documentation and Notes

## Data

To simulate a company we will use Microsoft's [WideWorldImporters](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers) OLAP database ([WideWorldImportersDW-Standard](https://github.com/Microsoft/sql-server-samples/releases/download/wide-world-importers-v1.0/WideWorldImportersDW-Standard.bacpac)) database, hosted as an Azure SQL Database standard edition. Documentation on how to set this up can be found on [Microsoft's Documentation](https://learn.microsoft.com/en-gb/sql/samples/wide-world-importers-dw-install-configure?view=sql-server-ver17&tabs=sql-database).

The following changes have been implemented in the database based on issues that the agents were having a hard time with (scripts are also available in this folder):

1. Adding Fiscal Quarter and Calendar Quarter columns to the Dimension.Date table
2. Updating dates so the most recent values are current
