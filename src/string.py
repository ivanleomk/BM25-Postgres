import re
from itertools import chain


def generate_ngrams(query: str):
    # Remove punctuation from the query
    query = re.sub(r"[^\w\s]", "", query)
    # Split the query into words
    words = query.split()
    # Generate unigrams (which are just the individual words)
    unigrams = words
    # Generate bigrams by zipping the words with itself offset by one
    bigrams = zip(words, words[1:])
    # Combine unigrams and bigrams into a single list
    all_ngrams = list(chain(unigrams, bigrams))
    # Convert bigrams tuples into a single string
    all_ngrams = [
        " ".join(ngram) if isinstance(ngram, tuple) else ngram for ngram in all_ngrams
    ]
    return all_ngrams
