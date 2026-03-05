from mcp.server.fastmcp import FastMCP
import sqlite3

from sqlite_helper import create_db, load_csv_to_table

# Create MCP server
mcp = FastMCP("data-query-server")

# Create SQLite database
conn = create_db()

# Store query history
query_history = []


@mcp.tool()
def load_csv(file_path: str, table_name: str) -> dict:
    """
    Load a CSV file into a SQLite table.

    Parameters:
        file_path: path to the CSV file
        table_name: name of the table

    Returns:
        table metadata including columns and row count
    """

    try:
        result = load_csv_to_table(conn, file_path, table_name)
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def list_tables() -> list:
    """
    List all tables in the database with row counts.
    """

    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    result = []

    for table in tables:
        table_name = table[0]

        count = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        result.append({
            "table": table_name,
            "rows": count
        })

    return result


@mcp.tool()
def describe_schema() -> dict:
    """
    List all tables and their columns with types.
    """

    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    schema = {}

    for table in tables:
        table_name = table[0]

        columns = cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        schema[table_name] = [
            {"column": col[1], "type": col[2]}
            for col in columns
        ]

    return schema


@mcp.tool()
def run_query(sql: str, limit: int = 50):
    """
    Execute a read-only SQL query and return results.
    """

    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER"]

    if any(word in sql.upper() for word in forbidden):
        return {"error": "Only read-only queries allowed"}

    try:
        cursor = conn.cursor()

        rows = cursor.execute(sql).fetchmany(limit)

        columns = [c[0] for c in cursor.description]

        results = [dict(zip(columns, row)) for row in rows]

        query_history.append(sql)

        return results

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_statistics(table_name: str, column: str):
    """
    Compute summary statistics for a column in a table.
    """

    try:
        cursor = conn.cursor()

        stats = cursor.execute(
            f"""
            SELECT
                COUNT("{column}"),
                MIN("{column}"),
                MAX("{column}"),
                AVG("{column}")
            FROM "{table_name}"
            """
        ).fetchone()

        nulls = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}" WHERE "{column}" IS NULL'
        ).fetchone()[0]

        return {
            "count": stats[0],
            "min": stats[1],
            "max": stats[2],
            "mean": stats[3],
            "nulls": nulls
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()