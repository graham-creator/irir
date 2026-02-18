from modern_tui.compare import get_response_text


class DummyAI:
    def __init__(self):
        self._conversations = [{'id': 'c1', 'messages': [{'role': 'assistant', 'model': 'm1', 'turn_id': 't1', 'content': 'hello world'}]}]
        self._current_conv_id = 'c1'


def test_get_response_text_from_conversation():
    ai = DummyAI()
    assert get_response_text(ai, 't1', 'm1') == 'hello world'


def test_get_response_text_missing():
    ai = DummyAI()
    assert get_response_text(ai, 't1', 'm2') == ''