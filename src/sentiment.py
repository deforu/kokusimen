from janome.tokenizer import Tokenizer

# シンプルな感情辞書（PN Table）
# 出典: 東北大学 乾・岡崎研究室 "日本語評価極性辞書" を参考に簡略化
# http://www.cl.ecei.tohoku.ac.jp/index.php?Open%20Resources%2FJapanese%20Sentiment%20Polarity%20Dictionary
PN_DIC = {
    # ポジティブ
    "良い": 1,
    "嬉しい": 1,
    "楽しい": 1,
    "好き": 1,
    "すごい": 1,
    "素晴らしい": 1,
    "感謝": 1,
    "ありがとう": 1,
    "助かる": 1,
    "便利": 1,
    "安心": 1,
    "成功": 1,
    # ネガティブ
    "悪い": -1,
    "悲しい": -1,
    "怒る": -1,
    "嫌い": -1,
    "ひどい": -1,
    "問題": -1,
    "面倒": -1,
    "残念": -1,
    "失敗": -1,
    "不安": -1,
    "難しい": -1,
    "大変": -1,
}

_tokenizer = Tokenizer()


def analyze_sentiment(text: str) -> float:
    """Analyze sentiment of a text and return a sentiment score.

    The score is the sum of the sentiment values of the words in the text.
    Returns a float value, where > 0 is positive, < 0 is negative, and 0 is neutral.
    """
    score = 0
    tokens = _tokenizer.tokenize(text, stream=True)
    for token in tokens:
        word = token.surface
        if word in PN_DIC:
            score += PN_DIC[word]
    return score
