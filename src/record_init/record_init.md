purpose: Initialize a bd store rooted at a directory using the vm prefix, running bd's server on the port given by BD_SERVER_PORT.
signature: record_init(path: str) -> dict
inputs: path: an existing empty directory.
outputs: {'path': str, 'prefix': 'vm'}.
side effects: runs `bd init --prefix vm --non-interactive --server --server-port <port>` with cwd=path, creating bd store files in that directory.
work item id: 0001-1-record_init-code
