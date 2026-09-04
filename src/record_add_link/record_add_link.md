purpose: create a link (parent_of, needs_first, checks) between two existing ids
signature: record_add_link(link: str, src: str, dst: str) -> dict
inputs: link: one of parent_of, needs_first, checks. src, dst: existing ids
outputs: {'link': str, 'src': str, 'dst': str}
side effects: runs the bd CLI to add a dependency link between src and dst
work item id: 0001-1-record_add_link-code
