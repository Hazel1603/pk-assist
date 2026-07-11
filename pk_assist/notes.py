from dataclasses import dataclass
from pathlib import Path

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
