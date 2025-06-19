# ai-analyst

## Configuration

There is two types of configuration; on one side, a `.env` file, for configuration that should not change between runs of the agent (e.g., API Keys), on the other, a `sqlite` database for configuration the user can change at will (e.g., the list of websites the model is allowed to use).

### Authentication

We will use Azure's own [identity management](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#authenticate-with-defaultazurecredential&preserve-view=true) for authenticating.
