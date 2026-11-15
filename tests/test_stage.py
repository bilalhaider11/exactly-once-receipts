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
