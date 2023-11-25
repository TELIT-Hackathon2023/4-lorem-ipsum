import re, string, unicodedata
import nltk
import contractions
import inflect

from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer

def download_ntlk():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

def download_punkt():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')


# nltk.download('punkt')
download_punkt()
download_ntlk()
# nltk.download('stopwords')


def replace_contractions(text):
    """Replace contractions in string of text"""
    return contractions.fix(text)


def delete_white_symbols(text):
    return re.sub("\n\t\v\r\f", ' ', text)


def remove_URL(sample):
    """Remove URLs from a sample string"""
    return re.sub(r"http\S+", "", sample)


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        if ('#' in word and len(word.translate(str.maketrans('', '', '#'))) >= 1) or ('+' in word and len(word.translate(str.maketrans('', '', '+'))) >= 1):
            new_words.append(word)
            continue
        new_word = word.translate(str.maketrans('', '', string.punctuation))
        if new_word != '':
            new_words.append(new_word)
    return new_words


def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words


def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words


def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems


def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas


def normalize(words):
    words = remove_non_ascii(words)
    # print(words,'1')
    words = to_lowercase(words)
    # print(words,'2')

    words = remove_punctuation(words)
    # print(words,'3')

    words = replace_numbers(words)
    # print(words,'4')

    # words = remove_stopwords(words)
    # print(words,'5')
    sentence = " ".join(words)
    return sentence


def preprocess(sample):
    sample = remove_URL(sample)
    sample = replace_contractions(sample)
    sample = delete_white_symbols(sample)
    # Tokenize
    words = nltk.word_tokenize(sample)

    # Normalize
    return normalize(words)


if __name__ == "__main__":
    sample = "WhereIAm is a cross-platform mobile application for fixing the position of another user’classification_keras.ipynb smartphone. The key feature of the application is that location tracking is activated only upon request. This significantly reduces the load on the phone’classification_keras.ipynb battery and thereby qualitatively distinguishes WhereIAm from its competitors.\n\nTechnologies\n#Dart #FireBase #Firebase Auth #FireBase Database #FireBase Messaging #Flutter #Google maps API #GPS #Push-notification"

    sample = remove_URL(sample)
    sample = replace_contractions(sample)

    # Tokenize
    words = sample.split(' ')
    print(words)

    # Normalize
    words = normalize(words)
    print(words)
