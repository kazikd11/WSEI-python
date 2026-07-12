import json
from pathlib import Path

import pytest
from tokenizer import Tokenizer


@pytest.fixture
def tokenizer():
    return Tokenizer()


@pytest.fixture
def imdb_sample():
    return json.loads(Path("imdb_sample.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("text, expected_len", [
    ("", 0),
    ("<br><p></p>", 0),
    ("Hello WORLD!", 2),
    ("...!?!?!?", 0),
    ("zażółć gęślą jaźń", 3),
    ("the cat sat on the mat", 6),
])
def test_tokenize_cases(tokenizer, text, expected_len):
    assert len(tokenizer.tokenize(text)) == expected_len


def test_vocab_dedup(tokenizer):
    assert tokenizer.vocab(["aa bb", "bb cc"]) == {"aa", "bb", "cc"}


def test_min_length_filter():
    tok = Tokenizer(min_length=4)
    assert tok.tokenize("a bb ccc dddd eeeee") == ["dddd", "eeeee"]


def test_imdb_integration(tokenizer, imdb_sample):
    vocab = tokenizer.vocab(imdb_sample)
    assert len(vocab) > 500, f"za malo unikalnych tokenow: {len(vocab)}"


@pytest.mark.xfail(reason="Tokenizer nie wspiera jeszcze regex z grupowaniem")
def test_advanced_regex_unsupported():
    tok = Tokenizer()
    assert tok.tokenize("user@domain.com")[0] == "user@domain.com"
