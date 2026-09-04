purpose: Check a proposal work item's sheet against the proposal format rules.
signature: proposal_check(item: dict) -> list[str]
inputs: item: a dict as returned by record_show_item, with keys id, kind, title, owner, state, parent, sheet. Only kind and sheet are read.
outputs: list of rule names broken, in fixed order, empty if none: not_proposal, no_page, no_target, bad_target, no_diff, multi_file, target_mismatch.
side effects: none.
work item id: 0002-4-proposal_check-code
