import sys
from pathlib import Path

from pk_assist.notes import load_notes, search_notes, chunk_notes, embed_chunks, LocalVectorDatabase, build_context, answer_question, build_citations, build_context_result, Note
from pk_assist.print import *
from pk_assist.input_util import *
from pk_assist.model import PlaceholderModel
from pk_assist.evaluation import load_evaluation_cases, evaluate_retrieval, aggregate_retrieval, EvaluationDatasetError, compare_retrieval_settings

# temporary global variable
NOTES = []
CHUNKS = []
EMBEDDED_CHUNKS = []
DATABASE = None
FOLDER = None

def load_database(folder):
    global NOTES
    global CHUNKS
    global EMBEDDED_CHUNKS
    global DATABASE

    NOTES = load_notes(folder)
    print_loaded_notes(NOTES)

    CHUNKS = chunk_notes(NOTES)
    print_chunks(CHUNKS)

    EMBEDDED_CHUNKS = embed_chunks(CHUNKS)
    print_embedded_chunks(EMBEDDED_CHUNKS)

    DATABASE = LocalVectorDatabase()
    DATABASE.add_many(EMBEDDED_CHUNKS)
    print_database_entries(DATABASE.count())

def init_app():
    global FOLDER
    if len(sys.argv) < 2:
        print_no_folder()
        return

    folder_arg = sys.argv[1]
    folder = Path(folder_arg)

    if not folder.exists() or not folder.is_dir():
        print_not_folder_or_dir()
        return

    FOLDER = folder
    load_database(FOLDER)

def handle_show_command(user_input: str, notes: list[Note]):
    # argument validation
    parts = user_input.split(" ", 1)
    if len(parts) < 2:
        print_no_file()
        return
    
    print_note(notes, parts[1])

def handle_search_command(user_input: str, notes: list[Note]):
    parts = user_input.split(" ", 1)
    if len(parts) < 2 or parts[1].strip() == "":
        print_no_query()
        return

    filtered = search_notes(notes, parts[1].strip())
    print_filtered_notes(filtered)

def handle_retrieve_command(user_input: str, database: LocalVectorDatabase):
    parts = user_input.split(" ", 1)
    if len(parts) < 2 or parts[1].strip() == "":
        print_no_query()
        return

    results = database.search(parts[1].strip())
    print_vector_records(results)
    print_context(build_context(results))

def handle_ask_command(user_input: str, database: LocalVectorDatabase):
    parts = user_input.split(" ", 1)
    if len(parts) < 2 or parts[1].strip() == "":
        print_no_query()
        return

    question = parts[1].strip()
    results = database.search(question)
    context_result = build_context_result(results)
    answer = answer_question(question, context_result.text, PlaceholderModel())
    citations = build_citations(context_result.records)

    print_context(context_result.text)
    print_answer(answer)
    print_citations(citations)

def handle_evaluate_command(user_input: str, database: LocalVectorDatabase):
    parts = user_input.split()
    if len(parts) < 2 or parts[1].strip() == "":
        print_no_query()
        return
    
    # retrieve and validate args
    try:
        top_k = 3 if len(parts) == 2 else int(parts[2])
    except ValueError:
        print_top_k_validation_error("a whole number.")
        return

    if top_k <= 0:
        print_top_k_validation_error("greater than zero.")
        return

    eval_file = parts[1]
    eval_file_path = Path(eval_file)
    if not eval_file_path.exists() or not eval_file_path.is_file():
        print_not_file()
        return
    
    # evaluate
    try:
        cases = load_evaluation_cases(eval_file_path)
    except EvaluationDatasetError as error:
        print_evaluation_error(str(error))
        return

    results = evaluate_retrieval(cases, database, top_k)
    print_evaluation_results(results)

    aggregated_results = aggregate_retrieval(results, top_k)
    print_aggregate_results(aggregated_results)

def handle_compare_command(user_input: str, database: LocalVectorDatabase):
    # validate args
    parts = user_input.split()
    if len(parts) < 4:
        print_not_enough_arguments()
        return
    
    eval_file = parts[1]
    eval_file_path = Path(eval_file)
    if not eval_file_path.exists() or not eval_file_path.is_file():
        print_not_file()
        return
    
    try:
        k_list = list(map(int, parts[2:]))
    except ValueError:
        print_top_k_validation_error("a whole number.")
        return
    
    if not all(k > 0 for k in k_list):
        print_top_k_validation_error("greater than zero.")
        return
    
    try:
        cases = load_evaluation_cases(eval_file_path)
    except EvaluationDatasetError as error:
        print_evaluation_error(str(error))
        return

    aggregate_list = compare_retrieval_settings(cases, database, k_list)
    print_aggregate_list(aggregate_list)


def handle_update_command(folder: Path | None):
    if folder is None:
        print_no_folder()
        return

    load_database(folder)
    print_update_success()


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
            elif should_show(user_input):
                handle_show_command(user_input, NOTES)
            elif should_search(user_input):
                handle_search_command(user_input, NOTES)
            elif should_retrieve(user_input):
                handle_retrieve_command(user_input, DATABASE)
            elif should_ask(user_input):
                handle_ask_command(user_input, DATABASE)
            elif should_evaluate(user_input):
                handle_evaluate_command(user_input, DATABASE)
            elif should_compare(user_input):
                handle_compare_command(user_input, DATABASE)
            elif should_update(user_input):
                handle_update_command(FOLDER)
            else:
                print_idk()
    except (KeyboardInterrupt, EOFError):
        print_goodbye()
    
def main():
    init_app()
    run_cli()

if __name__ == "__main__":
    main()
