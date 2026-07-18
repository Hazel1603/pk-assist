import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvaluationCase:
    question: str
    expected_sources: list[Path]
    expected_concepts: list[str]


def load_evaluation_cases(path: Path) -> list[EvaluationCase]:
    data = json.loads(path.read_text(encoding="utf-8"))

    cases = []

    for item in data:
        cases.append(
            EvaluationCase(
                question=item["question"],
                expected_sources=[Path(source) for source in item["expected_sources"]],
                expected_concepts=item.get("expected_concepts", []),
            )
        )

    return cases
