import sys
from pathlib import Path

from pk_assist.notes import load_notes, search_notes, chunk_notes, embed_chunks, LocalVectorDatabase, build_context, answer_question
from pk_assist.print import *
from pk_assist.input_util import *
from pk_assist.model import PlaceholderModel

# temporary global variable
NOTES = []
CHUNKS = []
EMBEDDED_CHUNKS = []
DATABASE = None

def init_app():
    global NOTES
    global CHUNKS
    global EMBEDDED_CHUNKS
    global DATABASE
    
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

    CHUNKS = chunk_notes(NOTES)
    print_chunks(CHUNKS)

    EMBEDDED_CHUNKS = embed_chunks(CHUNKS)
    print_embedded_chunks(EMBEDDED_CHUNKS)

    DATABASE = LocalVectorDatabase()
    DATABASE.add_many(EMBEDDED_CHUNKS)
    print_database_entries(DATABASE.count())

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
            elif should_retrieve(user_input):
                parts = user_input.split(" ", 1)
                if len(parts) < 2 or parts[1].strip() == "":
                    print_no_query()
                    continue
                results = DATABASE.search(parts[1].strip())
                print_vector_records(results)
                print_context(build_context(results))
            elif should_ask(user_input):
                parts = user_input.split(" ", 1)
                if len(parts) < 2 or parts[1].strip() == "":
                    print_no_query()
                    continue
                question = parts[1].strip()
                results = DATABASE.search(question)
                context = build_context(results)
                answer = answer_question(question, context, PlaceholderModel())

                print_context(context)
                print_answer(answer)
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
