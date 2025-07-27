from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detect the language of the input text
    Returns 'ar' for Arabic, 'en' for English, defaults to 'en' for unknown
    """
    try:
        if not text or len(text.strip()) < 3:
            return 'en'  # Default to English for very short texts
        
        detected = detect(text)
        
        # Map detected languages to our supported ones
        if detected == 'ar':
            return 'ar'
        else:
            return 'en'  # Default to English for all other languages
            
    except LangDetectException:
        return 'en'  # Default to English if detection fails

def is_arabic(text: str) -> bool:
    """
    Check if the text is in Arabic
    """
    return detect_language(text) == 'ar'

def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name
    """
    language_names = {
        'ar': 'Arabic',
        'en': 'English'
    }
    return language_names.get(lang_code, 'English') 