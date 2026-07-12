import re


class Tokenizer:
    def __init__(self, lower: bool = True, strip_html: bool = True, min_length: int = 1):
        self.lower = lower
        self.strip_html = strip_html
        self.min_length = min_length

    def tokenize(self, text: str) -> list[str]:
        if self.strip_html:
            text = re.sub(r"<[^>]+>", " ", text)
        if self.lower:
            text = text.lower()
        tokens = re.findall(r"\w+", text, flags=re.UNICODE)
        return [token for token in tokens if len(token) >= self.min_length]

    def vocab(self, texts: list[str]) -> set[str]:
        vocab = set()
        for text in texts:
            vocab.update(self.tokenize(text))
        return vocab
