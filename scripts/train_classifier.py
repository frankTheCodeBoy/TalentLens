import importlib.util
import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent.parent

EXTRACT_SPEC = importlib.util.spec_from_file_location(
    "utils_extract",
    BASE_DIR / "utils" / "extract.py",
)
PREPROCESS_SPEC = importlib.util.spec_from_file_location(
    "utils_preprocess",
    BASE_DIR / "utils" / "preprocess.py",
)

if EXTRACT_SPEC is None or EXTRACT_SPEC.loader is None:
    raise ImportError("Unable to load utils.extract")
if PREPROCESS_SPEC is None or PREPROCESS_SPEC.loader is None:
    raise ImportError("Unable to load utils.preprocess")

extract_module = importlib.util.module_from_spec(EXTRACT_SPEC)
preprocess_module = importlib.util.module_from_spec(PREPROCESS_SPEC)
EXTRACT_SPEC.loader.exec_module(extract_module)
PREPROCESS_SPEC.loader.exec_module(preprocess_module)

# extract_text_docx = extract_module.extract_text_docx
extract_text_pdf = extract_module.extract_text_pdf
clean_text = preprocess_module.clean_text

DEFAULT_MANIFEST_PATH = BASE_DIR / "data" / "training_manifest.json"
MODEL_PATH = BASE_DIR / "models" / "resume_classifier.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"


def load_training_manifest(manifest_path: Path | str) -> dict[str, str]:
    manifest_file = Path(manifest_path)

    if not manifest_file.exists():
        raise FileNotFoundError(f"Missing training manifest: {manifest_file}")

    payload = json.loads(manifest_file.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("training_manifest.json must contain a JSON object")

    return {str(filename): str(label) for filename, label in payload.items()}


def save_training_manifest(
    manifest: dict[str, str], manifest_path: Path | str = DEFAULT_MANIFEST_PATH
) -> dict[str, str]:
    manifest_file = Path(manifest_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def register_training_samples(
    file_paths: list[str | Path],
    category: str,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
) -> dict[str, str]:
    manifest_file = Path(manifest_path)

    if manifest_file.exists():
        manifest = load_training_manifest(manifest_file)
    else:
        manifest = {}

    for file_path in file_paths:
        candidate = Path(file_path)
        if not candidate.exists():
            raise FileNotFoundError(f"Missing resume file: {candidate}")

        filename = candidate.name
        if filename in manifest and manifest[filename] != category:
            raise ValueError(
                f"{filename} is already registered under {manifest[filename]}"
            )

        manifest[filename] = category

    return save_training_manifest(manifest, manifest_file)


def _load_resume_text(resume_path: Path) -> str:
    if resume_path.suffix.lower() == ".pdf":
        return extract_text_pdf(str(resume_path))
    else:
        raise ValueError(
            f"Unsupported resume format: {resume_path.name}. "
            f"Please load resume in pdf format.")


def build_training_examples(
    base_dir: Path | str,
    manifest: dict[str, str],
) -> tuple[list[str], list[str]]:
    root = Path(base_dir)
    raw_dir = root / "data" / "raw"

    examples: list[str] = []
    labels: list[str] = []

    for filename, label in manifest.items():
        resume_path = raw_dir / filename

        if not resume_path.exists():
            raise FileNotFoundError(
                f"Missing resume file for manifest entry: {filename}"
            )

        text = _load_resume_text(resume_path)
        examples.append(clean_text(text))
        labels.append(label)

    return examples, labels


def train_classifier(
    base_dir: Path | str = BASE_DIR,
    manifest_path: Path | str = DEFAULT_MANIFEST_PATH,
) -> dict[str, object]:
    manifest = load_training_manifest(manifest_path)
    examples, labels = build_training_examples(base_dir, manifest)

    if len(examples) == 0:
        raise ValueError("No training examples were found")

    if len(set(labels)) < 2:
        raise ValueError("At least two categories are required for training")

    vectorizer = TfidfVectorizer(stop_words="english")
    model = LogisticRegression(max_iter=1000)

    features = vectorizer.fit_transform(examples)
    model.fit(features, labels)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    return {
        "classes": sorted(set(labels)),
        "samples": len(examples),
        "model_path": str(MODEL_PATH),
        "vectorizer_path": str(VECTORIZER_PATH),
    }


if __name__ == "__main__":
    result = train_classifier()
    print(json.dumps(result, indent=2))
