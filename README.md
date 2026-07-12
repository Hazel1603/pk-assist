# Personal Knowledge Assistant

A small personal knowledge assistant for learning retrieval-augmented generation, memory architecture, context management, and retrieval evaluation.

This project follows the roadmap in `FUNCTIONAL_SPEC.md`. It builds on the earlier AI CLI Assistant described in `PREVIOUS_PROJECTS.md`, so that file should be passed in as background context alongside `FUNCTIONAL_SPEC.md`.

## Goal

The assistant will help answer questions about a folder of personal notes. It should retrieve relevant notes or chunks, summarize the answer, and cite which source notes were used.

The central learning question for this project is:

```text
What information should be placed into the model's context?
```

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

v0.6 is implemented. The app can load notes from a folder, search loaded notes with simple keyword matching, split loaded notes into smaller text chunks, generate fake embeddings, store embedded chunks in a local in-memory vector database, and retrieve relevant chunks for a user question.

Implemented features:

- Load notes from a folder.
- Read `.md`, `.txt`, `.MD`, and `.TXT` files.
- Recursively scan nested folders.
- Sort loaded paths for deterministic output.
- Skip files that cannot be read as UTF-8.
- Show a friendly message when no notes folder is provided or the folder does not exist.
- Print the number of loaded notes.
- Print each loaded note path.
- Search loaded notes from the CLI.
- Search note paths and note contents.
- Search case-insensitively.
- Show matching note paths.
- Show a friendly message when no notes match.
- Split loaded notes into smaller text chunks.
- Preserve the source note path for each chunk.
- Assign a stable index to each chunk.
- Skip empty chunks.
- Generate deterministic fake embeddings for chunks.
- Preserve the original chunk when creating embedded chunks.
- Store embedded chunks as vector records in a local vector database.
- Preserve the source note path, chunk index, chunk content, and embedding for each vector record.
- Retrieve relevant chunks from the local vector database.
- Convert user questions into fake embeddings for retrieval.
- Rank retrieved records by similarity score.
- Limit retrieved results to the top matching records.
- Search and retrieve from the CLI as separate commands.

Planned capabilities:

- Build compact context from retrieved chunks.
- Answer questions using constructed context.
- Show sources and citations for answers.
- Evaluate retrieval quality.
- Compare retrieval and context strategies.
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
- Memory architecture
- Short-term vs long-term memory
- Context construction and pruning
- Retrieval Recall@K
- Context relevance
- Token usage and context-cost tradeoffs

## Architecture

The assistant follows this pipeline:

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

This project should make each step visible. Retrieval, context construction, answer generation, citation, and evaluation are separate concerns so they can be tested and improved independently.

## Setup

Run the CLI with a notes folder path:

```bash
python3 -m pk_assist.cli sample_notes
```

Inside the CLI, search loaded notes:

```text
search kafka
```

Retrieve relevant chunks from the vector database:

```text
retrieve vector databases
```

You can also list loaded notes, show a note by path, or exit:

```text
list
show sample_notes/kafka.md
bye
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
- v0.7 - Build context from retrieved chunks.
- v0.8 - Answer questions using constructed context.
- v0.9 - Show sources/citations for answers.
- v0.10 - Add an evaluation dataset.
- v0.11 - Measure retrieval quality.
- v0.12 - Compare retrieval and context strategies.
- v0.13 - Add update/re-index command for changed notes.

## Evaluation Goal

The project will include a small evaluation dataset so retrieval behavior can be measured instead of guessed.

Example evaluation case:

```json
{
  "question": "What did I write about Kafka?",
  "expected_sources": ["sample_notes/kafka.md"],
  "expected_concepts": ["consumer lag", "producer throughput"]
}
```

The goal is to compare settings such as:

```text
top_k = 3
top_k = 5
top_k = 10
```

and measure:

- Retrieval Recall@K
- Context size
- Source relevance
- Answer correctness
