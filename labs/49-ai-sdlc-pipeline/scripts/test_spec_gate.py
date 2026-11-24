import pathlib

from spec_gate import check, find_task

TASKS = """# Implementation Plan
- [x] 1. Infrastructure
  - [x] 1.1 CDK stack
  - [ ] 1.2 DynamoDB tables
- [ ] 2. Notifier
"""


def make(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / ".kiro" / "specs" / "order-notifications"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(TASKS)
    return tmp_path


def test_find_task():
    assert find_task(TASKS, "1.1") is True
    assert find_task(TASKS, "1.2") is False
    assert find_task(TASKS, "9") is None
    assert find_task(TASKS, "1") is True        # "1." must not match "1.1"/"1.2" by accident


def test_gate(tmp_path):
    root = make(tmp_path)
    assert check("Implements: order-notifications#1.1", root)[0]
    assert not check("Implements: order-notifications#1.2", root)[0]
    assert not check("Implements: missing-spec#1", root)[0]
    assert not check("fix typo", root)[0]
    assert check("bump deps\nspec-exempt: dependabot", root)[0]
