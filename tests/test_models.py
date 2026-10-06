from src.models import ProtocolSnapshot


def test_negative_value_is_rejected():
    item = ProtocolSnapshot("Test", volume_24h=-1)
    item.validate()
    assert item.volume_24h is None
    assert item.warnings
