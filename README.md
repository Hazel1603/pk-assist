# Personal Knowledge Assistant

A small command-line project for learning how to build a retrieval-augmented personal knowledge assistant.

This repo is organized as a learning path. The `main` branch is the landing page and roadmap. Each milestone lives on its own branch so you can inspect the project one step at a time.

## Branches

| Branch | Status | What it shows |
| --- | --- | --- |
| `main` | Overview | Project roadmap and branch navigation. |
| `feature/v0.1` | Available | Load notes from a folder, recursively read `.md` and `.txt` files, and list loaded note paths. |
| `feature/v0.2` | Available | Search loaded notes with simple keyword matching across note paths and contents. |
| `feature/v0.3` | Available | Split notes into chunks for retrieval. |
| `feature/v0.4` | Available | Generate fake deterministic embeddings for note chunks. |
| `feature/v0.5` | Available | Store embeddings in a local in-memory vector database. |
| `feature/v0.6` | Planned | Retrieve relevant chunks for a user question. |
| `feature/v0.7` | Planned | Answer questions using retrieved context. |
| `feature/v0.8` | Planned | Show sources and citations for answers. |
| `feature/v0.9` | Planned | Re-index changed notes. |

## How To Navigate

Start from `main` to read the roadmap:

```bash
git checkout main
```

To view and run the first working version:

```bash
git checkout feature/v0.1
```

To view and run the keyword search version:

```bash
git checkout feature/v0.2
```

To view and run the chunking version:

```bash
git checkout feature/v0.3
```

To view and run the fake embedding version:

```bash
git checkout feature/v0.4
```

To view and run the local vector database version:

```bash
git checkout feature/v0.5
```

After switching branches, read that branch's `README.md` for setup and run instructions.

To see all local branches:

```bash
git branch
```

To return to the overview:

```bash
git checkout main
```

## Learning Roadmap

The project follows the plan in `FUNCTIONAL_SPEC.md`:

- v0.1 - Load notes from a folder.
- v0.2 - Search notes with simple keyword matching.
- v0.3 - Split notes into chunks.
- v0.4 - Generate embeddings for chunks.
- v0.5 - Store embeddings in a local vector database.
- v0.6 - Retrieve relevant chunks for a user question.
- v0.7 - Answer questions using retrieved context.
- v0.8 - Show sources/citations for answers.
- v0.9 - Add update/re-index command for changed notes.

The goal is to keep each step small and understandable before adding more retrieval-augmented generation behavior.

## Project Goal

The assistant will eventually help answer questions about a folder of personal notes. It should retrieve relevant notes or chunks, summarize the answer, and cite which source notes were used.

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

## Context Files

- `FUNCTIONAL_SPEC.md` defines the project goal, learning objectives, and version roadmap.
- `PREVIOUS_PROJECTS.md` summarizes the earlier AI CLI Assistant project and the concepts already covered.

## Possible Project Extensions

After v0.9, good optional features include:

- Watching the notes folder for changes.
- Supporting more file types.
- Better citation formatting.
- Hybrid keyword and semantic search.
- A small local web interface.
