# Personal Knowledge Assistant

Difficulty: ★★☆☆☆

## Description

Use `PREVIOUS_PROJECTS.md` as context when working on this project. `PREVIOUS_PROJECTS.md` describes the earlier AI CLI Assistant project and should be passed in as background context so the Personal Knowledge Assistant can build on concepts the user has already covered.

User:

- "What did I write about Kafka?"
- "Summarize my notes on agent memory."
- "Find notes related to vector databases."

Agent:

- searches a folder of notes
- retrieves relevant documents or chunks
- ranks and selects the most useful context
- builds a compact context block for the model
- summarizes the answer
- cites which notes were used

This project is not only about adding a vector database. It is a learning lab for the question:

> What information should be placed into the model's context?

The intended pipeline is:

```text
User Question
      ↓
Query Processing
      ↓
Document Retrieval
      ↓
Ranking
      ↓
Context Construction
      ↓
LLM Answer
      ↓
Sources and Evaluation
```

## You'll Learn

- embeddings
- semantic search
- vector databases
- retrieval-augmented generation
- chunking documents
- building a small personal knowledge base
- memory architecture
- short-term vs long-term memory
- context construction and pruning
- retrieval evaluation
- Recall@K
- context relevance
- token usage and context-cost tradeoffs

## Version Management

- v0.1 — Load notes from a folder.
- v0.2 — Search notes with simple keyword matching.
- v0.3 — Split notes into chunks.
- v0.4 — Generate embeddings for chunks.
- v0.5 — Store embeddings in a local vector database.
- v0.6 — Retrieve relevant chunks for a user question.
- v0.7 — Build context from retrieved chunks.
- v0.8 — Answer questions using constructed context.
- v0.9 — Show sources/citations for answers.
- v0.10 — Add an evaluation dataset.
- v0.11 — Measure retrieval quality.
- v0.12 — Compare retrieval and context strategies.
- v0.13 — Add update/re-index command for changed notes.

## Current Implementation Status

v0.8 is implemented. The app can now retrieve relevant chunks, construct a compact context block from them, and answer a user question using that constructed context. The CLI keeps retrieval/context inspection separate from generated answers, and answer generation is covered by tests that use a fake or stubbed model boundary.

## v0.1 Acceptance Criteria

- User can pass a folder path from the command line.
- App recursively loads `.md` and `.txt` files.
- App prints the number of loaded notes.
- App prints each loaded note path.
- Loader is covered by basic tests.

## v0.2 Acceptance Criteria

- User can search loaded notes from the CLI.
- Search checks note path and note content.
- Search is case-insensitive.
- App prints matching note paths.
- App shows a friendly message when no notes match.
- Search behavior is covered by basic tests.

## v0.3 Acceptance Criteria

- App can split a loaded note into smaller text chunks.
- Each chunk preserves the source note path.
- Each chunk has a stable chunk index.
- Empty notes produce no chunks.
- Long notes can produce multiple chunks.
- Chunking behavior is covered by basic tests.

## v0.4 Acceptance Criteria

- App can generate a fake embedding for a text chunk.
- Fake embeddings are deterministic for the same text input.
- Each embedding is represented as a list of floats.
- Each embedded chunk preserves the original chunk.
- Empty chunk lists produce no embedded chunks.
- Embedding behavior is covered by basic tests.

## v0.5 Acceptance Criteria

- App can create a local vector database.
- App can store embedded chunks in the local vector database.
- Each stored vector record preserves the source note path.
- Each stored vector record preserves the source chunk index.
- Each stored vector record preserves the chunk content.
- Each stored vector record preserves the chunk embedding.
- Empty embedded chunk lists store zero vector records.
- Vector database storage behavior is covered by basic tests.

## v0.6 Acceptance Criteria

- User can retrieve relevant chunks from the CLI.
- App can retrieve relevant chunks for a user question.
- The CLI passes only the user question text into retrieval, not the command name.
- User questions are converted into fake embeddings using the existing embedding function.
- Retrieval compares the question embedding against stored vector records.
- Retrieval returns the most relevant vector records first.
- Retrieval supports limiting the number of returned records.
- Empty user questions return no retrieved records.
- Empty vector databases return no retrieved records.
- Retrieved records preserve the source note path, chunk index, chunk content, and embedding.
- Retrieval behavior is covered by basic tests.

## v0.7 Acceptance Criteria

- App can build a context block from retrieved chunks.
- Context includes source note path, chunk index, and chunk content.
- Context preserves retrieval ranking order.
- Context supports a configurable maximum character or token budget.
- Context excludes chunks that do not fit within the configured budget.
- Empty retrieval results produce an empty context.
- Context construction behavior is covered by basic tests.

## v0.8 Acceptance Criteria

- App can answer a user question using the constructed context.
- App clearly distinguishes between retrieved context and generated answer.
- App gives a friendly response when no relevant context is available.
- App avoids claiming information that is not present in the provided context.
- Answer generation behavior is covered by basic tests using a fake or stubbed model.

## v0.9 Acceptance Criteria

- App shows which source notes were used to answer a question.
- Citations include source note path and chunk index.
- Duplicate source references are displayed cleanly.
- Answers with no retrieved context show no citations.
- Citation behavior is covered by basic tests.

## v0.10 Acceptance Criteria

- Project includes a small evaluation dataset for retrieval questions.
- Each evaluation case includes a user question.
- Each evaluation case includes expected source note paths.
- Each evaluation case can include expected concepts.
- Evaluation cases can be loaded from a local file.
- Evaluation dataset loading is covered by basic tests.

## v0.11 Acceptance Criteria

- App can run retrieval against every evaluation question.
- App can calculate Retrieval Recall@K for expected source notes.
- App reports per-question retrieval results.
- App reports aggregate retrieval metrics across the evaluation dataset.
- App reports the approximate size of the retrieved context.
- Retrieval evaluation behavior is covered by basic tests.

## v0.12 Acceptance Criteria

- User can compare at least two retrieval settings, such as `top_k=3` and `top_k=5`.
- App reports retrieval metrics for each setting.
- App reports approximate context size for each setting.
- App makes quality vs context-cost tradeoffs visible.
- Strategy comparison behavior is covered by basic tests.

## v0.13 Acceptance Criteria

- App can re-index notes after files are added, changed, or deleted.
- Re-indexing updates stored vector records for changed notes.
- Re-indexing removes stored vector records for deleted notes.
- Re-indexing preserves deterministic behavior for unchanged notes.
- Re-indexing behavior is covered by basic tests.
