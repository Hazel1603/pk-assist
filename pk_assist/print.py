def print_loaded_notes(notes):
    print(f"⚯ : Loaded {len(notes)} notes")

    for note in notes:
        print(f"- {note.path}")

def print_note(notes, path):
    for note in notes:
        if str(note.path) == path.strip():
            print(f"{note.content[:100]}...")
            return
    print(f"⚯ : No note found at {path}")

def print_goodbye():
    print(f"⚯ : („• ֊ •„)੭ Adios!")