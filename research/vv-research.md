# V&V and tiered agentic workflow: research notes

Date: 2026-09-04. Status: input to a future policy, not the policy.

Correction carried forward from review of draft 0.1: the policy is about
interdependent task tracking, ownership, independence and traceability.
Beads, linters and model choice are technology decisions that implement the
policy and must not appear in it.

## 1. What formal V&V actually says

Sources: INCOSE handbook / ISO 15288 (via reqi.io, se-trends.de), IEEE 1012,
DO-178C summaries.

- Verification: built the thing right (conforms to its specification).
  Validation: built the right thing (meets stakeholder intent in use).
- Each right-arm stage checks against its paired left-arm stage. Unit test
  pairs with detailed design, integration with architecture, system
  verification with requirements, validation with concept of operations.
- V&V happens on the left arm too. Before any code exists, requirements and
  design are checked for consistency, completeness and testability, usually
  by inspection and analysis. IEEE 1012 names these as separate activities:
  Concept V&V, Requirements V&V, Design V&V, Implementation V&V, Test V&V.
- Four verification methods, not one: Inspection, Analysis, Demonstration,
  Test. Each requirement records which method verifies it and the pass/fail
  criterion. Test is the expensive one; inspection and analysis are cheap.
- IEEE 1012 minimum tasks that recur at every level: traceability analysis,
  criticality analysis, interface analysis, requirements evaluation,
  hazard/risk/security analysis.
- Integrity levels (1 to 4) set from consequence x likelihood decide how much
  V&V a component gets. Rigor is proportional to risk, never uniform.
- Independence (IV&V, DO-178C): the verifier of an item may not be its
  author. Three dimensions: technical (own tools and analysis), managerial
  (reports outside the dev chain), financial (own budget). DO-178C requires
  the separation to be documented, not just practised.
- Traceability must be bidirectional. Forward finds requirements with no
  verification; backward finds work with no requirement (scope creep). Best
  practice: a small fixed set of link types, checked continuously, with
  orphan detection in both directions. Most failures are links never made or
  never updated after change.
- Iteration is expected. INCOSE calls iterations "the rule, not the
  exception". Verification has three phases: prepare, perform, manage
  results.

## 2. Agile plus V (the sawtooth idea has prior art)

- Agile V (arXiv 2602.20684, AI-augmented engineering): every iteration runs
  four gates with objective exit criteria: Requirements gate (complete and
  testable), Design gate (aligned to requirements), Implementation gate
  (review, static analysis, AI-code validation), Test gate (coverage,
  pass/fail, traceability evidence). Roles include an Audit agent that logs
  every AI decision, and spec-drift detection that flags deviation for human
  approval. Traceability matrix auto-generated per iteration and frozen at
  release.
- ITEA Agile-V hybrid: sprints verify artefact maturity; formal gates verify
  the accumulated system. Test people join sprint planning from day one.
  Named pitfalls: ambiguous operational detail, cultural adoption, scaling
  across long projects.
- Both keep the V per increment and add a slower outer loop of gates. A
  sawtooth alone has no outer loop; something must own the system-level
  view across teeth.

## 3. Agent architecture patterns

- Anthropic, Building Effective Agents: orchestrator-workers when subtasks
  cannot be predicted up front (coding is the example given);
  evaluator-optimizer when there are clear criteria and iteration adds
  measurable value. Add complexity only when it demonstrably improves
  outcomes.
- Planner vs Supervisor are distinct in the literature. Planner turns goal
  into structure, subtasks and dependencies. Supervisor owns orchestration:
  which agent runs next, information and token budgets, stopping criteria,
  replanning on failure, system-wide quality gates, and synthesising partial
  results. Hierarchical frameworks (Nexus, Autonoma) use one root supervisor
  with task supervisors below it.
- aider architect/editor: separating reasoning from editing gave
  state-of-the-art results on aider's benchmark (o1 architect plus cheap
  editor, 85%). Evidence that the frontier-plans, cheap-edits split works.
- Routing/cascade studies (FrugalGPT, RouteLLM): 50 to 98% cost reduction at
  near-frontier quality when execution tasks go to cheap models. The same
  sources warn that routing planning or reasoning to cheap models backfires.
  Confirms the tier split, and marks the boundary: anything requiring
  judgement stays on the expensive tier.

## 4. Human in the loop

- Risk-tiered gates: assign each action type a risk tier; depth of human
  review follows the tier. Critical tier gets approval on every consequential
  action, low tier gets none. Oversight proportional, not uniform.
- Escalation authority: a senior reviewer handles cases above threshold,
  novel conditions, or cross-functional judgement. Front-line approvers pass
  up what they cannot resolve.
- Cloud Security Alliance autonomy tiers: fully supervised, up to full
  autonomy including spawning sub-agents. Useful as a scale for how much
  rope each role gets.

## 5. Spec-driven development tooling

- GitHub Spec Kit: specify, plan, tasks, implement. Kiro: spec, design,
  tasks, implementation. OpenSpec: delta-and-archive model aimed at drift.
  BMAD: roles across product, architecture, UX, dev, test passing files.
- All treat the spec as the primary artefact and code as regenerable output.
  All produce a requirement-to-task chain, none enforce independence between
  the author of code and the author of tests, and none have a supervisor.

## 6. Implications for vmode

### Policy versus technology

| Policy (what) | Technology (how, swappable) |
|---|---|
| Roles, what each may and may not do | Which model runs each role |
| Ownership: every item has one owner and one independent checker | Beads, or any tracker |
| Link types and the rule that every item has a source and a check | Tracker features |
| Gate exit criteria per level | Linter, coverage tool, CI |
| Integrity tiers and what each tier requires | Config |
| Independence rules | Separate contexts / instances |

### Four roles, not three

| Role | Literature name | Owns | Does not |
|---|---|---|---|
| Board (human) | Escalation authority / stakeholder | Intent, validation, subjective calls, integrity tier assignment | Read code, review diffs |
| Architect (frontier) | Planner / task decomposer | Decomposition, acceptance criteria, task specs, verification method per requirement | Orchestrate, read or write code |
| Supervisor | Supervisor / orchestrator | Which task runs next, budgets, stopping, gate enforcement, replanning, escalation routing, audit log | Decide scope, write specs, write code |
| Builder (cheap) | Worker / executor | One task under a strict spec | Change scope, decide design |

Open design choice: Supervisor as a model or as deterministic code. The
literature's supervisor duties (sequencing, budgets, gates, logging) are
mostly mechanical. Recommendation: deterministic state machine for gates
and sequencing, a model only for replanning triage when a task fails.

### Independence, applied

- Code task and test task are authored by different Builder instances with
  no shared context. The tester sees the spec, not the code author's
  reasoning.
- The checker of a level is never its author: Supervisor verifies Builder
  output against spec, Architect verifies stories against intent, Board
  validates. This is the DO-178C rule and must be written down, not assumed.

### Left-arm V&V is missing from the draft

The draft only checked on the right arm. Add a requirements gate: before a
story is released to Builders, someone other than its author checks that
acceptance criteria are complete, testable, and traceable to intent. This
is cheap (inspection) and catches the errors that are most expensive later.

### Verification method per requirement

Not everything is a test. Lint limits are verified by inspection
(tooling), structural rules by analysis, subjective acceptance by
demonstration to the Board. Recording the method per requirement stops
over-testing and gives the Board a clear reason for each item it sees.

### Integrity tiers

Not every slice needs the same rigor. A tier set by the Board at intent
level decides: whether tests are mandatory, whether Board demonstration is
required, how many independent checks. Low tier slices can close on
Supervisor verification alone.

### Traceability rules (tracker-agnostic)

- Fixed link types: parent-of, verifies, depends-on. No others.
- Every item except intent has exactly one parent.
- Every left-arm item has at least one right-arm item that verifies it.
- Every right-arm item verifies exactly one left-arm item.
- Orphan check both directions runs at every gate.
- Change to a left-arm item reopens every item that verifies it.

## 7. Open questions

1. Supervisor implementation: state machine, model, or hybrid (see above).
2. Outer loop: who owns the system view across sawtooth teeth? Likely
   Architect at story level, Board at intent level, but interface and
   regression checks across slices need an explicit owner.
3. Integrity tier scale: two tiers (Board sees / Board does not see) or
   IEEE's four.
4. Audit log: what the Supervisor records per decision so the Board can
   trust closures it did not witness.
5. Whether the Architect may see Builder failure output verbatim during
   replanning, or only the Supervisor's summary.

## Sources

- https://reqi.io/articles/system-engineering-v-diagram-the-vee
- https://www.se-trends.de/en/what-is-actually-the-v-model/
- https://ieeexplore.ieee.org/document/8055462 (IEEE 1012-2016)
- https://spectrum.ieee.org/regulating-ai-programs-roadmap/table-1-ieee-1012-standards-map-of-integrity-levels-onto-a-combination-of-consequence-and-likelihood-levels
- https://dv7engineering.com/2022/03/15/ivv-in-regulated-industries/
- https://phoenixnap.com/glossary/iv-and-v
- https://arxiv.org/pdf/2602.20684 (Agile V)
- https://itea.org/journals/volume-47-1/implementing-agile-v-hybrid-model/
- https://www.anthropic.com/engineering/building-effective-agents
- https://arxiv.org/pdf/2502.19091 (Nexus)
- https://arxiv.org/pdf/2603.19270 (Autonoma)
- https://medium.com/@mjgmario/multi-agent-system-patterns-a-unified-guide-to-designing-agentic-architectures-04bb31ab9c41
- https://aider.chat/2024/09/26/architect.html
- https://tianpan.co/blog/2025-11-03-llm-routing-model-cascades
- https://www.digitalapplied.com/blog/human-in-the-loop-escalation-design-ai-agents-2026
- https://www.arthur.ai/column/human-in-the-loop-governance-for-ai-agents
- https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/traceability-matrix/
- https://www.sodiuswillert.com/en/blog/implementing-requirements-traceability-in-systems-software-engineering
- https://www.augmentcode.com/tools/best-spec-driven-development-tools
- https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-enterprise-developers/3-examine-github-spec-kit
