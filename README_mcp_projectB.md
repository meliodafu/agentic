
# Data Query Builder – MCP Server

## Overview

This MCP server allows an AI assistant to query data stored in CSV files using natural language instead of writing SQL manually.

The server loads CSV files into an in-memory SQLite database and provides tools to:

- load datasets
- explore the database schema
- run SQL queries safely
- compute statistics

This enables AI agents such as Claude Desktop or Gemini CLI to analyze structured data efficiently.

---

# Setup

Create a virtual environment and install dependencies.

```bash
uv venv
source .venv/bin/activate
uv pip install "mcp[cli]"
```

Project B only uses standard Python libraries:

- sqlite3
- csv

---

# Run the MCP Server

Start the server locally:

```bash
python server.py
```

Inspect tools:

```bash
mcp dev server.py
```

---

# Gemini CLI Configuration

```json
{
  "mcpServers": {
    "data-query-builder": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Gemini CLI after updating the config.

---

# Tools

## load_csv

Load a CSV file into a SQLite table with automatic type detection.

| Parameter | Type | Required | Description |
|----------|------|---------|-------------|
| file_path | str | yes | path to the CSV file |
| table_name | str | yes | name of the table |

Example:

Load the CSV file `sample_data.csv` into a table called `sales`.

---

## describe_schema

List all tables and their columns in the SQLite database.

---

## run_query

Execute a read-only SQL query.

| Parameter | Type | Required | Description |
|----------|------|---------|-------------|
| sql | str | yes | SQL query |
| limit | int | no | max rows returned |

Forbidden SQL commands:

- DROP
- DELETE
- INSERT
- UPDATE
- ALTER

---

## get_statistics

Compute summary statistics for a column.

| Parameter | Type | Required | Description |
|----------|------|---------|-------------|
| table_name | str | yes | table name |
| column | str | yes | column name |

Returns:

- count
- min
- max
- mean
- null values

---

## list_tables

List all tables in the database with row counts.

---

# Resources

## resource: /schema

Provides the current database schema as JSON.

Example:

```json
{
  "tables": [
    {
      "name": "sales",
      "columns": [
        {"name": "region", "type": "TEXT"},
        {"name": "price", "type": "REAL"}
      ]
    }
  ]
}
```

---

# Limitations

- Database is stored in memory only
- Data is lost when the server stops
- Only read-only SQL queries are allowed

---

# Comparison Results

## Without MCP Tools

Gemini receives raw data pasted in the prompt.

Problems observed:

- limited data analysis
- hallucinated values
- difficult to compute statistics

---

## With MCP Tools

Gemini can:

- load structured datasets
- query the database
- compute statistics accurately

Advantages:

- accurate results
- dynamic queries
- structured data exploration

---

# Prompting Strategy Comparison

## Strategy 1 – Minimal

Prompt:

You have access to tools. Use them.

Result:

Gemini sometimes calls tools inefficiently.

---

## Strategy 3 – Expert Workflow

Prompt:

You are a data analyst.

Phase 1 — Load and explore the dataset  
Phase 2 — Analyze relevant columns using queries  
Phase 3 — Summarize insights based on the results

Result:

- better planning
- more efficient tool usage
- better final answers

---

# Example Scenario

User prompt:

Load the sales dataset and tell me which region has the highest average price.

Tool sequence:

load_csv → describe_schema → run_query → get_statistics
