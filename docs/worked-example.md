# Worked example: finding the parameter behind a behavior

**Question:** Which data field sets how long an enemy investigates a sound
before giving up?

## What was known

Enemies responded to a sound through walls and gave up after roughly 20–24
seconds. The community knew a parameter controlled this, but not which one.

## Plan

1. Create a fresh **child sandbox** from the protected baseline, and record the
   baseline data file's SHA-256 hash.
2. Change **only one candidate field**, `SoundTargetForgetTime`, from `3.0` to
   `6.0`. A related field, `forgetTime`, was held constant.
3. Use a **dedicated, isolated save file**, never a real one.
4. Repeat the same scripted scenario and time each phase separately.
5. Run the **unchanged baseline** as a control.

## First result, and why it was misleading

Total time from sound to giving up was 24, 27 and 30 seconds. On its own that
looks noisy. But total time included **travel**: enemies took different routes,
and in one trial one enemy blocked another.

## Separating the phases

Timing only the **investigation phase** (from arrival at the sound to
abandonment) gave:

| `SoundTargetForgetTime` | Investigation dwell, 3 trials (s) |
| --- | --- |
| 3.0 (baseline control) | 3, 3, 3 |
| 6.0 (test) | 6, 6, 6 |

## Conclusion, kept to its scope

- `SoundTargetForgetTime` maps directly, roughly one-to-one, to investigation
  dwell in seconds **for enemies that use the edited entry**.
- `forgetTime` was held constant, so it doesn't explain the change.
- **The field is per-entry, not global.** A later check of an enemy using a
  different entry showed about 1 second of dwell. Changing every enemy would
  need every relevant entry edited.

## What this example shows

- Controlled single-variable change in an isolated copy, with hashes recorded.
- A baseline control run alongside the test.
- Phase-aware measurement exposed a confounder (travel time) that the headline
  number hid.
- The conclusion was limited to what was actually tested.
