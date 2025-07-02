# Model Evaluation Documentation and Notes

## Evaluation Criteria

### Final Report

For the final report, we will follow a scoring system that evaluates the following set of questions; the idea with this set of questions is to make it as easy to follow as possible, so it can be evolved into an AI as judge system later on. Each question is a yes or no answer, reducing the risk of bias or changes between runs (pending: include literature supporting this).

1. Questions regarding form (evaluates instruction following):
   1. Does the report include all the required sections? (Executive Summary, Overview, Trends & Context, In Depth Analysis, Forward Outlook)
   2. Does the report actually address the required KPI? (e.g., if the report should be for Sales in California, it should not refer to Sales in Texas)
   3. Does the report include an analysis of the evolution of the KPI?
   4. Does the report include detailed data, in addition to the high level KPI information?
   5. Does the report include at least one graph?
   6. Does the report include a projection of the KPI?
   7. Is the data retrieved correct? (i.e., manually retrieving the data results in the same numbers)
2. Questions regarding depth (evaluates reasoning capabilities):
   1. Is the content of each section accurate to the section's description? (5 points, 1 per section)
   2. Does the analysis in the report accurately represent the evolution of the KPI? (e.g., if there is seasonality, as there usually is in sales, the best comparison is the same period the year before, not the previous month)
   3. Does the report include an analysis of the detailed data? (i.e., is not just included without any context)
   4. Are all graphs relevant to the report?
   5. Are all graphs adequate for the data presented? (e.g., if the data represents categories, a line graph is not an adequate representation)
   6. Are all projections adequate for the data presented?  (e.g., if the data represents categories, a trend line and projection does not make sense)
   7. Does the report accurately note any "special case" present? (e.g., declining sales or a sharp change in trend)
   8. Does the report provide next steps for any "special case" present?

## Data

To simulate a company we will use Microsoft's [WideWorldImporters](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers) OLAP database ([WideWorldImportersDW-Standard](https://github.com/Microsoft/sql-server-samples/releases/download/wide-world-importers-v1.0/WideWorldImportersDW-Standard.bacpac)) database, hosted as an Azure SQL Database standard edition. Documentation on how to set this up can be found on [Microsoft's Documentation](https://learn.microsoft.com/en-gb/sql/samples/wide-world-importers-dw-install-configure?view=sql-server-ver17&tabs=sql-database).

The following changes have been implemented in the database based on issues that the agents were having a hard time with (scripts are also available in this folder):

1. Adding Fiscal Quarter and Calendar Quarter columns to the Dimension.Date table
2. Updating dates so the most recent values are current
