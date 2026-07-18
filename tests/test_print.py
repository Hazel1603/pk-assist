import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from pk_assist.evaluation import EvaluationCase, EvaluationResult
from pk_assist.print import print_answer, print_citations, print_evaluation_results


class PrintAnswerTests(unittest.TestCase):
    def test_print_answer_labels_answer_as_generated(self):
        output = StringIO()

        with redirect_stdout(output):
            print_answer("Kafka is described as an event log.")

        printed = output.getvalue()
        self.assertIn("Generated answer:", printed)
        self.assertIn("Kafka is described as an event log.", printed)


class PrintCitationsTests(unittest.TestCase):
    def test_print_citations_labels_and_prints_each_citation(self):
        output = StringIO()

        with redirect_stdout(output):
            print_citations(["kafka.md#chunk-0", "agent-memory.txt#chunk-2"])

        printed = output.getvalue()
        self.assertIn("Cited:", printed)
        self.assertIn("kafka.md#chunk-0", printed)
        self.assertIn("agent-memory.txt#chunk-2", printed)

    def test_print_citations_with_no_citations_prints_only_label(self):
        output = StringIO()

        with redirect_stdout(output):
            print_citations([])

        printed = output.getvalue()
        self.assertIn("Cited:", printed)
        self.assertNotIn("\t-", printed)


class PrintEvaluationResultsTests(unittest.TestCase):
    def test_prints_plain_paths_and_context_size_label(self):
        case = EvaluationCase(
            question="What did I write about Kafka?",
            expected_sources=[Path("sample_notes/kafka.md")],
            expected_concepts=[],
        )
        result = EvaluationResult(
            case=case,
            top_k=3,
            retrieved_sources=[Path("sample_notes/kafka.md")],
            recall_at_k=1.0,
            context_size_chars=420,
        )
        output = StringIO()

        with redirect_stdout(output):
            print_evaluation_results([result])

        printed = output.getvalue()
        self.assertIn("Expected sources: sample_notes/kafka.md", printed)
        self.assertIn("Retrieved sources: sample_notes/kafka.md", printed)
        self.assertNotIn("PosixPath", printed)
        self.assertIn("Recall@3: 1.0", printed)
        self.assertIn("Context size: 420 characters", printed)
        self.assertNotIn("Context size char:", printed)


if __name__ == "__main__":
    unittest.main()
