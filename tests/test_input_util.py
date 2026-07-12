import unittest

from pk_assist.input_util import should_ask


class ShouldAskTests(unittest.TestCase):
    def test_recognizes_ask_command(self):
        self.assertTrue(should_ask("ask What did I write about Kafka?"))

    def test_recognizes_ask_command_case_insensitively(self):
        self.assertTrue(should_ask("ASK What did I write about Kafka?"))

    def test_does_not_recognize_non_ask_command(self):
        self.assertFalse(should_ask("retrieve Kafka"))


if __name__ == "__main__":
    unittest.main()
