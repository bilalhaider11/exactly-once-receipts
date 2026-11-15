"""A stage that ends with exactly one terminal receipt: "done" or "timeout".

The worker calls finish() when the stage completes. A watchdog calls
time_out() if the stage overruns. Both can fire close together.
"""


class Stage:
    def __init__(self, stage_id, store, before_write=None):
        self.stage_id = stage_id
        self.store = store
        # Test seam: called right before the receipt is persisted.
        self._before_write = before_write or (lambda outcome: None)

    def finish(self):
        return self._write_terminal("done")

    def time_out(self):
        return self._write_terminal("timeout")

    def _write_terminal(self, outcome):
        self._before_write(outcome)
        # One atomic statement: the primary key lets exactly one writer in.
        return self.store.insert(self.stage_id, outcome)
