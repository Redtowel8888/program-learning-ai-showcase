# Working with AI coding agents

Program Learning AI is developed with two AI coding agents, OpenAI Codex and
Anthropic Claude, working in one repository. AI agents can produce confident
results that are wrong, so the workflow is built to keep their output
trustworthy.

## When to use a second model

Before bringing in the second model, ask:

> Is there a specific, independent contribution the second model can make that
> could materially change the outcome?

**One model** is enough for routine, reversible or clearly specified work, where
a second opinion would likely just say "looks good".

**Two models** are worth it when a mistake could cause data loss or invalid
evidence, when there are real tradeoffs between approaches, when the first
model is stuck, or when independent review could catch hidden assumptions.

## Collaboration modes

| Mode | How it works |
| --- | --- |
| **Blind review** (default) | The primary model implements. The reviewer gets only the requirements, the diff, the test results and one review question, never the primary model's reasoning. It records its findings before seeing anything else. |
| **Specialist consultation** | One bounded question, tied to concrete evidence. |
| **Parallel exploration** | Both models propose an approach on their own, and one final owner chooses. Used sparingly. |

## Handoff protocol

A shared handoff file is the single source of truth for:

- who is the **primary owner** and who currently **owns writes** (exactly one
  model at any moment);
- what is done, what is pending, and whether an editing pass is unfinished;
- the read and write permissions for the current assignment;
- a **concrete next action**, which can be run right away, not "continue
  working".

When one model runs out of quota, the other can take over. It reads the
handoff, checks every claim against the actual repository state, keeps any
unfinished edits, records the takeover, and continues from the next action.

## Grounding rules

These rules apply to every agent, in every project:

- **Approvals come from the human, per action.** Agents never commit, push,
  publish, or unlock protected files on their own authority.
- **Stop at locks.** A read-only file or an access-denied error means stop and
  report. Agents never work around it.
- **Never change evidence to make checks pass.** No editing sealed data,
  manifests or test assertions, and no adding skips.
- **Numbers come from files.** Every reported figure matches a stored data file
  or tool output exactly. Anything not measured is marked UNVERIFIED.
- **Check other agents' numbers** against the data files during review.

These rules are backed by OS-level file locks on protected areas, an
independent checker, and a sentinel process outside the repository that
watches for unauthorized changes.
