def test_hs256key(hs256_key, payload):
    assert hs256_key.decode(hs256_key.encode(payload)) == payload


def test_rs256key(rs256_key, payload):
    assert rs256_key.decode(rs256_key.encode(payload)) == payload


def test_es256key(es256_key, payload):
    assert es256_key.decode(es256_key.encode(payload)) == payload


def test_ps256key(ps256_key, payload):
    assert ps256_key.decode(ps256_key.encode(payload)) == payload


def test_eddsakey(eddsa_key, payload):
    assert eddsa_key.decode(eddsa_key.encode(payload)) == payload
