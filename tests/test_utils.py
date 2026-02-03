from modern_tui.utils import extract_youtube_id, sanitize_id


def test_extract_youtube_id_short():
    assert extract_youtube_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'


def test_extract_youtube_id_watch():
    assert extract_youtube_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'


def test_sanitize_id():
    assert sanitize_id('Model Name 1!') == 'model-name-1'