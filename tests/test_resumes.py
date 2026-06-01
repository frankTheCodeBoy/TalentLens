import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_URL = "http://127.0.0.1:8000/classify"
DEFAULT_DATA_DIR = BASE_DIR / "data" / "raw"


def load_settings() -> tuple[str, Path]:
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

    url = os.getenv("CLASSIFY_URL", DEFAULT_URL)
    raw_data_dir = Path(os.getenv("CLASSIFY_DATA_DIR", str(DEFAULT_DATA_DIR)))

    if not raw_data_dir.is_absolute():
        data_dir = (BASE_DIR / raw_data_dir).resolve()
    else:
        data_dir = raw_data_dir.expanduser()

    return url, data_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send resume PDFs to the FastAPI classifier endpoint."
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Override CLASSIFY_URL for the API endpoint.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help=(
            "Override CLASSIFY_DATA_DIR for the folder containing "
            "PDF resumes."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="HTTP timeout in seconds.",
    )
    return parser


def iter_pdf_files(data_dir: Path):
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    if not data_dir.is_dir():
        raise NotADirectoryError(f"Data path is not a directory: {data_dir}")

    return sorted(
        path
        for path in data_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def test_resumes():
    url, data_dir = load_settings()
    pdf_files = iter_pdf_files(data_dir)

    assert pdf_files, f"No PDF files found in {data_dir}"

    session = requests.Session()
    headers = {
        "X-API-Key": os.getenv(
            "BACKEND_API_KEY", "changeme123")}  # <-- add this

    for pdf_path in pdf_files:
        with pdf_path.open("rb") as file_obj:
            files = {"file": (pdf_path.name, file_obj, "application/pdf")}
            response = session.post(
                url, files=files, headers=headers, timeout=30
                )  # <-- include headers
            assert response.status_code == 200
            data = response.json()
            assert "category" in data


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    url, data_dir = load_settings()

    if args.url:
        url = args.url
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser()
        if not data_dir.is_absolute():
            data_dir = (BASE_DIR / data_dir).resolve()

    return test_resumes(url, data_dir, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
