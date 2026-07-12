import re

POS_WORDS = {"good", "great", "excellent", "wonderful", "love", "best", "amazing", "brilliant", "perfect"}
NEG_WORDS = {"bad", "worst", "awful", "terrible", "hate", "boring", "waste", "poor", "horrible"}


def sentiment_score(text: str) -> int:
    tokens = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    pos = sum(token in POS_WORDS for token in tokens)
    neg = sum(token in NEG_WORDS for token in tokens)
    return pos - neg
