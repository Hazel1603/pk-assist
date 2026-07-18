import json
from dataclasses import dataclass
from pathlib import Path
from pk_assist.notes import build_context_result, LocalVectorDatabase


@dataclass
class EvaluationCase:
    question: str
    expected_sources: list[Path]
    expected_concepts: list[str]

class EvaluationDatasetError(Exception):
    pass

def load_evaluation_cases(path: Path) -> list[EvaluationCase]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvaluationDatasetError(
            f"Evaluation file does not exist: {path}"
        ) from error
    except IsADirectoryError as error:
        raise EvaluationDatasetError(
            f"Evaluation dataset path is not a file: {path}"
        ) from error
    except UnicodeDecodeError as error:
        raise EvaluationDatasetError(
            "Evaluation file must be UTF-8 encoded."
        ) from error
    except json.JSONDecodeError as error:
        raise EvaluationDatasetError(
            "Evaluation file contains invalid JSON."
        ) from error

    if not isinstance(data, list):
        raise EvaluationDatasetError("Evaluation dataset must be a list of cases.")

    cases = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise EvaluationDatasetError(
                f"Evaluation case at index {index} must be an object."
            )

        for field in ("question", "expected_sources"):
            if field not in item:
                raise EvaluationDatasetError(
                    f"Evaluation case is missing required field: {field}"
                )

        question = item["question"]
        expected_sources = item["expected_sources"]
        expected_concepts = item.get("expected_concepts", [])

        if not isinstance(question, str):
            raise EvaluationDatasetError(
                f"Evaluation case at index {index} has a non-string question."
            )
        if not isinstance(expected_sources, list) or not all(
            isinstance(source, str) for source in expected_sources
        ):
            raise EvaluationDatasetError(
                f"Evaluation case at index {index} expected_sources must be a list of strings."
            )
        if not isinstance(expected_concepts, list) or not all(
            isinstance(concept, str) for concept in expected_concepts
        ):
            raise EvaluationDatasetError(
                f"Evaluation case at index {index} expected_concepts must be a list of strings."
            )

        cases.append(
            EvaluationCase(
                question=question,
                expected_sources=[Path(source) for source in expected_sources],
                expected_concepts=expected_concepts,
            )
        )

    return cases
    
def calculate_recall_at_k(
    expected_sources: list[Path],
    retrieved_sources: list[Path],
) -> float:

    if len(set(expected_sources)) == 0:
        return 0.0

    matched = set(expected_sources) & set(retrieved_sources)
    
    return len(matched)/len(set(expected_sources))



@dataclass
class EvaluationResult:
    case: EvaluationCase
    top_k: int
    retrieved_sources: list[Path]
    recall_at_k: float
    context_size_chars: int

def evaluate_case(
    case: EvaluationCase,
    database: LocalVectorDatabase,
    top_k: int,
) -> EvaluationResult:
    # search
    records = database.search(case.question, top_k) #returns list[VectorRecords]

    # flatten vector records into list of paths 
    record_paths = [Path(record.note_path) for record in records]
    
    # evaluate recall at k
    recall_k = calculate_recall_at_k(case.expected_sources, record_paths)

    # evaluate context result
    context_result = build_context_result(records)

    return EvaluationResult(
        case=case,
        top_k=top_k,
        retrieved_sources=record_paths,
        recall_at_k=recall_k,
        context_size_chars=len(context_result.text)
    )

def evaluate_retrieval(
    cases: list[EvaluationCase],
    database: LocalVectorDatabase,
    top_k: int,
) -> list[EvaluationResult]:
    return [evaluate_case(case, database, top_k) for case in cases]



@dataclass
class RetrievalAggregate:
    top_k: int
    case_count: int
    average_recall_at_k: float
    average_context_size_chars: float

def aggregate_retrieval(results: list[EvaluationResult], top_k: int) -> RetrievalAggregate:
    
    average_recall = sum(result.recall_at_k for result in results)/len(results) if results else 0.0

    average_context_size = sum(result.context_size_chars for result in results)/len(results) if results else 0.0
    
    return RetrievalAggregate(
        top_k=top_k, 
        case_count=len(results),
        average_recall_at_k=average_recall,
        average_context_size_chars=average_context_size
    )


def compare_retrieval_settings(
    cases: list[EvaluationCase],
    database: LocalVectorDatabase,
    top_k_values: list[int],
) -> list[RetrievalAggregate]:
    aggregates = []

    for top_k in top_k_values:
        results = evaluate_retrieval(cases, database, top_k)
        aggregates.append(aggregate_retrieval(results, top_k))

    return aggregates
    