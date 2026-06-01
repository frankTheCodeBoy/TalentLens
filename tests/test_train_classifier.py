import json

import scripts.train_classifier as train_classifier


def test_load_training_manifest_reads_json(tmp_path):
    manifest_path = tmp_path / "training_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {"tech_resume.pdf": "Tech", "finance_resume.pdf": "Finance"}
        )
    )

    assert train_classifier.load_training_manifest(manifest_path) == {
        "tech_resume.pdf": "Tech",
        "finance_resume.pdf": "Finance",
    }


def test_save_training_manifest_writes_json(tmp_path):
    manifest_path = tmp_path / "training_manifest.json"

    result = train_classifier.save_training_manifest(
        {"sales_resume.pdf": "Sales"}, manifest_path
    )

    assert result == {"sales_resume.pdf": "Sales"}
    assert json.loads(manifest_path.read_text()) == {
        "sales_resume.pdf": "Sales"
    }


def test_register_training_samples_appends_and_preserves_existing(tmp_path):
    manifest_path = tmp_path / "training_manifest.json"
    manifest_path.write_text(
        json.dumps({"tech_resume.pdf": "Tech"})
    )

    sample_file = tmp_path / "sales_resume.pdf"
    sample_file.write_text("dummy")

    result = train_classifier.register_training_samples(
        [sample_file],
        "Sales",
        manifest_path,
    )

    assert result == {
        "tech_resume.pdf": "Tech",
        "sales_resume.pdf": "Sales",
    }


def test_register_training_samples_creates_manifest_when_missing(tmp_path):
    manifest_path = tmp_path / "missing" / "training_manifest.json"
    sample_file = tmp_path / "sales_resume.pdf"
    sample_file.write_text("dummy")

    result = train_classifier.register_training_samples(
        [sample_file],
        "Sales",
        manifest_path,
    )

    assert result == {"sales_resume.pdf": "Sales"}
    assert manifest_path.exists()


def test_build_training_examples_uses_manifest_and_extractor(
    monkeypatch, tmp_path
):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    resume_path = raw_dir / "tech_resume.pdf"
    resume_path.touch()

    def fake_extract(path):
        assert path == str(resume_path)
        return "Python FastAPI SQL"

    monkeypatch.setattr(train_classifier, "extract_text_pdf", fake_extract)

    examples, labels = train_classifier.build_training_examples(
        tmp_path,
        {"tech_resume.pdf": "Tech"},
    )

    assert examples == ["python fastapi sql"]
    assert labels == ["Tech"]
