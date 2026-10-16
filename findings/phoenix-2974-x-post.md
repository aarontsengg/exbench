An AI can pass a coding benchmark without fixing the bug.

I found a concrete example while building ExBench, my Elixir/OTP evaluation.

The issue: Phoenix generated Ecto-dependent code even when the user opted out of Ecto.

The reference patch fixes that. But the dataset's designated failing test checks URL-parameter conversion—and already passes BEFORE the fix in our local run.

We also hit a separate environment compatibility error. So this task is quarantined from scoring, not counted as an AI failure.

Lesson: validate the issue, reference fix, and tests together before spending money on agent runs.

This is one task, not a verdict on the whole dataset. I'm preparing a reproducible upstream report.
