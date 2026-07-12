# AI-generated tests for the v0.1 note loader acceptance criteria.

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from pk_assist.notes import (
    Chunk,
    EmbeddedChunk,
    LocalVectorDatabase,
    Note,
    VectorRecord,
    answer_question,
    build_citations,
    build_context,
    build_context_result,
    chunk_note,
    embed_chunks,
    embed_text,
    load_notes,
    search_notes,
)


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

    def test_returns_empty_list_when_folder_has_no_notes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            unsupported_file = folder / "image.png"

            unsupported_file.write_text("not a note", encoding="utf-8")

            notes = load_notes(folder)

            self.assertEqual(notes, [])


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

    def test_search_strips_surrounding_whitespace(self):
        notes = [
            Note(
                path=Path("kafka.md"),
                title="kafka.md",
                content="Kafka is a durable event log.",
            ),
        ]

        results = search_notes(notes, "   kafka   ")

        self.assertEqual(results, notes)
        
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


class ChunkNoteTests(unittest.TestCase):
    def test_splits_note_into_one_chunk_when_content_is_short(self):
        note = Note(
            path=Path("kafka.md"),
            title="kafka.md",
            content="Kafka is a durable event log.",
        )

        chunks = chunk_note(note, max_chars=100)

        self.assertEqual(
            chunks,
            [
                Chunk(
                    note_path=Path("kafka.md"),
                    chunk_index=0,
                    content="Kafka is a durable event log.",
                )
            ],
        )

    def test_splits_long_note_into_multiple_chunks(self):
        note = Note(
            path=Path("agent-memory.txt"),
            title="agent-memory.txt",
            content="First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
        )

        chunks = chunk_note(note, max_chars=30)

        self.assertEqual(len(chunks), 3)
        self.assertEqual([chunk.chunk_index for chunk in chunks], [0, 1, 2])
        self.assertEqual([chunk.content for chunk in chunks], [
            "First paragraph.",
            "Second paragraph.",
            "Third paragraph.",
        ])

    def test_splits_single_long_paragraph_into_multiple_chunks(self):
        note = Note(
            path=Path("long.md"),
            title="long.md",
            content="abcdefghij",
        )

        chunks = chunk_note(note, max_chars=4)

        self.assertEqual(
            chunks,
            [
                Chunk(
                    note_path=Path("long.md"),
                    chunk_index=0,
                    content="abcd",
                ),
                Chunk(
                    note_path=Path("long.md"),
                    chunk_index=1,
                    content="efgh",
                ),
                Chunk(
                    note_path=Path("long.md"),
                    chunk_index=2,
                    content="ij",
                ),
            ],
        )

    def test_chunk_preserves_source_note_path(self):
        note = Note(
            path=Path("research/chunking.txt"),
            title="chunking.txt",
            content="Split long documents into smaller pieces.",
        )

        chunks = chunk_note(note, max_chars=100)

        self.assertEqual(chunks[0].note_path, Path("research/chunking.txt"))

    def test_empty_note_returns_no_chunks(self):
        note = Note(
            path=Path("empty.md"),
            title="empty.md",
            content="",
        )

        chunks = chunk_note(note)

        self.assertEqual(chunks, [])

    def test_whitespace_only_note_returns_no_chunks(self):
        note = Note(
            path=Path("empty.md"),
            title="empty.md",
            content="   \n\n   ",
        )

        chunks = chunk_note(note)

        self.assertEqual(chunks, [])


class EmbedTextTests(unittest.TestCase):
    def test_creates_fake_embedding_from_text_features(self):
        embedding = embed_text("Aa ee i o u")

        self.assertEqual(
            embedding,
            [
                11.0,  # character count
                5.0,   # word count
                2.0,   # a count
                2.0,   # e count
                1.0,   # i count
                1.0,   # o count
                1.0,   # u count
            ],
        )

    def test_embedding_is_deterministic_for_same_text(self):
        first_embedding = embed_text("Kafka stores events")
        second_embedding = embed_text("Kafka stores events")

        self.assertEqual(first_embedding, second_embedding)

    def test_embedding_values_are_floats(self):
        embedding = embed_text("Vector databases store embeddings.")

        self.assertTrue(all(isinstance(value, float) for value in embedding))

    def test_embedding_has_stable_length(self):
        self.assertEqual(len(embed_text("Kafka")), 7)
        self.assertEqual(len(embed_text("Vector databases")), 7)


class EmbedChunksTests(unittest.TestCase):
    def test_embeds_each_chunk_and_preserves_original_chunk(self):
        chunks = [
            Chunk(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
            ),
            Chunk(
                note_path=Path("vector-databases.md"),
                chunk_index=1,
                content="Vector databases store embeddings.",
            ),
        ]

        embedded_chunks = embed_chunks(chunks)

        self.assertEqual(
            embedded_chunks,
            [
                EmbeddedChunk(
                    chunk=chunks[0],
                    embedding=embed_text(chunks[0].content),
                ),
                EmbeddedChunk(
                    chunk=chunks[1],
                    embedding=embed_text(chunks[1].content),
                ),
            ],
        )

    def test_returns_empty_list_when_there_are_no_chunks(self):
        embedded_chunks = embed_chunks([])

        self.assertEqual(embedded_chunks, [])


class LocalVectorDatabaseTests(unittest.TestCase):
    def test_stores_embedded_chunks_as_vector_records(self):
        chunks = [
            Chunk(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
            ),
            Chunk(
                note_path=Path("vector-databases.md"),
                chunk_index=1,
                content="Vector databases store embeddings.",
            ),
        ]
        embedded_chunks = [
            EmbeddedChunk(
                chunk=chunks[0],
                embedding=[1.0, 2.0, 3.0],
            ),
            EmbeddedChunk(
                chunk=chunks[1],
                embedding=[4.0, 5.0, 6.0],
            ),
        ]
        database = LocalVectorDatabase()

        database.add_many(embedded_chunks)

        self.assertEqual(
            database.records,
            [
                VectorRecord(
                    note_path=Path("kafka.md"),
                    chunk_index=0,
                    content="Kafka stores events.",
                    embedding=[1.0, 2.0, 3.0],
                ),
                VectorRecord(
                    note_path=Path("vector-databases.md"),
                    chunk_index=1,
                    content="Vector databases store embeddings.",
                    embedding=[4.0, 5.0, 6.0],
                ),
            ],
        )

    def test_add_stores_one_embedded_chunk(self):
        chunk = Chunk(
            note_path=Path("agent-memory.txt"),
            chunk_index=2,
            content="Agents can remember useful context.",
        )
        embedded_chunk = EmbeddedChunk(
            chunk=chunk,
            embedding=[7.0, 8.0, 9.0],
        )
        database = LocalVectorDatabase()

        database.add(embedded_chunk)

        self.assertEqual(
            database.records,
            [
                VectorRecord(
                    note_path=Path("agent-memory.txt"),
                    chunk_index=2,
                    content="Agents can remember useful context.",
                    embedding=[7.0, 8.0, 9.0],
                )
            ],
        )

    def test_count_returns_number_of_stored_vector_records(self):
        chunk = Chunk(
            note_path=Path("kafka.md"),
            chunk_index=0,
            content="Kafka stores events.",
        )
        embedded_chunk = EmbeddedChunk(
            chunk=chunk,
            embedding=[1.0, 2.0, 3.0],
        )
        database = LocalVectorDatabase()

        database.add(embedded_chunk)

        self.assertEqual(database.count(), 1)

    def test_empty_embedded_chunk_list_stores_zero_records(self):
        database = LocalVectorDatabase()

        database.add_many([])

        self.assertEqual(database.records, [])
        self.assertEqual(database.count(), 0)

    def test_retrieves_records_for_a_user_question(self):
        chunk = Chunk(
            note_path=Path("kafka.md"),
            chunk_index=0,
            content="Kafka stores events.",
        )
        embedded_chunk = EmbeddedChunk(
            chunk=chunk,
            embedding=[1.0, 2.0, 3.0],
        )
        database = LocalVectorDatabase()
        database.add(embedded_chunk)

        results = database.search("Kafka")

        self.assertEqual(
            results,
            [
                VectorRecord(
                    note_path=Path("kafka.md"),
                    chunk_index=0,
                    content="Kafka stores events.",
                    embedding=[1.0, 2.0, 3.0],
                )
            ],
        )

    def test_retrieval_returns_most_relevant_records_first(self):
        less_relevant_chunk = Chunk(
            note_path=Path("low-score.md"),
            chunk_index=0,
            content="Low scoring chunk.",
        )
        more_relevant_chunk = Chunk(
            note_path=Path("high-score.md"),
            chunk_index=0,
            content="High scoring chunk.",
        )
        database = LocalVectorDatabase()
        database.add(
            EmbeddedChunk(
                chunk=less_relevant_chunk,
                embedding=[0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            )
        )
        database.add(
            EmbeddedChunk(
                chunk=more_relevant_chunk,
                embedding=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            )
        )

        results = database.search("Kafka")

        self.assertEqual(
            [record.note_path for record in results],
            [Path("high-score.md"), Path("low-score.md")],
        )

    def test_retrieval_supports_limiting_returned_records(self):
        first_chunk = Chunk(
            note_path=Path("first.md"),
            chunk_index=0,
            content="First chunk.",
        )
        second_chunk = Chunk(
            note_path=Path("second.md"),
            chunk_index=0,
            content="Second chunk.",
        )
        database = LocalVectorDatabase()
        database.add(
            EmbeddedChunk(
                chunk=first_chunk,
                embedding=[10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0],
            )
        )
        database.add(
            EmbeddedChunk(
                chunk=second_chunk,
                embedding=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            )
        )

        results = database.search("Kafka", limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].note_path, Path("first.md"))

    def test_empty_user_question_returns_no_retrieved_records(self):
        chunk = Chunk(
            note_path=Path("kafka.md"),
            chunk_index=0,
            content="Kafka stores events.",
        )
        database = LocalVectorDatabase()
        database.add(
            EmbeddedChunk(
                chunk=chunk,
                embedding=[1.0, 2.0, 3.0],
            )
        )

        self.assertEqual(database.search(""), [])
        self.assertEqual(database.search("   "), [])

    def test_empty_database_returns_no_retrieved_records(self):
        database = LocalVectorDatabase()

        results = database.search("Kafka")

        self.assertEqual(results, [])


class BuildContextTests(unittest.TestCase):
    def test_empty_retrieval_results_produce_empty_context(self):
        context = build_context([])

        self.assertEqual(context, "")

    def test_context_includes_source_path_chunk_index_and_content(self):
        records = [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
                embedding=[1.0, 2.0, 3.0],
            )
        ]

        context = build_context(records)

        self.assertIn("Source: kafka.md", context)
        self.assertIn("Chunk: 0", context)
        self.assertIn("Kafka stores events.", context)

    def test_context_preserves_retrieval_ranking_order(self):
        records = [
            VectorRecord(
                note_path=Path("first.md"),
                chunk_index=0,
                content="First retrieved chunk.",
                embedding=[1.0],
            ),
            VectorRecord(
                note_path=Path("second.md"),
                chunk_index=1,
                content="Second retrieved chunk.",
                embedding=[2.0],
            ),
        ]

        context = build_context(records)

        self.assertLess(
            context.index("Source: first.md"),
            context.index("Source: second.md"),
        )

    def test_context_respects_max_character_budget(self):
        first_record = VectorRecord(
            note_path=Path("first.md"),
            chunk_index=0,
            content="Short.",
            embedding=[1.0],
        )
        second_record = VectorRecord(
            note_path=Path("second.md"),
            chunk_index=1,
            content="This chunk is too long to fit.",
            embedding=[2.0],
        )
        first_context = build_context([first_record])

        context = build_context(
            [first_record, second_record],
            max_chars=len(first_context),
        )

        self.assertEqual(context, first_context)
        self.assertNotIn("Source: second.md", context)

    def test_context_excludes_first_chunk_when_it_exceeds_budget(self):
        records = [
            VectorRecord(
                note_path=Path("large.md"),
                chunk_index=0,
                content="This chunk is too large for the budget.",
                embedding=[1.0],
            )
        ]

        context = build_context(records, max_chars=10)

        self.assertEqual(context, "")


class BuildContextResultTests(unittest.TestCase):
    def test_empty_retrieval_results_produce_empty_context_result(self):
        context_result = build_context_result([])

        self.assertEqual(context_result.text, "")
        self.assertEqual(context_result.records, [])

    def test_context_result_includes_text_and_used_records(self):
        record = VectorRecord(
            note_path=Path("kafka.md"),
            chunk_index=0,
            content="Kafka stores events.",
            embedding=[1.0],
        )

        context_result = build_context_result([record])

        self.assertIn("Source: kafka.md", context_result.text)
        self.assertIn("Chunk: 0", context_result.text)
        self.assertIn("Kafka stores events.", context_result.text)
        self.assertEqual(context_result.records, [record])

    def test_context_result_records_preserve_context_budget_order(self):
        first_record = VectorRecord(
            note_path=Path("first.md"),
            chunk_index=0,
            content="Short.",
            embedding=[1.0],
        )
        second_record = VectorRecord(
            note_path=Path("second.md"),
            chunk_index=1,
            content="This chunk is too long to fit.",
            embedding=[2.0],
        )
        first_context = build_context([first_record])

        context_result = build_context_result(
            [first_record, second_record],
            max_chars=len(first_context),
        )

        self.assertEqual(context_result.text, first_context)
        self.assertEqual(context_result.records, [first_record])

    def test_context_result_excludes_first_record_when_it_exceeds_budget(self):
        record = VectorRecord(
            note_path=Path("large.md"),
            chunk_index=0,
            content="This chunk is too large for the budget.",
            embedding=[1.0],
        )

        context_result = build_context_result([record], max_chars=10)

        self.assertEqual(context_result.text, "")
        self.assertEqual(context_result.records, [])


class BuildCitationsTests(unittest.TestCase):
    def test_empty_retrieval_results_produce_no_citations(self):
        citations = build_citations([])

        self.assertEqual(citations, [])

    def test_citations_include_source_path_and_chunk_index(self):
        records = [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
                embedding=[1.0],
            ),
            VectorRecord(
                note_path=Path("agent-memory.txt"),
                chunk_index=2,
                content="Agents can remember useful context.",
                embedding=[2.0],
            ),
        ]

        citations = build_citations(records)

        self.assertEqual(
            citations,
            [
                "kafka.md#chunk-0",
                "agent-memory.txt#chunk-2",
            ],
        )

    def test_duplicate_source_references_are_displayed_once(self):
        records = [
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events.",
                embedding=[1.0],
            ),
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=0,
                content="Kafka stores events again.",
                embedding=[2.0],
            ),
            VectorRecord(
                note_path=Path("kafka.md"),
                chunk_index=1,
                content="Kafka has partitions.",
                embedding=[3.0],
            ),
        ]

        citations = build_citations(records)

        self.assertEqual(
            citations,
            [
                "kafka.md#chunk-0",
                "kafka.md#chunk-1",
            ],
        )


class FakeModel:
    def __init__(self, response="Generated answer."):
        self.response = response
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


class FailingModel:
    def generate(self, prompt: str) -> str:
        raise AssertionError("Model should not be called.")


class AnswerQuestionTests(unittest.TestCase):
    def test_empty_context_returns_friendly_response(self):
        answer = answer_question(
            "What did I write about Kafka?",
            "",
            FailingModel(),
        )

        self.assertEqual(
            answer,
            "I could not find relevant context to answer that question.",
        )

    def test_whitespace_context_returns_friendly_response(self):
        answer = answer_question(
            "What did I write about Kafka?",
            "   \n\n   ",
            FailingModel(),
        )

        self.assertEqual(
            answer,
            "I could not find relevant context to answer that question.",
        )

    def test_answer_uses_model_response_when_context_is_available(self):
        model = FakeModel(response="Kafka is described as a durable event log.")

        answer = answer_question(
            "What did I write about Kafka?",
            "Source: kafka.md\nChunk: 0\nContent:\nKafka is a durable event log.",
            model,
        )

        self.assertEqual(answer, "Kafka is described as a durable event log.")

    def test_prompt_includes_question_and_context(self):
        model = FakeModel()
        question = "What did I write about Kafka?"
        context = "Source: kafka.md\nChunk: 0\nContent:\nKafka stores events."

        answer_question(question, context, model)

        self.assertEqual(len(model.prompts), 1)
        self.assertIn(f"Question:\n{question}", model.prompts[0])
        self.assertIn(f"Context:\n{context}", model.prompts[0])

    def test_prompt_requires_answer_to_use_only_provided_context(self):
        model = FakeModel()

        answer_question(
            "What did I write about Kafka?",
            "Source: kafka.md\nChunk: 0\nContent:\nKafka stores events.",
            model,
        )

        self.assertIn("using only the context", model.prompts[0].lower())
        self.assertIn("if the context does not contain the answer", model.prompts[0].lower())


if __name__ == "__main__":
    unittest.main()
