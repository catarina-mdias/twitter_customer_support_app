"""
Text processing utilities for customer support analytics.
Handles text preprocessing, cleaning, and keyword extraction.
"""

import pandas as pd
import numpy as np
import re
import string
from typing import List, Dict, Optional, Tuple
import logging
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """Handles text preprocessing and analysis for customer support messages."""
    
    def __init__(self):
        """Initialize the text processor with NLTK components."""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set()
        self._setup_nltk()
        logger.info("Text processor initialized")
    
    def _setup_nltk(self):
        """Setup NLTK components and download required data."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Load stop words
            self.stop_words = set(stopwords.words('english'))
            
            # Add custom stop words for customer support
            custom_stop_words = {
                'ticket', 'support', 'customer', 'service', 'help', 'issue',
                'problem', 'please', 'thank', 'thanks', 'hello', 'hi',
                'regards', 'best', 'sincerely', 'dear', 'sir', 'madam'
            }
            self.stop_words.update(custom_stop_words)
            
        except Exception as e:
            logger.warning(f"Error setting up NLTK: {str(e)}")
            self.stop_words = set()
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text for analysis.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text or pd.isna(text):
            return ""
        
        # Convert to string
        text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove extra punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List[str]: List of keywords
        """
        if not text or pd.isna(text):
            return []
        
        try:
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Tokenize
            tokens = word_tokenize(cleaned_text)
            
            # Remove stop words and short words
            filtered_tokens = [
                token for token in tokens 
                if token not in self.stop_words 
                and len(token) > 2 
                and token.isalpha()
            ]
            
            # Count word frequencies
            word_counts = Counter(filtered_tokens)
            
            # Get most common keywords
            keywords = [word for word, count in word_counts.most_common(max_keywords)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text (basic implementation).
        
        Args:
            text: Text to detect language for
            
        Returns:
            str: Detected language code
        """
        if not text or pd.isna(text):
            return 'unknown'
        
        try:
            # Simple language detection based on common words
            text_lower = text.lower()
            
            # English indicators
            english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
            english_count = sum(1 for word in english_words if word in text_lower)
            
            # Spanish indicators
            spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se']
            spanish_count = sum(1 for word in spanish_words if word in text_lower)
            
            # French indicators
            french_words = ['le', 'la', 'de', 'et', 'à', 'un', 'il', 'que', 'ne', 'se']
            french_count = sum(1 for word in french_words if word in text_lower)
            
            # Determine language based on word counts
            if english_count > spanish_count and english_count > french_count:
                return 'en'
            elif spanish_count > french_count:
                return 'es'
            elif french_count > 0:
                return 'fr'
            else:
                return 'en'  # Default to English
                
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'unknown'
    
    def get_text_statistics(self, text: str) -> Dict:
        """
        Get basic text statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict: Text statistics
        """
        if not text or pd.isna(text):
            return {
                'word_count': 0,
                'character_count': 0,
                'sentence_count': 0,
                'average_word_length': 0.0,
                'readability_score': 0.0
            }
        
        try:
            # Basic counts
            word_count = len(text.split())
            character_count = len(text)
            sentence_count = len(re.split(r'[.!?]+', text))
            
            # Average word length
            words = text.split()
            average_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Simple readability score (Flesch Reading Ease approximation)
            if sentence_count > 0 and word_count > 0:
                avg_sentence_length = word_count / sentence_count
                avg_syllables_per_word = self._estimate_syllables(text) / word_count
                readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            else:
                readability_score = 0.0
            
            return {
                'word_count': word_count,
                'character_count': character_count,
                'sentence_count': sentence_count,
                'average_word_length': round(average_word_length, 2),
                'readability_score': round(readability_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating text statistics: {str(e)}")
            return {
                'word_count': 0,
                'character_count': 0,
                'sentence_count': 0,
                'average_word_length': 0.0,
                'readability_score': 0.0
            }
    
    def _estimate_syllables(self, text: str) -> int:
        """
        Estimate the number of syllables in text.
        
        Args:
            text: Text to count syllables for
            
        Returns:
            int: Estimated syllable count
        """
        # Simple syllable estimation
        words = text.lower().split()
        syllable_count = 0
        
        for word in words:
            # Remove punctuation
            word = re.sub(r'[^a-z]', '', word)
            if not word:
                continue
                
            # Count vowel groups
            vowels = 'aeiouy'
            prev_was_vowel = False
            syllable_count += 1  # Every word has at least one syllable
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = is_vowel
            
            # Subtract one if word ends with 'e'
            if word.endswith('e'):
                syllable_count -= 1
        
        return max(syllable_count, 1)
    
    def process_batch_texts(self, texts: List[str]) -> pd.DataFrame:
        """
        Process a batch of texts and return statistics.
        
        Args:
            texts: List of texts to process
            
        Returns:
            pd.DataFrame: DataFrame with text statistics
        """
        logger.info(f"Processing {len(texts)} texts for statistics")
        
        results = []
        for i, text in enumerate(texts):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(texts)} texts")
            
            stats = self.get_text_statistics(text)
            keywords = self.extract_keywords(text)
            language = self.detect_language(text)
            
            result = {
                **stats,
                'keywords': ', '.join(keywords[:5]),  # Top 5 keywords
                'language': language,
                'keyword_count': len(keywords)
            }
            results.append(result)
        
        df_results = pd.DataFrame(results)
        logger.info(f"Text processing completed for {len(texts)} texts")
        
        return df_results
    
    def get_common_keywords(self, texts: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Get most common keywords across all texts.
        
        Args:
            texts: List of texts to analyze
            top_n: Number of top keywords to return
            
        Returns:
            List[Tuple[str, int]]: List of (keyword, count) tuples
        """
        all_keywords = []
        
        for text in texts:
            keywords = self.extract_keywords(text, max_keywords=20)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        return keyword_counts.most_common(top_n)
    
    def create_word_cloud_data(self, texts: List[str], max_words: int = 100) -> Dict[str, int]:
        """
        Create data for word cloud visualization.
        
        Args:
            texts: List of texts to analyze
            max_words: Maximum number of words for word cloud
            
        Returns:
            Dict[str, int]: Word frequency dictionary
        """
        all_keywords = []
        
        for text in texts:
            keywords = self.extract_keywords(text, max_keywords=50)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Return top words
        return dict(keyword_counts.most_common(max_words))
