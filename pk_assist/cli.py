import sys
from pathlib import Path

from pk_assist.notes import load_notes, search_notes
from pk_assist.print import print_loaded_notes, print_goodbye, print_note, print_no_file, print_idk, print_not_folder_or_dir, print_no_folder, print_filtered_notes, print_no_query
from pk_assist.input_util import should_exit, should_list, should_show, should_search

# temporary global variable
NOTES = []

def init_app():
    global NOTES
    
    if len(sys.argv) < 2:
        print_no_folder()
        return

    folder_arg = sys.argv[1]
    folder = Path(folder_arg)

    if not folder.exists() or not folder.is_dir():
        print_not_folder_or_dir()
        return
    
    NOTES = load_notes(folder)

    print_loaded_notes(NOTES)

def run_cli():
    global NOTES
    try:
        while True:
            user_input = input("➤ : ") 
            if should_exit(user_input):
                print_goodbye()
                break
            elif should_list(user_input):
                print_loaded_notes(NOTES)
                continue
            elif should_show(user_input):
                parts = user_input.split(" ", 1)
                if len(parts) < 2:
                    print_no_file()
                    continue
                print_note(NOTES, parts[1])
                continue
            elif should_search(user_input):
                parts = user_input.split(" ", 1)
                if len(parts) < 2 or parts[1].strip() == "":
                    print_no_query()
                    continue
                filtered = search_notes(NOTES, parts[1].strip())
                print_filtered_notes(filtered)
            else:
                print_idk()
                continue
    except (KeyboardInterrupt, EOFError):
        print_goodbye()
    
def main():
    init_app()
    run_cli()

if __name__ == "__main__":
    main()
