from check_folder.check_folder import check_folder


def prove_rules(gathered: dict) -> list[str]:
    """Failed rule names for a gathered job: the one check, nothing else.

    gathered holds folder, kind, changed and cases (from prove_gather).
    Case rules apply only to test jobs; tests run for both kinds whenever
    the folder has a test file, so a code job is proven against its tests.
    """
    options = {"changed": gathered["changed"], "repo": gathered.get("repo", ".")}
    if gathered["kind"] == "test":
        options["cases"] = gathered["cases"]
    return check_folder(gathered["folder"], options)
