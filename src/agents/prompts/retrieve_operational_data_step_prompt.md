Today is {date}.

You have already retrieved the last three years of {kpi_description}, which you stored at {previous_output_location}.

You are now tasked to retrieve and analyze more detailed operational data for the last period of {periodicity} data that you retrieved. For this analysis, please create csv files with the data you retrieve and calculations supporting your analysis, and provide a summary of your findings.

## Examples

Example 1:

If you have already retrieved sales by geography, and the most recent data you have is for January 2022:

1. Filter the data at {input_location} to include only data that:
   - Corresponds to the geography retrieved
   - Corresponds to January 2022 (or whatever the last period retrieved is)
2. Create a new Dataframe with sales grouped by smaller geography:
   - For example, if you already retrieved country level data, group by state / province or city
   - Order by highest sale total
3. Repeat for sales by product category, product name or product ID.
4. Repeat for sales by client name or client ID.

Example 2:

If you have already retrieved sales by product or product ID, and the most recent data is July 2025:

1. Filter the data at {input_location} to include only data that:
   - Corresponds to the product or product ID retrieved
   - Corresponds to July 2025 (or whatever the last period retrieved is)
2. Create a new Dataframe with sales grouped by geography:
   - For example, retrieve group data by country
   - Order by highest sale total
3. Repeat for sales by client name or client ID.

## Notes

Any breakdown should include the total sales and the percentage of total they represent.

Prefer ordering the results by sales, so the most important groups are on top.

Note that you should always first filter the data {grouping_str} the last period available, before grouping by any other category.

## Previous outputs
