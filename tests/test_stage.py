from receipts.store import ReceiptStore
from receipts.stage import Stage


def test_finish_writes_one_done_receipt():
    store = ReceiptStore()
    stage = Stage("s1", store)
    assert stage.finish() is True
    assert store.all("s1") == ["done"]


def test_late_timeout_after_done_writes_nothing():
    store = ReceiptStore()
    stage = Stage("s1", store)
    stage.finish()
    assert stage.time_out() is False
    assert store.all("s1") == ["done"]


def test_done_and_timeout_racing_write_exactly_one_receipt():
    """Force the bad interleaving with a barrier, no sleep and no retries.

    Both paths pass the "no receipt yet" check, then both wait at the barrier
    right before persisting. Only after both have arrived is either allowed to
    write. On the buggy code both then write, so two receipts exist.
    """
    import threading

    store = ReceiptStore()
    barrier = threading.Barrier(2, timeout=5)
    stage = Stage("s1", store, before_write=lambda outcome: barrier.wait())

    results = {}
    worker = threading.Thread(target=lambda: results.update(done=stage.finish()))
    watchdog = threading.Thread(target=lambda: results.update(timeout=stage.time_out()))
    worker.start()
    watchdog.start()
    worker.join(10)
    watchdog.join(10)

    receipts = store.all("s1")
    assert len(receipts) == 1, f"expected one terminal receipt, got {receipts}"
    assert sorted(results.values()) == [False, True], f"exactly one winner, got {results}"
