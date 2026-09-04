from gate_proven.gate_proven import gate_proven


def test_failed_detected():
    output = "FAILED src/x/test_x.py::test_a - assert"
    result = gate_proven("job-1", output, ["a"])
    assert "tests_failed" in result


def test_missing_case():
    output = "PASSED src/x/test_x.py::test_a\n1 passed in 0.1s"
    result = gate_proven("job-1", output, ["a", "b"])
    assert "case_missing" in result


def test_extra_case():
    output = (
        "PASSED src/x/test_x.py::test_a\n"
        "PASSED src/x/test_x.py::test_c\n"
        "2 passed in 0.1s"
    )
    result = gate_proven("job-1", output, ["a"])
    assert "case_extra" in result


def test_clean_passes():
    output = (
        "PASSED src/x/test_x.py::test_a\n"
        "PASSED src/x/test_x.py::test_b\n"
        "2 passed in 0.1s"
    )
    result = gate_proven("job-1", output, ["a", "b"])
    assert result == []
