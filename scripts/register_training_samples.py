import argparse
import importlib.util
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

TRAIN_SPEC = importlib.util.spec_from_file_location(
    "train_classifier_module",
    BASE_DIR / "scripts" / "train_classifier.py",
)
if TRAIN_SPEC is None or TRAIN_SPEC.loader is None:
    raise ImportError("Unable to load scripts/train_classifier.py")

train_classifier = importlib.util.module_from_spec(TRAIN_SPEC)
TRAIN_SPEC.loader.exec_module(train_classifier)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Register one or more resume files under a single category."
        )
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Resume files to register in the training manifest.",
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Category label to assign to all provided resumes.",
    )
    parser.add_argument(
        "--manifest",
        default=str(BASE_DIR / "data" / "training_manifest.json"),
        help="Path to the training manifest JSON file.",
    )
    parser.add_argument(
        "--retrain",
        action="store_true",
        help="Rebuild the classifier after registering the samples.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    train_classifier.register_training_samples(
        args.files,
        args.category,
        manifest_path=args.manifest,
    )

    print(f"Registered {len(args.files)} file(s) under {args.category}.")

    if args.retrain:
        result = train_classifier.train_classifier(manifest_path=args.manifest)
        print(
            f"Retrained classifier with {result['samples']} sample(s) and "
            f"{len(result['classes'])} category(ies)."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
