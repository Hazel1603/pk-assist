from dataclasses import dataclass
from pathlib import Path

#################### note implementation ####################
@dataclass
class Note:
    path: Path
    title: str
    content: str

def load_notes(folder: Path) -> list[Note]:
    notes = []

    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix in [".md", ".txt", ".MD", ".TXT"]:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                print(f"⚯ : Could not read file as UTF-8: {path}")
                continue

            notes.append(
                Note(
                    path=path,
                    title=path.name,
                    content=content
                )
            )
    return notes

def search_notes(notes: list[Note], query: str) -> list[Note]:
    filtered = []

    query_lower = query.strip().lower()

    if query_lower == "":
        return filtered

    for note in notes:
        path_contains_query = query_lower in str(note.path).lower()
        content_contains_query = query_lower in note.content.lower()

        if path_contains_query or content_contains_query:
            filtered.append(note)

    return filtered


#################### chunk implementation ####################
@dataclass
class Chunk:
    note_path: Path
    chunk_index: int
    content: str

def chunk_notes(notes: list[Note]) -> list[Chunk]:
    chunks = []
    for note in notes: 
        chunks.extend(chunk_note(note))
    return chunks

def chunk_note(note: Note, max_chars: int = 500) -> list[Chunk]:
    chunks = []
    content = note.content.strip()
    note_path = note.path
    chunk_index = 0

    if content == "":
        return chunks

    paragraphs = content.split("\n\n") # split by new line

    for paragraph in paragraphs: 
        for start in range(0, len(paragraph), max_chars):
            chunk_content = paragraph[start:start + max_chars].strip() # split by max_chars
            if chunk_content == "":
                continue
            chunks.append(
                Chunk(
                    note_path = note_path, 
                    chunk_index = chunk_index,
                    content = chunk_content
                )
            )
            chunk_index += 1
    return chunks

#################### embeddedchunk implementation ####################
@dataclass
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]

def embed_chunks(chunks: list[Chunk]) -> list[EmbeddedChunk]:
    embedded_chunks = []

    for chunk in chunks: 
        embedded_chunks.append(
            EmbeddedChunk(
                chunk = chunk, 
                embedding = embed_text(chunk.content)
            )
        )

    return embedded_chunks

def embed_text(text: str) -> list[float]:
    # to be replaced later
    normalized = text.lower()

    return [
        float(len(text)),
        float(len(text.split())),
        float(normalized.count("a")),
        float(normalized.count("e")),
        float(normalized.count("i")),
        float(normalized.count("o")),
        float(normalized.count("u")),
    ]



#################### vectorrecord implementation ####################
@dataclass
class VectorRecord:
    note_path: Path
    chunk_index: int
    content: str
    embedding: list[float]

    def to_context_string(self) -> str:
        return (
            f"Source: {self.note_path}\n"
            f"Chunk: {self.chunk_index}\n"
            f"Content:\n"
            f"{self.content}\n\n"
        )

class LocalVectorDatabase:
    def __init__(self):
        self.records = []

    def add(self, embedded_chunk: EmbeddedChunk):
        self.records.append(
            VectorRecord(
                note_path=embedded_chunk.chunk.note_path,
                chunk_index=embedded_chunk.chunk.chunk_index,
                content=embedded_chunk.chunk.content,
                embedding=embedded_chunk.embedding,
            )
        )

    def add_many(self, embedded_chunks: list[EmbeddedChunk]):
        for embedded_chunk in embedded_chunks:
            self.add(embedded_chunk)

    def count(self) -> int:
        return len(self.records)
    
    def search(self, query: str, limit: int = 3) -> list[VectorRecord]:
        if query.strip() == "":
            return []

        query_embedding = embed_text(query)
        scored_records = []

        for record in self.records:
            score = dot_product(query_embedding, record.embedding)
            scored_records.append((score, record))

        scored_records.sort(reverse=True, key=lambda item: item[0])

        return [record for score, record in scored_records[:limit]]



#################### context methods ####################
def build_context(records: list[VectorRecord], max_chars: int = 2000) -> str:
    context = ""
    for record in records:
        record_string = record.to_context_string()
        if len(context) + len(record_string) <= max_chars:
            context += record_string
        else: 
            break
    return context


def answer_question(question: str, context: str, model) -> str:
    if context.strip() == "":
        return "I could not find relevant context to answer that question."

    prompt = (
        "Answer the question using only the context below.\n"
        "If the context does not contain the answer, say so.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}"
    )

    return model.generate(prompt)


#################### helper methods ####################
def dot_product(first: list[float], second: list[float]) -> float:
    return sum(a * b for a, b in zip(first, second))
