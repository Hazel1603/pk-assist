import tempfile
import unittest
from pathlib import Path

from pk_assist.evaluation import EvaluationCase, load_evaluation_cases


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
