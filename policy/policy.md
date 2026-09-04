# How We Build Things

Draft 0.2. Written so a 12 year old could follow it. This is the policy. It says who does what and what counts as done. It never names a tool, a model, or a product. Those are choices we can swap later.

## 1. The big idea

We build software in small pieces. Each piece goes down a "V" and back up.

Going down, we say what we want, more and more precisely. Going up, we check that we got it, more and more broadly. Every step down has a matching step up that checks it.

```
What we want ..................................... Did we get what we wanted?
   \                                            /
    What it must do ................... Does it do that?
       \                            /
        Build this, test this ... Built, tested
           \               /
              the code
```

Two words we use a lot:

- **Verify**: did we build it right? Does it match what was asked?
- **Validate**: did we build the right thing? Is it actually what we wanted?

You can build something perfectly and still build the wrong thing. That is why we need both.

## 2. The four roles

Think of it like a small company.

| Role | Who | Their job | Not allowed to |
|---|---|---|---|
| **Board** | A human | Decides what we want and why. Says yes or no at the end. Decides anything that is a matter of taste or judgement. | Read code. Check details. |
| **Architect** | The smartest helper | Turns what the Board wants into clear, checkable instructions. Checks that finished work matches what was asked. Keeps the whole picture in mind across pieces. | Read or write code. Run the process. |
| **Supervisor** | A rulebook, not a thinker | Runs the process. Decides which job is next. Checks every gate. Counts retries. Writes everything down. Passes problems up. | Decide what we want. Write instructions. Write code. Make judgement calls. |
| **Builder** | A cheap, fast helper | Does exactly one job from exactly one instruction sheet. Writes code or writes tests. | Change the job. Make design choices. Touch anything outside the job. |

Problems go **up one level only**. A Builder talks to the Supervisor. The Supervisor talks to the Architect. The Architect talks to the Board. Nobody skips a level.

## 3. The work items

Everything we do is a work item. There are six kinds. Each one on the left has a partner on the right that checks it.

| Going down (what we want) | Going up (checking it) | Who writes it |
|---|---|---|
| **Intent**: what we want and why | **Validation**: the Board says "yes, that is it" | Board |
| **Story**: one thing it must do, with a checklist of what "done" looks like | **Verification**: the Architect ticks every item on the checklist | Architect |
| **Code job**: build one small function | **Test job**: prove that function works | Architect writes both, Builders do them |

Rules for work items:

1. Every item has exactly one parent, except Intent, which has none.
2. Every left-side item has at least one right-side item that checks it.
3. Every right-side item checks exactly one left-side item.
4. A code job and its test job are always created together, as a pair. Neither is done until both are done.
5. A Verification is not done until every code and test job under its Story is done.
6. A Validation is not done until every Verification under its Intent is done.
7. If a left-side item changes, every right-side item that checks it opens again.
8. Only three kinds of link exist: "parent of", "checks", and "needs first". No others.
9. Every item says how it gets checked: by **looking** (a tool inspects it), by **reasoning** (someone analyses it), by **showing** (someone demonstrates it to the Board), or by **testing** (code runs against it). Not everything needs a test.

Nobody is allowed to write an item without its checklist. No checklist, not ready.

## 4. Who checks whom

The person who made a thing never checks that thing. Always somebody else.

| What is being checked | Who made it | Who checks it |
|---|---|---|
| Code | One Builder | A different Builder writes the tests, without seeing the first Builder's work or thoughts |
| A finished code and test pair | Builders | Supervisor, against the instruction sheet |
| A Story's checklist, before any Builder starts | Architect | Supervisor confirms every item is clear, checkable, and linked to an Intent |
| A finished Story | Architect wrote it | Architect checks it against the Intent and against every other finished Story under that Intent |
| A finished Intent | Board wrote it | Board looks at it and decides |

This is written down because it is easy to skip when busy. It is never skipped.

## 5. Gates

A gate is a checkpoint. Nothing passes a gate without meeting every rule at that gate. The Supervisor runs every gate and never uses judgement, only the rules.

| Gate | When | Passes if |
|---|---|---|
| **Ready** | Before a Story goes to Builders | Every checklist item is clear and checkable. Story is linked to an Intent. Every code job has its test job. |
| **Built** | When a Builder says a job is done | Code fits the size and shape rules (section 7). Nothing outside the job was touched. |
| **Proven** | When a test job is done | All tests pass. Tests cover every checklist item they were asked to cover. |
| **Verified** | When all pairs under a Story are done | Architect ticks every item on the Story checklist. No conflict with other finished Stories under the same Intent. |
| **Validated** | When all Stories under an Intent are done | Board says yes. |

## 6. When something fails

The Supervisor follows these rules exactly. It does not think about why.

1. A gate fails: send it back to the Builder with the exact rule that failed. No escalation.
2. A test job fails: reopen its code job, attach the failure, run the pair again.
3. The same pair fails **three** times: stop. Mark it blocked. Send the Architect a short summary: what failed, how many times, which rule. The Architect never sees the code or the raw error.
4. The Architect cannot fix it by rewriting or splitting the jobs: send the Board a short summary.
5. Every retry, every stop, every escalation is written in the log (section 9).

## 7. Shape of the code

Very flat. One function, one folder. Nothing else.

```
src/
  add_numbers/
    add_numbers.<ext>        the code
    test_add_numbers.<ext>   the tests
    add_numbers.md           one short note
```

Rules:

- One public function per folder. The folder name, the file name, and the function name are the same.
- Nothing nested below the function folder.
- Exactly three files in the folder. Never a fourth.
- The note says only: what the function is for, its signature, what goes in, what comes out, what else it touches, and which work item asked for it.

Size and shape limits are checked by a tool at the Built gate, not by a person. The numbers live in the tool's settings, not here. Today they are roughly: fifty lines per file, fifty per function, very few branches, shallow nesting, few parameters. If a function cannot fit, the Architect splits the job. The Builder never decides that.

## 8. How careful to be

Not every piece deserves the same effort. When the Board writes an Intent, it picks one of two levels.

| Level | Means | What extra it needs |
|---|---|---|
| **Low** | If this is wrong, it is annoying, not harmful. | Nothing extra. Supervisor verification is enough to close it. Board may skip looking. |
| **High** | If this is wrong, it matters. | A different Builder writes tests, never the code author. The Board must be shown it working before it closes. |

## 9. The log

The Supervisor writes down every decision it makes, for every piece, at every level. Each entry says:

- Which item and which gate.
- Which rule was checked.
- The actual inputs: the tool output, the test result, the retry count.
- What happened next.

The log is how the Board can trust a closed item it never looked at. Nothing is ever removed from the log.

## 10. One piece, start to finish

1. Board writes an Intent, picks Low or High, and writes the Validation it will use to say yes.
2. Architect writes Stories under it, each with a checklist and a Verification.
3. Architect writes code and test job pairs under each Story, with full instruction sheets.
4. Supervisor runs the Ready gate on each Story.
5. Supervisor hands each pair to Builders, one job each, runs Built and Proven gates, retries on the rules in section 6.
6. Supervisor tells the Architect a Story is ready to verify. Architect checks the checklist and the other Stories under the Intent.
7. Supervisor tells the Board an Intent is ready. Board looks, or is shown it for High, and says yes or no.
8. Next piece.

Good pieces are small. If a Story needs more than a handful of job pairs, it is probably two Stories.

## 11. What this document is not

It is not a list of tools. Trackers, linters, models, and test runners come and go. The rules above stay the same whatever we plug in.
