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

v0.12 is implemented. In addition to evaluating one retrieval setting, the app can compare multiple `top_k` settings and show their average Recall@K and constructed-context size side by side.

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
- Build compact context from retrieved chunks.
- Preserve source note path, chunk index, and chunk content in context.
- Limit constructed context with a configurable character budget.
- Answer questions using constructed context.
- Return a friendly response when no relevant context is available.
- Show citations for answers.
- Include source note path and chunk index in citations.
- Deduplicate repeated citation references.
- Include a small retrieval evaluation dataset.
- Load evaluation cases from a local JSON file.
- Represent each evaluation case with a question, expected source paths, and optional expected concepts.
- Evaluate retrieval with a configurable `top_k` value.
- Report expected and retrieved sources for every evaluation question.
- Calculate per-question and average Recall@K.
- Report per-question and average context size in characters.
- Compare two or more retrieval settings in one run.
- Report average Recall@K and context size for each compared setting.
- Make retrieval-quality and context-cost tradeoffs visible.
- Search, retrieve, ask, evaluate, and compare from the CLI as separate commands.

Planned capabilities:

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

Ask a question using retrieved context:

```text
ask What did I write about Kafka?
```

The `ask` command prints the constructed context, a generated answer, and citations such as:

```text
kafka.md#chunk-0
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

Evaluate retrieval using the included dataset and `top_k=3`:

```text
evaluate eval/evaluation_cases.json 3
```

If `top_k` is omitted, the evaluation command defaults to `3`:

```text
evaluate eval/evaluation_cases.json
```

The command prints each question's expected and retrieved sources, Recall@K,
and approximate context size, followed by averages across the dataset.

Compare two or more retrieval settings in one run:

```text
compare eval/evaluation_cases.json 3 5
```

The comparison reports average Recall@K and average context size for each
setting, making the quality-versus-context-cost tradeoff visible. More settings
can be included when needed:

```text
compare eval/evaluation_cases.json 3 5 10
```

## Evaluation Dataset

The retrieval evaluation dataset is stored at `eval/evaluation_cases.json`.
Each case includes a question, the source notes expected to be retrieved, and
optional concepts that a good answer should cover.

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

The project includes a small evaluation dataset so retrieval behavior can be measured instead of guessed.

Example evaluation case:

```json
{
  "question": "What did I write about Kafka?",
  "expected_sources": ["sample_notes/kafka.md"],
  "expected_concepts": ["distributed event streaming", "durable log", "consumer groups"]
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
