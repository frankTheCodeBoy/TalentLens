import re
from sklearn.feature_extraction.text import TfidfVectorizer


def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text.strip()


vectorizer = TfidfVectorizer(stop_words='english')
