import unittest
from contextlib import redirect_stdout
from io import StringIO

from pk_assist.print import print_answer, print_citations


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


if __name__ == "__main__":
    unittest.main()
