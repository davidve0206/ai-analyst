# ai-analyst

## Configuration

There is two types of configuration; on one side, a `.env` file, for configuration that should not change between runs of the agent (e.g., API Keys), on the other, a `sqlite` database for configuration the user can change at will (e.g., the list of websites the model is allowed to use).

### Authentication

We will use Azure's own [identity management](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#authenticate-with-defaultazurecredential&preserve-view=true) for authenticating. It's the user's decision to use environment variables, cli, or any of the methods Azure provides.

## Running Locally

For now, the project only has configuration for using Azure SQL Database; make sure your local configuration has the required ODBC Driver.

## Testing

We have a single tests folders; that said, this test actually include agent evaluations; some of the evaluations are fully represented in code, while others might just be a a way to run an agent with a set scenario, but the actual evaluation might be human driven.
