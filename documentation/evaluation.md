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
   8. Does the report accurately present the last information period?
2. Questions regarding depth (evaluates reasoning capabilities):
   1. Is the content of each section accurate to the section's description? (5 points, 1 per section)
   2. Does the analysis in the report accurately represent the evolution of the KPI? (e.g., if there is seasonality, as there usually is in sales, the best comparison is the same period the year before, not the previous month)
   3. Does the report include an analysis of the detailed data? (i.e., is not just included without any context)
   4. Are all graphs relevant to the report?
   5. Are all graphs adequate for the data presented? (e.g., if the data represents categories, a line graph is not an adequate representation)
   6. Are all projections adequate for the data presented?  (e.g., if the data represents categories, a trend line and projection does not make sense)
   7. Does the report accurately note any "special case" present? (e.g., declining sales or a sharp change in trend)
   8. Does the report provide next steps for any "special case" present?
   9. Are all statements in the report sustained with data? (i.e., make sure the agent didn't make something up)

## Data

We have received the financials_raw.csv file from the project partner (data not included in the repository due to weight). The following changes were implemented:

1. Remove data for December 2023 (only 2 sales in the month)
