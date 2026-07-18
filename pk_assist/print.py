from pk_assist.notes import VectorRecord
from pk_assist.evaluation import RetrievalAggregate, EvaluationResult

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
    print(f"{computer}{confused} Folder does not exist or is not a directory! ")

def print_not_file():
    print(f"{computer}{confused} Path is not a file!")

def print_no_query():
    print(f"{computer}{confused} No query provided.")

def print_no_folder():
    print(f"{computer}No notes folder passed! Skip loading...")
    print("\tUsage: python3 -m pk_assist.cli <notes-folder>")

def print_chunks(chunks):
    print(f"{computer}created {len(chunks)} chunks")

def print_embedded_chunks(embedded_chunks):
    print(f"{computer}created {len(embedded_chunks)} embedded chunks")

def print_database_entries(entries):
    print(f"{computer}created {entries} entries in database")

def print_vector_records(records: list[VectorRecord]):
    print(f"{computer}Retrieved the following records:")
    for record in records:
        print(f"\t- {record}")

def print_context(context):
    print(f"{computer}Constructed context:")
    if context == "":
        return
    print(context)

def print_answer(answer):
    print(f"{computer}Generated answer:")
    if answer == "":
        return
    print(answer)

def print_citations(citations):
    print(f"{computer}Cited:")
    if not citations:
        return 
    for citation in citations:
        print(f"\t- {citation}")

def print_evaluation_results(results: list[EvaluationResult]):
    print(f"{computer}Individual Results:")
    for result in results:
        expected_sources = ", ".join(str(path) for path in result.case.expected_sources)
        retrieved_sources = ", ".join(str(path) for path in result.retrieved_sources)
        print(f"\tQuestion: {result.case.question}")
        print(f"\tExpected sources: {expected_sources}")
        print(f"\tRetrieved sources: {retrieved_sources}")
        print(f"\tRecall@{result.top_k}: {result.recall_at_k}")
        print(f"\tContext size: {result.context_size_chars} characters")
        print("\n")

def print_aggregate_results(result: RetrievalAggregate):
    print(f"{computer}Aggregated Results:")
    print(f"\tCases evaluated: {result.case_count}")
    print(f"\tAverage Recall@{result.top_k}: {result.average_recall_at_k}")
    print(f"\tAverage context size: {result.average_context_size_chars} characters")
    
def print_evaluation_error(error):
    print(f"{computer}{confused} encountered the following error:")
    print(error)

def print_top_k_validation_error(error):
    print(f"{computer}{confused} top_k must be {error}")

def print_not_enough_arguments():
    print(f"{computer}{confused} Insufficient arguments for compare command")

def print_aggregate_list(aggregates: list[RetrievalAggregate]):
    print(f"{computer}Comparison Results:")
    print(f"top_k\tavg Recall@K\tavg context chars")
    for agg in aggregates:
        print(f"{agg.top_k}\t{agg.average_recall_at_k}\t\t{agg.average_context_size_chars}")

def print_goodbye():
    print(f"{computer}(„• ֊ •„)੭ Adios!")
