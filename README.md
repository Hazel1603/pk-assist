# Personal Knowledge Assistant

A small personal knowledge assistant for learning retrieval-augmented generation.

This project follows the roadmap in `FUNCTIONAL_SPEC.md`. It builds on the earlier AI CLI Assistant described in `PREVIOUS_PROJECTS.md`, so that file should be passed in as background context alongside `FUNCTIONAL_SPEC.md`.

## Goal

The assistant will help answer questions about a folder of personal notes. It should retrieve relevant notes or chunks, summarize the answer, and cite which source notes were used.

Example questions:

```text
What did I write about Kafka?
```

```text
Summarize my notes on agent memory.
```

```text
Find notes related to vector databases.
```

## Current Status

v0.1 is implemented. The app can load notes from a folder, print how many notes were loaded, and list each loaded note path.

Implemented v0.1 features:

- Load notes from a folder.
- Read `.md`, `.txt`, `.MD`, and `.TXT` files.
- Recursively scan nested folders.
- Sort loaded paths for deterministic output.
- Skip files that cannot be read as UTF-8.
- Show a friendly message when no notes folder is provided or the folder does not exist.
- Print the number of loaded notes.
- Print each loaded note path.

Planned capabilities:

- Search notes with simple keyword matching.
- Split notes into chunks.
- Generate embeddings for chunks.
- Store embeddings in a local vector database.
- Retrieve relevant chunks for a user question.
- Answer questions using retrieved context.
- Show sources and citations for answers.
- Re-index changed notes.

## Context Files

- `FUNCTIONAL_SPEC.md` defines the project goal, learning objectives, and version roadmap.
- `PREVIOUS_PROJECTS.md` summarizes the earlier AI CLI Assistant project and the concepts already covered.

## You'll Learn

- Embeddings
- Semantic search
- Vector databases
- Retrieval-augmented generation
- Document chunking
- Building a small personal knowledge base

## Setup

Run the v0.1 CLI with a notes folder path:

```bash
python3 -m pk_assist.cli sample_notes
```

Run the tests:

```bash
python3 -m unittest discover
```

## Project Roadmap

- v0.1 - Load notes from a folder.
- v0.2 - Search notes with simple keyword matching.
- v0.3 - Split notes into chunks.
- v0.4 - Generate embeddings for chunks.
- v0.5 - Store embeddings in a local vector database.
- v0.6 - Retrieve relevant chunks for a user question.
- v0.7 - Answer questions using retrieved context.
- v0.8 - Show sources/citations for answers.
- v0.9 - Add update/re-index command for changed notes.
