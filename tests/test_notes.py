# AI-generated tests for the v0.1 note loader acceptance criteria.

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from pk_assist.notes import Note, load_notes, search_notes


class LoadNotesTests(unittest.TestCase):
    def test_loads_markdown_and_text_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            markdown_note = folder / "kafka.md"
            text_note = folder / "agent-memory.txt"

            markdown_note.write_text("# Kafka\nEvents and streams", encoding="utf-8")
            text_note.write_text("Agent memory notes", encoding="utf-8")

            notes = load_notes(folder)
            loaded_paths = {note.path for note in notes}

            self.assertEqual(len(notes), 2)
            self.assertIn(markdown_note, loaded_paths)
            self.assertIn(text_note, loaded_paths)

    def test_loads_uppercase_markdown_and_text_extensions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            markdown_note = folder / "kafka.MD"
            text_note = folder / "agent-memory.TXT"

            markdown_note.write_text("# Kafka", encoding="utf-8")
            text_note.write_text("Agent memory notes", encoding="utf-8")

            notes = load_notes(folder)
            loaded_paths = {note.path for note in notes}

            self.assertEqual(len(notes), 2)
            self.assertIn(markdown_note, loaded_paths)
            self.assertIn(text_note, loaded_paths)

    def test_recursively_loads_notes_in_subfolders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            nested_folder = folder / "research"
            nested_folder.mkdir()
            nested_note = nested_folder / "chunking.txt"

            nested_note.write_text("Chunking notes", encoding="utf-8")

            notes = load_notes(folder)

            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].path, nested_note)

    def test_ignores_unsupported_file_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            supported_note = folder / "vector-databases.md"
            unsupported_file = folder / "image.png"

            supported_note.write_text("# Vector databases", encoding="utf-8")
            unsupported_file.write_text("not a note", encoding="utf-8")

            notes = load_notes(folder)
            loaded_paths = {note.path for note in notes}

            self.assertEqual(len(notes), 1)
            self.assertIn(supported_note, loaded_paths)
            self.assertNotIn(unsupported_file, loaded_paths)

    def test_ignores_directories_with_supported_suffixes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            fake_note_folder = folder / "not-a-note.md"
            real_note = folder / "real-note.md"

            fake_note_folder.mkdir()
            real_note.write_text("# Real note", encoding="utf-8")

            notes = load_notes(folder)

            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].path, real_note)

    def test_returns_notes_in_sorted_path_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            second_note = folder / "b-note.md"
            first_note = folder / "a-note.md"

            second_note.write_text("Second", encoding="utf-8")
            first_note.write_text("First", encoding="utf-8")

            notes = load_notes(folder)

            self.assertEqual(
                [note.path for note in notes],
                [first_note, second_note],
            )

    def test_skips_files_that_are_not_valid_utf8(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            valid_note = folder / "valid.md"
            invalid_note = folder / "invalid.md"

            valid_note.write_text("# Valid", encoding="utf-8")
            invalid_note.write_bytes(b"\xff\xfe\xfa")

            output = StringIO()
            with redirect_stdout(output):
                notes = load_notes(folder)

            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].path, valid_note)
            self.assertIn("Could not read file as UTF-8", output.getvalue())

    def test_sets_title_and_content_from_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            note_path = folder / "kafka.md"
            note_content = "# Kafka\nKafka is a durable event log."

            note_path.write_text(note_content, encoding="utf-8")

            notes = load_notes(folder)

            self.assertEqual(notes[0].title, "kafka.md")
            self.assertEqual(notes[0].content, note_content)


class SearchNotesTests(unittest.TestCase):
    def test_finds_notes_with_query_in_content(self):
        notes = [
            Note(
                path=Path("kafka.md"),
                title="kafka.md",
                content="Kafka is a durable event log.",
            ),
            Note(
                path=Path("agent-memory.txt"),
                title="agent-memory.txt",
                content="Agents can keep useful context over time.",
            ),
        ]

        results = search_notes(notes, "event log")

        self.assertEqual(results, [notes[0]])

    def test_finds_notes_with_query_in_title(self):
        notes = [
            Note(
                path=Path("vector-databases.md"),
                title="vector-databases.md",
                content="Stores embeddings for semantic search.",
            ),
            Note(
                path=Path("chunking.txt"),
                title="chunking.txt",
                content="Split long documents into smaller pieces.",
            ),
        ]

        results = search_notes(notes, "vector")

        self.assertEqual(results, [notes[0]])

    def test_search_is_case_insensitive(self):
        notes = [
            Note(
                path=Path("agent-memory.txt"),
                title="agent-memory.txt",
                content="Agent Memory helps preserve context.",
            ),
        ]

        results = search_notes(notes, "memory")

        self.assertEqual(results, notes)

    def test_returns_empty_list_when_no_notes_match(self):
        notes = [
            Note(
                path=Path("kafka.md"),
                title="kafka.md",
                content="Kafka is a durable event log.",
            ),
        ]

        results = search_notes(notes, "pineapple")

        self.assertEqual(results, [])

    def test_returns_empty_list_for_empty_query(self):
        notes = [
            Note(
                path=Path("kafka.md"),
                title="kafka.md",
                content="Kafka is a durable event log.",
            ),
        ]

        results = search_notes(notes, "")

        self.assertEqual(results, [])

    def test_returns_empty_list_for_whitespace_query(self):
        notes = [
            Note(
                path=Path("kafka.md"),
                title="kafka.md",
                content="Kafka is a durable event log.",
            ),
        ]

        results = search_notes(notes, "   ")

        self.assertEqual(results, [])
        
    def test_finds_notes_with_query_in_path_folder(self):
        notes = [
            Note(
                path=Path("research/chunking.txt"),
                title="chunking.txt",
                content="Split long documents into smaller pieces.",
            ),
        ]

        results = search_notes(notes, "research")

        self.assertEqual(results, notes)


if __name__ == "__main__":
    unittest.main()
