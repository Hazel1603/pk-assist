import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pk_assist.cli as cli
from pk_assist.notes import VectorRecord


class FakeDatabase:
    def __init__(self, records=None):
        self.queries = []
        self.records = records

    def search(self, query: str):
        self.queries.append(query)
        if self.records is not None:
            return self.records

        return [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
                embedding=[1.0],
            )
        ]


class FakeRuntimeModel:
    def generate(self, prompt: str) -> str:
        return "Kafka is described as storing events."


class RunCliAskTests(unittest.TestCase):
    def test_ask_command_prints_context_then_generated_answer(self):
        database = FakeDatabase()
        output = StringIO()

        with patch.object(cli, "DATABASE", database):
            with patch.object(cli, "PlaceholderModel", FakeRuntimeModel):
                with patch("builtins.input", side_effect=["ask   Kafka  ", "bye"]):
                    with redirect_stdout(output):
                        cli.run_cli()

        printed = output.getvalue()

        self.assertEqual(database.queries, ["Kafka"])
        self.assertIn("Constructed context:", printed)
        self.assertIn("Source: kafka.md", printed)
        self.assertIn("Kafka stores events.", printed)
        self.assertIn("Generated answer:", printed)
        self.assertIn("Kafka is described as storing events.", printed)
        self.assertLess(
            printed.index("Constructed context:"),
            printed.index("Generated answer:"),
        )

    def test_ask_command_prints_friendly_response_when_no_context_is_available(self):
        database = FakeDatabase(records=[])
        output = StringIO()

        with patch.object(cli, "DATABASE", database):
            with patch.object(cli, "PlaceholderModel", FakeRuntimeModel):
                with patch("builtins.input", side_effect=["ask Kafka", "bye"]):
                    with redirect_stdout(output):
                        cli.run_cli()

        printed = output.getvalue()

        self.assertEqual(database.queries, ["Kafka"])
        self.assertIn("Constructed context:", printed)
        self.assertIn("Generated answer:", printed)
        self.assertIn(
            "I could not find relevant context to answer that question.",
            printed,
        )

    def test_ask_command_with_no_question_prints_no_query_message(self):
        database = FakeDatabase()
        output = StringIO()

        with patch.object(cli, "DATABASE", database):
            with patch("builtins.input", side_effect=["ask   ", "bye"]):
                with redirect_stdout(output):
                    cli.run_cli()

        printed = output.getvalue()

        self.assertEqual(database.queries, [])
        self.assertIn("No query provided.", printed)


if __name__ == "__main__":
    unittest.main()
