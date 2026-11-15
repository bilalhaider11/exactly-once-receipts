# exactly-once-receipts

A stage ends with exactly one terminal receipt: `done` (worker) or `timeout` (watchdog).

Read the history in order:

1. `ef0564b` stage + happy-path tests + CI (green)
2. `076f9af` failing test: done and timeout race and write two receipts (CI red)
3. `7219960` fix: one atomic insert guarded by a primary key (CI green)

## What the test proves

The old code checked "no receipt yet" and then wrote in a second statement, so both paths
could pass the check before either wrote. The test forces that interleaving with a
`threading.Barrier` placed between check and write: no `sleep()`, no repeat loop, so it
fails every time on the old code. After the fix there is no check-then-write window: the
primary key lets one insert win and the other returns `False`.
