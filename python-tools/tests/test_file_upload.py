import pytest

# Simulate file-processing handler that a client would POST to
def process_file(contents: bytes, filename: str):
    # simple checks: ensure not empty and filename safe
    if not contents:
        raise ValueError('empty file')
    if '..' in filename:
        raise ValueError('unsafe filename')
    # pretend to compute checksum
    import hashlib
    return {'filename': filename, 'sha256': hashlib.sha256(contents).hexdigest()}


@pytest.mark.unit
def test_file_processing_checks():
    res = process_file(b'hello', 'greeting.txt')
    assert 'sha256' in res and res['filename'] == 'greeting.txt'
    with pytest.raises(ValueError):
        process_file(b'', 'empty.txt')
    with pytest.raises(ValueError):
        process_file(b'bad', '../escape')
