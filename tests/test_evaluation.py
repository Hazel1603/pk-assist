import tempfile
import unittest
from pathlib import Path

from pk_assist.evaluation import (
    EvaluationCase,
    EvaluationDatasetError,
    EvaluationResult,
    RetrievalAggregate,
    aggregate_retrieval,
    calculate_recall_at_k,
    compare_retrieval_settings,
    evaluate_case,
    evaluate_retrieval,
    load_evaluation_cases,
)
from pk_assist.notes import VectorRecord, build_context_result


class StubVectorDatabase:
    def __init__(self, records):
        self.records = records
        self.search_calls = []

    def search(self, query, limit):
        self.search_calls.append((query, limit))
        return self.records


class LoadEvaluationCasesTests(unittest.TestCase):
    def test_loads_question_and_expected_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                """
                [
                  {
                    "question": "What did I write about Kafka?",
                    "expected_sources": ["sample_notes/kafka.md"],
                    "expected_concepts": ["consumer lag"]
                  }
                ]
                """,
                encoding="utf-8",
            )

            cases = load_evaluation_cases(path)

            self.assertEqual(
                cases,
                [
                    EvaluationCase(
                        question="What did I write about Kafka?",
                        expected_sources=[Path("sample_notes/kafka.md")],
                        expected_concepts=["consumer lag"],
                    )
                ],
            )

    def test_loads_multiple_evaluation_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                """
                [
                  {
                    "question": "What did I write about Kafka?",
                    "expected_sources": ["sample_notes/kafka.md"],
                    "expected_concepts": ["consumer lag"]
                  },
                  {
                    "question": "Find notes related to vector databases.",
                    "expected_sources": ["sample_notes/vector-databases.md"],
                    "expected_concepts": ["embeddings", "semantic search"]
                  }
                ]
                """,
                encoding="utf-8",
            )

            cases = load_evaluation_cases(path)

            self.assertEqual(len(cases), 2)
            self.assertEqual(cases[0].question, "What did I write about Kafka?")
            self.assertEqual(
                cases[1].expected_sources,
                [Path("sample_notes/vector-databases.md")],
            )

    def test_expected_concepts_are_optional(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                """
                [
                  {
                    "question": "Summarize my notes on agent memory.",
                    "expected_sources": ["sample_notes/agent-memory.txt"]
                  }
                ]
                """,
                encoding="utf-8",
            )

            cases = load_evaluation_cases(path)

            self.assertEqual(cases[0].expected_concepts, [])

    def test_loads_empty_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text("[]", encoding="utf-8")

            cases = load_evaluation_cases(path)

            self.assertEqual(cases, [])

    def test_invalid_json_raises_evaluation_dataset_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text('[{"question": "Kafka"}', encoding="utf-8")

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "invalid JSON",
            ):
                load_evaluation_cases(path)

    def test_missing_question_raises_evaluation_dataset_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                '[{"expected_sources": ["kafka.md"]}]',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "missing required field: question",
            ):
                load_evaluation_cases(path)

    def test_missing_expected_sources_raises_evaluation_dataset_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text('[{"question": "Kafka"}]', encoding="utf-8")

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "missing required field: expected_sources",
            ):
                load_evaluation_cases(path)

    def test_non_list_dataset_raises_evaluation_dataset_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                '{"question": "Kafka", "expected_sources": ["kafka.md"]}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "must be a list of cases",
            ):
                load_evaluation_cases(path)

    def test_missing_file_raises_evaluation_dataset_error(self):
        path = Path("does-not-exist-evaluation-cases.json")

        with self.assertRaisesRegex(
            EvaluationDatasetError,
            "does not exist",
        ):
            load_evaluation_cases(path)

    def test_non_object_case_raises_precise_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text('["not-an-object"]', encoding="utf-8")

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "case at index 0 must be an object",
            ):
                load_evaluation_cases(path)

    def test_non_list_expected_sources_raises_precise_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "evaluation_cases.json"
            path.write_text(
                '[{"question": "Kafka", "expected_sources": "kafka.md"}]',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                EvaluationDatasetError,
                "expected_sources must be a list of strings",
            ):
                load_evaluation_cases(path)


class CalculateRecallAtKTests(unittest.TestCase):
    def test_returns_one_when_all_expected_sources_are_retrieved(self):
        recall = calculate_recall_at_k(
            [Path("kafka.md"), Path("memory.md")],
            [Path("memory.md"), Path("kafka.md")],
        )

        self.assertEqual(recall, 1.0)

    def test_returns_fraction_when_some_expected_sources_are_retrieved(self):
        recall = calculate_recall_at_k(
            [Path("kafka.md"), Path("memory.md")],
            [Path("kafka.md"), Path("other.md")],
        )

        self.assertEqual(recall, 0.5)

    def test_returns_zero_when_no_expected_sources_are_retrieved(self):
        recall = calculate_recall_at_k(
            [Path("kafka.md"), Path("memory.md")],
            [Path("chunking.md"), Path("other.md")],
        )

        self.assertEqual(recall, 0.0)

    def test_duplicate_expected_sources_do_not_change_recall(self):
        recall = calculate_recall_at_k(
            [Path("kafka.md"), Path("memory.md"), Path("kafka.md")],
            [Path("kafka.md"), Path("other.md")],
        )

        self.assertEqual(recall, 0.5)

    def test_duplicate_retrieved_sources_do_not_change_recall(self):
        recall = calculate_recall_at_k(
            [Path("kafka.md"), Path("memory.md")],
            [Path("kafka.md"), Path("kafka.md"), Path("other.md")],
        )

        self.assertEqual(recall, 0.5)

    def test_returns_zero_when_there_are_no_expected_sources(self):
        recall = calculate_recall_at_k(
            [],
            [Path("kafka.md")],
        )

        self.assertEqual(recall, 0.0)


class EvaluateCaseTests(unittest.TestCase):
    def setUp(self):
        self.case = EvaluationCase(
            question="What did I write about Kafka?",
            expected_sources=[Path("kafka.md"), Path("memory.md")],
            expected_concepts=["consumer groups"],
        )

    def test_searches_using_the_case_question_and_top_k(self):
        database = StubVectorDatabase([])

        evaluate_case(self.case, database, top_k=5)

        self.assertEqual(
            database.search_calls,
            [("What did I write about Kafka?", 5)],
        )

    def test_returns_the_case_retrieved_sources_and_recall(self):
        records = [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka uses consumer groups.",
                embedding=[],
            ),
            VectorRecord(
                note_path=Path("other.md"),
                chunk_index=0,
                content="An unrelated note.",
                embedding=[],
            ),
        ]
        database = StubVectorDatabase(records)

        result = evaluate_case(self.case, database, top_k=2)

        self.assertEqual(
            result,
            EvaluationResult(
                case=self.case,
                top_k=2,
                retrieved_sources=[Path("kafka.md"), Path("other.md")],
                recall_at_k=0.5,
                context_size_chars=len(build_context_result(records).text),
            ),
        )

    def test_counts_the_size_of_the_constructed_context(self):
        records = [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events in a durable log.",
                embedding=[],
            )
        ]
        database = StubVectorDatabase(records)

        result = evaluate_case(self.case, database, top_k=1)

        self.assertEqual(
            result.context_size_chars,
            len(build_context_result(records).text),
        )

    def test_handles_no_retrieved_records(self):
        database = StubVectorDatabase([])

        result = evaluate_case(self.case, database, top_k=3)

        self.assertEqual(result.retrieved_sources, [])
        self.assertEqual(result.recall_at_k, 0.0)
        self.assertEqual(result.context_size_chars, 0)


class EvaluateRetrievalTests(unittest.TestCase):
    def test_evaluates_every_case_with_the_same_top_k(self):
        cases = [
            EvaluationCase(
                question="Kafka question",
                expected_sources=[Path("kafka.md")],
                expected_concepts=[],
            ),
            EvaluationCase(
                question="Memory question",
                expected_sources=[Path("memory.md")],
                expected_concepts=[],
            ),
        ]
        database = StubVectorDatabase([])

        results = evaluate_retrieval(cases, database, top_k=5)

        self.assertEqual(
            database.search_calls,
            [("Kafka question", 5), ("Memory question", 5)],
        )
        self.assertEqual([result.case for result in results], cases)

    def test_returns_no_results_for_an_empty_dataset(self):
        database = StubVectorDatabase([])

        results = evaluate_retrieval([], database, top_k=3)

        self.assertEqual(results, [])
        self.assertEqual(database.search_calls, [])


class AggregateRetrievalTests(unittest.TestCase):
    def setUp(self):
        case = EvaluationCase(
            question="Example question",
            expected_sources=[Path("expected.md")],
            expected_concepts=[],
        )
        self.results = [
            EvaluationResult(
                case=case,
                top_k=3,
                retrieved_sources=[Path("expected.md")],
                recall_at_k=1.0,
                context_size_chars=600,
            ),
            EvaluationResult(
                case=case,
                top_k=3,
                retrieved_sources=[Path("other.md")],
                recall_at_k=0.5,
                context_size_chars=900,
            ),
            EvaluationResult(
                case=case,
                top_k=3,
                retrieved_sources=[],
                recall_at_k=0.0,
                context_size_chars=750,
            ),
        ]

    def test_returns_average_metrics_and_case_count(self):
        aggregate = aggregate_retrieval(self.results, top_k=3)

        self.assertEqual(
            aggregate,
            RetrievalAggregate(
                top_k=3,
                case_count=3,
                average_recall_at_k=0.5,
                average_context_size_chars=750.0,
            ),
        )

    def test_preserves_the_evaluated_top_k(self):
        aggregate = aggregate_retrieval(self.results, top_k=5)

        self.assertEqual(aggregate.top_k, 5)

    def test_returns_zero_metrics_for_no_results(self):
        aggregate = aggregate_retrieval([], top_k=3)

        self.assertEqual(
            aggregate,
            RetrievalAggregate(
                top_k=3,
                case_count=0,
                average_recall_at_k=0.0,
                average_context_size_chars=0.0,
            ),
        )


class CompareRetrievalSettingsTests(unittest.TestCase):
    def setUp(self):
        self.cases = [
            EvaluationCase(
                question="What did I write about Kafka?",
                expected_sources=[Path("kafka.md")],
                expected_concepts=[],
            )
        ]

    def test_compares_top_k_three_and_five(self):
        database = StubVectorDatabase([])

        compare_retrieval_settings(self.cases, database, [3, 5])

        self.assertEqual(
            database.search_calls,
            [
                ("What did I write about Kafka?", 3),
                ("What did I write about Kafka?", 5),
            ],
        )

    def test_returns_one_aggregate_for_each_setting(self):
        database = StubVectorDatabase([])

        aggregates = compare_retrieval_settings(
            self.cases,
            database,
            [3, 5],
        )

        self.assertEqual(len(aggregates), 2)
        self.assertTrue(
            all(isinstance(aggregate, RetrievalAggregate) for aggregate in aggregates)
        )

    def test_preserves_the_requested_setting_order(self):
        database = StubVectorDatabase([])

        aggregates = compare_retrieval_settings(
            self.cases,
            database,
            [5, 3],
        )

        self.assertEqual([aggregate.top_k for aggregate in aggregates], [5, 3])

    def test_reports_recall_and_context_size_for_each_setting(self):
        class LimitAwareDatabase:
            def search(self, query, limit):
                records = [
                    VectorRecord(
                        note_path=Path("other.md"),
                        chunk_index=0,
                        content="An unrelated note.",
                        embedding=[],
                    ),
                    VectorRecord(
                        note_path=Path("kafka.md"),
                        chunk_index=0,
                        content="Kafka stores events in a durable log.",
                        embedding=[],
                    ),
                ]
                return records[:1] if limit == 3 else records

        aggregates = compare_retrieval_settings(
            self.cases,
            LimitAwareDatabase(),
            [3, 5],
        )

        self.assertEqual(aggregates[0].average_recall_at_k, 0.0)
        self.assertEqual(aggregates[1].average_recall_at_k, 1.0)
        self.assertLess(
            aggregates[0].average_context_size_chars,
            aggregates[1].average_context_size_chars,
        )

    def test_handles_an_empty_settings_list(self):
        database = StubVectorDatabase([])

        aggregates = compare_retrieval_settings(self.cases, database, [])

        self.assertEqual(aggregates, [])
        self.assertEqual(database.search_calls, [])
