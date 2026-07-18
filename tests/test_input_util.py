import unittest

from pk_assist.input_util import should_ask, should_evaluate


class ShouldAskTests(unittest.TestCase):
    def test_recognizes_ask_command(self):
        self.assertTrue(should_ask("ask What did I write about Kafka?"))

    def test_recognizes_ask_command_case_insensitively(self):
        self.assertTrue(should_ask("ASK What did I write about Kafka?"))

    def test_does_not_recognize_non_ask_command(self):
        self.assertFalse(should_ask("retrieve Kafka"))


class ShouldEvaluateTests(unittest.TestCase):
    def test_recognizes_evaluate_command(self):
        self.assertTrue(should_evaluate("evaluate eval/evaluation_cases.json 3"))

    def test_recognizes_evaluate_command_case_insensitively(self):
        self.assertTrue(should_evaluate("EVALUATE eval/evaluation_cases.json"))

    def test_does_not_recognize_unrelated_command(self):
        self.assertFalse(should_evaluate("retrieve Kafka"))


if __name__ == "__main__":
    unittest.main()
