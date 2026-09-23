from laya_ai.categorize import categorize


def test_categorize_stub():
    tasks = [
        {"id": "1", "content": "Task 1"},
        {"id": "2", "content": "Task 2"},
    ]
    result = categorize(tasks)
    assert result["1"] == "uncategorized"
    assert result["2"] == "uncategorized"
