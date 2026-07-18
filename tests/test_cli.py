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


class RunCliCompareTests(unittest.TestCase):
    def test_compare_command_uses_all_settings_and_prints_aggregates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("[]", encoding="utf-8")
            database = object()
            aggregates = [
                RetrievalAggregate(3, 0, 0.0, 0.0),
                RetrievalAggregate(5, 0, 0.0, 0.0),
            ]

            with patch.object(cli, "DATABASE", database):
                with patch.object(cli, "load_evaluation_cases", return_value=[]) as load:
                    with patch.object(
                        cli,
                        "compare_retrieval_settings",
                        return_value=aggregates,
                    ) as compare:
                        with patch.object(cli, "print_aggregate_list") as print_list:
                            with patch(
                                "builtins.input",
                                side_effect=[f"compare {eval_path} 3 5", "bye"],
                            ):
                                cli.run_cli()

            load.assert_called_once_with(eval_path)
            compare.assert_called_once_with([], database, [3, 5])
            print_list.assert_called_once_with(aggregates)

    def test_requires_at_least_two_settings(self):
        output = StringIO()

        with patch.object(cli, "load_evaluation_cases") as load:
            with patch(
                "builtins.input",
                side_effect=["compare eval/evaluation_cases.json 3", "bye"],
            ):
                with redirect_stdout(output):
                    cli.run_cli()

        self.assertIn("Insufficient arguments for compare command", output.getvalue())
        load.assert_not_called()

    def test_non_integer_setting_prints_error_and_does_not_load_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("[]", encoding="utf-8")
            output = StringIO()

            with patch.object(cli, "load_evaluation_cases") as load:
                with patch(
                    "builtins.input",
                    side_effect=[f"compare {eval_path} 3 abc", "bye"],
                ):
                    with redirect_stdout(output):
                        cli.run_cli()

            self.assertIn("top_k must be a whole number.", output.getvalue())
            load.assert_not_called()

    def test_non_positive_setting_prints_error_and_does_not_load_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("[]", encoding="utf-8")
            output = StringIO()

            with patch.object(cli, "load_evaluation_cases") as load:
                with patch(
                    "builtins.input",
                    side_effect=[f"compare {eval_path} 3 0", "bye"],
                ):
                    with redirect_stdout(output):
                        cli.run_cli()

            self.assertIn("top_k must be greater than zero.", output.getvalue())
            load.assert_not_called()

    def test_missing_evaluation_file_does_not_run_comparison(self):
        output = StringIO()

        with patch.object(cli, "compare_retrieval_settings") as compare:
            with patch(
                "builtins.input",
                side_effect=["compare missing-cases.json 3 5", "bye"],
            ):
                with redirect_stdout(output):
                    cli.run_cli()

        self.assertIn("Path is not a file!", output.getvalue())
        compare.assert_not_called()

    def test_dataset_validation_error_is_printed_and_comparison_is_not_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_path = Path(temp_dir) / "cases.json"
            eval_path.write_text("not-json", encoding="utf-8")
            output = StringIO()

            with patch.object(
                cli,
                "load_evaluation_cases",
                side_effect=EvaluationDatasetError(
                    "Evaluation file contains invalid JSON."
                ),
            ):
                with patch.object(cli, "compare_retrieval_settings") as compare:
                    with patch(
                        "builtins.input",
                        side_effect=[f"compare {eval_path} 3 5", "bye"],
                    ):
                        with redirect_stdout(output):
                            cli.run_cli()

            self.assertIn("Evaluation file contains invalid JSON.", output.getvalue())
            compare.assert_not_called()


class RunCliUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)
        self.note_path = self.folder / "kafka.md"
        self.note_path.write_text("Kafka stores events.", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()
        cli.NOTES = []
        cli.CHUNKS = []
        cli.EMBEDDED_CHUNKS = []
        cli.DATABASE = None
        cli.FOLDER = None

    def initialize_app(self):
        with patch.object(cli.sys, "argv", ["pk_assist.cli", str(self.folder)]):
            with redirect_stdout(StringIO()):
                cli.init_app()

    def run_update(self):
        with patch("builtins.input", side_effect=["update", "bye"]):
            with redirect_stdout(StringIO()):
                cli.run_cli()

    def test_update_adds_records_for_a_new_note(self):
        self.initialize_app()
        new_note = self.folder / "memory.txt"
        new_note.write_text("Agents use memory.", encoding="utf-8")

        self.run_update()

        self.assertEqual(
            {record.note_path for record in cli.DATABASE.records},
            {self.note_path, new_note},
        )

    def test_update_replaces_records_for_a_changed_note(self):
        self.initialize_app()
        old_records = list(cli.DATABASE.records)
        self.note_path.write_text("Kafka uses consumer groups.", encoding="utf-8")

        self.run_update()

        self.assertEqual(cli.DATABASE.count(), 1)
        self.assertEqual(cli.DATABASE.records[0].content, "Kafka uses consumer groups.")
        self.assertNotEqual(cli.DATABASE.records, old_records)

    def test_update_removes_records_for_a_deleted_note(self):
        self.initialize_app()
        self.note_path.unlink()

        self.run_update()

        self.assertEqual(cli.NOTES, [])
        self.assertEqual(cli.DATABASE.records, [])

    def test_update_is_deterministic_for_an_unchanged_note(self):
        self.initialize_app()
        original_records = list(cli.DATABASE.records)

        self.run_update()

        self.assertEqual(cli.DATABASE.records, original_records)

    def test_update_command_rebuilds_the_database_once(self):
        cli.FOLDER = self.folder

        with patch.object(cli, "load_database") as load_database:
            with patch("builtins.input", side_effect=["update", "bye"]):
                cli.run_cli()

        load_database.assert_called_once_with(cli.FOLDER)

    def test_update_prints_a_completion_message(self):
        self.initialize_app()
        output = StringIO()

        with patch("builtins.input", side_effect=["update", "bye"]):
            with redirect_stdout(output):
                cli.run_cli()

        self.assertIn("Notes updated successfully.", output.getvalue())

    def test_update_without_an_initialized_folder_does_not_rebuild(self):
        cli.FOLDER = None
        output = StringIO()

        with patch.object(cli, "load_database") as load_database:
            with patch("builtins.input", side_effect=["update", "bye"]):
                with redirect_stdout(output):
                    cli.run_cli()

        load_database.assert_not_called()
        self.assertIn("No notes folder passed!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
