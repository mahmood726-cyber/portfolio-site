import json
from pathlib import Path


REQUIRED_SUBMISSION_FILES = ('config.json', 'paper.md', 'protocol.md', 'index.html')


def test_repository_smoke():
    root = Path(__file__).resolve().parents[1]
    assert root.exists()

    submission = root / 'e156-submission'
    if submission.is_dir():
        for name in REQUIRED_SUBMISSION_FILES:
            assert (submission / name).exists(), name

        config = json.loads((submission / 'config.json').read_text(encoding='utf-8'))
        body = config.get('body', '')
        assert len(body.split()) == 156

        sentences = config.get('sentences', [])
        assert len(sentences) == 7
        assert all((entry.get('text') if isinstance(entry, dict) else str(entry)).strip() for entry in sentences)
        assert config.get('notes', {}).get('code')
        return

    candidates = []
    for base in [root, root / 'src', root / 'app', root / 'scripts']:
        if not base.is_dir():
            continue
        for pattern in ('*.py', '*.R', '*.html', '*.js', '*.ts'):
            candidates.extend(base.glob(pattern))
    assert candidates


def test_body_parity_across_copies():
    """The 156-word body is duplicated across several submission artifacts.

    Guard against silent drift: config.json is the source of truth; paper.json
    must carry a byte-identical body, and the same paragraph must appear
    verbatim in the two Markdown copies (e156-submission/paper.md and
    paper/manuscript.md). Any edit to one copy that is not mirrored to the
    others fails this test.
    """
    root = Path(__file__).resolve().parents[1]
    submission = root / 'e156-submission'
    if not submission.is_dir():
        return

    config = json.loads((submission / 'config.json').read_text(encoding='utf-8'))
    body = config.get('body', '')
    assert body, 'config.json body is empty'

    paper_json = json.loads((submission / 'paper.json').read_text(encoding='utf-8'))
    assert paper_json.get('body', '') == body, 'paper.json body differs from config.json body'

    for md_path in (submission / 'paper.md', root / 'paper' / 'manuscript.md'):
        text = md_path.read_text(encoding='utf-8')
        assert body in text, f'{md_path.name} does not contain the config.json body verbatim'
