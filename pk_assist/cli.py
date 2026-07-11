import sys
from pathlib import Path

from pk_assist.notes import load_notes
from pk_assist.print import print_loaded_notes, print_goodbye, print_note

# temporary global variable
NOTES = []


def init_app():
    global NOTES
    
    if len(sys.argv) < 2:
        print("⚯ : No notes folder passed! Skip loading...")
        print("\tUsage: python3 -m pk_assist.cli <notes-folder>")
        return

    folder_arg = sys.argv[1]
    folder = Path(folder_arg)

    if not folder.exists() or not folder.is_dir():
        print("⚯ : (｡·  v  ·｡) ? Folder does not exist or is not a directory! Skip loading...")
        return
    
    NOTES = load_notes(folder)

    print_loaded_notes(NOTES)


def should_exit(user_input):
    return user_input.lower() in {"exit", "quit", "bye"}

def should_list(user_input):
    return user_input.lower() in {"list", "list notes"}

def should_show(user_input):
    return user_input.lower().startswith("show ")

def run_cli():
    global NOTES
    try:
        while True:
            user_input = input("➤ : ") 
            if should_exit(user_input):
                print_goodbye()
                break
            if should_list(user_input):
                print_loaded_notes(NOTES)
                continue
            if should_show(user_input):
                parts = user_input.split(" ", 1)
                if len(parts) < 2:
                    print("⚯ : (｡·  v  ·｡) ? No file path provided.")
                    continue
                print_note(NOTES, parts[1])
                continue
            else:
                print("⚯ : (｡·  v  ·｡) ?")
                continue
    except (KeyboardInterrupt, EOFError):
        print_goodbye()
    
def main():
    init_app()
    run_cli()

if __name__ == "__main__":
    main()