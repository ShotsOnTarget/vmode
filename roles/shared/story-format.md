# Story

- **Id**:
- **Parent Intent**:
- **One thing it must do**: one sentence.
- **Customer**: who or what consumes the output, and what they do with it.
- **Supplier**: who or what produces it. A role, or an existing thing we adopt.
- **Inputs**: what the supplier receives, from where, in what form.
- **Outputs**: what the customer gets, in what form.
- **Contract**: the promises the output keeps. Invariants, error behaviour, limits, what is never allowed.
- **Boundaries**: every external thing the code will touch (a record command, a CLI, a library, a file format), one per line. The cutter probes each one and names the probe on the sheet.
- **Checklist**: each line is a sentence a stranger could check, followed by its method in brackets: looking, reasoning, showing, or testing.
  1.
  2.
- **Job pairs**: one line per pair: `name: one line of purpose (checklist items served)`. A pair on a function that already exists says `change:` and what changes.
- **Needs first**: ids of Stories that must be done before this one, if any.
