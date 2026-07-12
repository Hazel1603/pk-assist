import unittest
from contextlib import redirect_stdout
from io import StringIO

from pk_assist.print import print_answer


class PrintAnswerTests(unittest.TestCase):
    def test_print_answer_labels_answer_as_generated(self):
        output = StringIO()

        with redirect_stdout(output):
            print_answer("Kafka is described as an event log.")

        printed = output.getvalue()
        self.assertIn("Generated answer:", printed)
        self.assertIn("Kafka is described as an event log.", printed)


if __name__ == "__main__":
    unittest.main()
