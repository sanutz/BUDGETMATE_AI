import os
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import string

# Download necessary NLTK data - normally done once
try:
    import tempfile
    nltk_data_dir = os.path.join(tempfile.gettempdir(), 'nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
    nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)
    nltk.download('punkt_tab', download_dir=nltk_data_dir, quiet=True)
    nltk.download('stopwords', download_dir=nltk_data_dir, quiet=True)
    stop_words_list = stopwords.words('english')
    stemmer = PorterStemmer()
    NLTK_READY = True
except Exception:
    NLTK_READY = False
    stop_words_list = []

# Fallback basic stemmer if NLTK fails
def fallback_stem(word):
    word = word.lower()
    if word.endswith('ing'):
        return word[:-3]
    elif word.endswith('es'):
        return word[:-2]
    elif word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word

# Keyword mapping for categories
CATEGORY_KEYWORDS = {
    'Food': ['groceri', 'dinner', 'lunch', 'breakfast', 'coffe', 'restaurant', 'cafe', 'food', 'snack', 'pizza', 'burger', 'supermarket', 'mart'],
    'Transport': ['uber', 'lyft', 'taxi', 'cab', 'gas', 'fuel', 'petrol', 'bus', 'train', 'subway', 'transit', 'car', 'repair', 'toll', 'flight', 'ticket', 'transport'],
    'Shopping': ['cloth', 'shoe', 'amazon', 'electron', 'appl', 'mall', 'shop', 'purchas', 'onlin', 'store'],
    'Entertainment': ['movi', 'netflix', 'spotify', 'hulu', 'cinema', 'game', 'concert', 'ticket', 'entertain', 'fun', 'subscript'],
    'Health': ['pharmaci', 'gym', 'doctor', 'hospit', 'clinic', 'dentist', 'medicin', 'health', 'yoga', 'fit'],
    'Education': ['book', 'cours', 'school', 'colleg', 'univers', 'tutor', 'educ', 'class', 'workshop'],
    'Utilities': ['electr', 'water', 'internet', 'phone', 'mobil', 'wifi', 'util', 'bill', 'trash', 'sewer'],
    'Salary': ['salari', 'wage', 'paycheck', 'pay', 'incom', 'bonus', 'freelanc', 'project'],
    'Investment': ['stock', 'divid', 'interest', 'invest', 'crypto', 'bitcoin', 'mutual', 'fund'],
}

def clean_and_tokenize(text):
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    return tokens

def detect_category(description: str) -> str:
    if not description:
        return "Other"
        
    tokens = clean_and_tokenize(description)
    
    # Stem tokens
    stemmed_tokens = []
    if NLTK_READY:
        stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words_list]
    else:
        # Fallback list of stopwords
        fallback_stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'for', 'at', 'in', 'on', 'to', 'with'}
        stemmed_tokens = [fallback_stem(word) for word in tokens if word not in fallback_stopwords]
        
    # Tally matches per category
    category_scores = {cat: 0 for cat in CATEGORY_KEYWORDS.keys()}
    
    for token in stemmed_tokens:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if token in keywords:
                category_scores[category] += 1
                
    # Find category with max score
    best_category = max(category_scores, key=category_scores.get)
    
    if category_scores[best_category] > 0:
        return best_category
    else:
        # Default fallback
        # Check if income keywords exist
        for inc_cat in ['Salary', 'Investment']:
            for inc_kw in CATEGORY_KEYWORDS[inc_cat]:
                if inc_kw in stemmed_tokens:
                    return inc_cat
        return "Other"
