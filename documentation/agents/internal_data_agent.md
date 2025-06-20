# Database Agent Documentation

## Model

## Prompt

The prompt includes a list of the database tables.

## Tools

The agent has access the InternalDatabase class, which exposes a few utilities:

1. The ability to view the list of tables in the database
2. The ability to request schemas for a list of tables in the database
3. The ability to execute read-only raw queries written
