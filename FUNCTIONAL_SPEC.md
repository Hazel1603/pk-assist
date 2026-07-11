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
- summarizes the answer
- cites which notes were used

## You'll Learn

- embeddings
- semantic search
- vector databases
- retrieval-augmented generation
- chunking documents
- building a small personal knowledge base

## Version Management

- v0.1 — Load notes from a folder.
- v0.2 — Search notes with simple keyword matching.
- v0.3 — Split notes into chunks.
- v0.4 — Generate embeddings for chunks.
- v0.5 — Store embeddings in a local vector database.
- v0.6 — Retrieve relevant chunks for a user question.
- v0.7 — Answer questions using retrieved context.
- v0.8 — Show sources/citations for answers.
- v0.9 — Add update/re-index command for changed notes.

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
