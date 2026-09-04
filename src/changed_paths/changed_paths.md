purpose: list changed src paths for this job's folder from git status, excluding paths claimed by other in-progress or checking jobs
signature: changed_paths(folder: str, graph: dict, repo: str = ".") -> list[str]
inputs: folder (this job's function folder name), graph (from record_graph), repo (working tree path)
outputs: sorted list of repo-relative changed paths under src/, excluding paths under src/<x>/ for other claimed folders x
side effects: none (reads git status via subprocess)
work item id: 0003-4-changed_paths-code
