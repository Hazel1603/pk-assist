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