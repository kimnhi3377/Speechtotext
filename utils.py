import re
from collections import Counter

def remove_word_repeat(text):
    words = text.split()
    if not words:
        return text

    result = [words[0]]

    for i in range(1, len(words)):
        if words[i] != words[i - 1]:
            result.append(words[i])

    return " ".join(result)


# ❌ FIX: KHÔNG return pattern nữa (giữ an toàn)
def remove_phrase_repeat(text):
    words = text.split()
    n = len(words)

    for size in range(2, min(6, n // 2 + 1)):
        pattern = words[:size]

        repeat = True
        for i in range(0, n, size):
            if words[i:i+size] != pattern:
                repeat = False
                break

        # chỉ xử lý nếu lặp rất rõ ràng (>= 3 lần)
        if repeat and n >= size * 3:
            return " ".join(pattern)

    return text


# ✔ chỉ xử lý spam cực mạnh (>=5 lần)
def remove_spam_words(text):
    words = text.split()
    counts = Counter(words)

    cleaned = [w for w in words if counts[w] < 5]

    return " ".join(cleaned)


def clean_speech(text):
    text = text.strip()

    # 1. bỏ lặp từ liên tiếp
    text = remove_word_repeat(text)

    # 2. bỏ lặp cụm (an toàn hơn)
    text = remove_phrase_repeat(text)

    # 3. spam filter nhẹ
    text = remove_spam_words(text)

    # 4. normalize space
    text = re.sub(r'\s+', ' ', text)

    return text