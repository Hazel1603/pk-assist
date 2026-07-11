computer = "⚯ : "
confused = "(｡·  v  ·｡) ?"

def print_loaded_notes(notes):
    print(f"{computer}Loaded {len(notes)} notes")
    print_notes(notes)

def print_filtered_notes(notes):
    if len(notes) == 0:
        print(f"{computer}No matching notes found.")
        return

    print(f"{computer}Filtered {len(notes)} notes")
    print_notes(notes)

def print_notes(notes):
    for note in notes:
        print(f"\t- {note.path}")

def print_note(notes, path):
    for note in notes:
        if str(note.path) == path.strip():
            print(f"{note.content[:100]}...")
            return
    print(f"{computer}No note found at {path}")

def print_no_file():
    print(f"{computer}{confused} No file path provided.")

def print_idk():
    print(f"{computer}{confused}")

def print_not_folder_or_dir():
    print(f"{computer}{confused} Folder does not exist or is not a directory! Skip loading...")

def print_no_query():
    print(f"{computer}{confused} No query provided.")

def print_no_folder():
    print(f"{computer}No notes folder passed! Skip loading...")
    print("\tUsage: python3 -m pk_assist.cli <notes-folder>")

def print_chunks(chunks):
    print(f"{computer}created {len(chunks)} chunks")

def print_goodbye():
    print(f"{computer}(„• ֊ •„)੭ Adios!")
