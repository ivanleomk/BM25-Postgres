from lib.db import get_connection
from lib.models import CommentChunk
from psycopg2.extras import DictCursor
import ast
from rich.table import box
from rich.console import Console
from rich.table import Table


def run_text_query(query: str):
    try:
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)
        query = f"""
        SELECT *, paradedb.rank_bm25(id)
        FROM search_idx.search(
          '(text:"{query}" OR context:"{query}")',
          limit_rows => 5
        );
        """
        cursor.execute(query)
        results = [dict(item) for item in cursor.fetchall()]
        results = [
            CommentChunk(**{**item, "vector": ast.literal_eval(item["vector"])})
            for item in results
        ]

        console = Console()
        table = Table(title="Results", box=box.HEAVY, padding=(1, 2), show_lines=True)
        table.add_column("ID", style="dim", width=12)
        table.add_column("Text", justify="left")
        table.add_column("Repo", justify="left")
        table.add_column("Context", justify="left")

        for result in results:
            table.add_row(
                str(result.id),
                result.text[:100],
                result.repo,
                result.context[:200] + "...",
            )
        console.print(table)

    except Exception as e:
        print(f"An error occurred: {e}")


run_text_query("wheel torch")
