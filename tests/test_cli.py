import unittest
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pk_assist.cli as cli
from pk_assist.notes import VectorRecord
from pk_assist.evaluation import EvaluationDatasetError, RetrievalAggregate


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
        self.assertIn("Cited:", printed)
        self.assertIn("kafka.md#chunk-0", printed)
        self.assertLess(
            printed.index("Constructed context:"),
            printed.index("Generated answer:"),
        )
        self.assertLess(
            printed.index("Generated answer:"),
            printed.index("Cited:"),
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
        self.assertIn("Cited:", printed)
        self.assertNotIn("#chunk-", printed)

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


class RunCliEvaluateTests(unittest.TestCase):
    def test_evaluate_command_uses_explicit_top_k_and_prints_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("[]", encoding="utf-8")
            aggregate = RetrievalAggregate(5, 0, 0.0, 0.0)
            database = object()

            with patch.object(cli, "DATABASE", database):
                with patch.object(cli, "load_evaluation_cases", return_value=[]) as load:
                    with patch.object(cli, "evaluate_retrieval", return_value=[]) as evaluate:
                        with patch.object(cli, "aggregate_retrieval", return_value=aggregate):
                            with patch.object(cli, "print_evaluation_results") as print_results:
                                with patch.object(cli, "print_aggregate_results") as print_aggregate:
                                    with patch(
                                        "builtins.input",
                                        side_effect=[f"evaluate   {eval_path}   5", "bye"],
                                    ):
                                        cli.run_cli()

            load.assert_called_once_with(eval_path)
            evaluate.assert_called_once_with([], database, 5)
            print_results.assert_called_once_with([])
            print_aggregate.assert_called_once_with(aggregate)

    def test_evaluate_command_defaults_top_k_to_three(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("[]", encoding="utf-8")
            database = object()

            with patch.object(cli, "DATABASE", database):
                with patch.object(cli, "load_evaluation_cases", return_value=[]):
                    with patch.object(cli, "evaluate_retrieval", return_value=[]) as evaluate:
                        with patch.object(
                            cli,
                            "aggregate_retrieval",
                            return_value=RetrievalAggregate(3, 0, 0.0, 0.0),
                        ):
                            with patch("builtins.input", side_effect=[f"evaluate {eval_path}", "bye"]):
                                cli.run_cli()

            evaluate.assert_called_once_with([], database, 3)

    def test_non_integer_top_k_prints_error_and_continues(self):
        output = StringIO()

        with patch("builtins.input", side_effect=["evaluate cases.json abc", "bye"]):
            with redirect_stdout(output):
                cli.run_cli()

        self.assertIn("top_k must be a whole number.", output.getvalue())

    def test_non_positive_top_k_prints_error_and_does_not_load_dataset(self):
        output = StringIO()

        with patch.object(cli, "load_evaluation_cases") as load:
            with patch("builtins.input", side_effect=["evaluate cases.json 0", "bye"]):
                with redirect_stdout(output):
                    cli.run_cli()

        self.assertIn("top_k must be greater than zero.", output.getvalue())
        load.assert_not_called()

    def test_missing_evaluation_file_does_not_attempt_to_load_it(self):
        output = StringIO()

        with patch.object(cli, "load_evaluation_cases") as load:
            with patch(
                "builtins.input",
                side_effect=["evaluate missing-evaluation-cases.json 3", "bye"],
            ):
                with redirect_stdout(output):
                    cli.run_cli()

        self.assertIn("Path is not a file!", output.getvalue())
        load.assert_not_called()

    def test_dataset_validation_error_is_printed_and_cli_continues(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("not-json", encoding="utf-8")
            output = StringIO()

            with patch.object(
                cli,
                "load_evaluation_cases",
                side_effect=EvaluationDatasetError("Evaluation file contains invalid JSON."),
            ):
                with patch(
                    "builtins.input",
                    side_effect=[f"evaluate {eval_path} 3", "bye"],
                ):
                    with redirect_stdout(output):
                        cli.run_cli()

            self.assertIn("Evaluation file contains invalid JSON.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
