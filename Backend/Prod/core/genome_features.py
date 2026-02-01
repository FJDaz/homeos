import numpy as np
import re
from typing import Dict, List, Any
from collections import Counter
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

# Mock IntentTranslator for semantic embeddings
# In a real scenario, this would interact with an actual service or model.
class IntentTranslator:
    """
    A mock class to simulate the IntentTranslator/STAR API for generating
    semantic embeddings and extracting keywords.
    """
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        # A simple TF-IDF vectorizer could be used as a basic text feature extractor
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
        self.fitted_tfidf = False

    def get_features_from_text(self, text: str) -> np.ndarray:
        """
        Generates a mock semantic embedding for the given text.
        In a real scenario, this would call an embedding model.
        """
        if not text:
            return np.zeros(self.embedding_dim)
        # For demonstration, return a random vector for embedding
        # A more sophisticated mock could hash the text or use a pre-trained small embedding model
        np.random.seed(hash(text) % (2**32 - 1)) # Seed for reproducibility based on text
        return np.random.rand(self.embedding_dim)

    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        Extracts keywords from the text using a simple TF-IDF approach (mock).
        In a real scenario, this might use more advanced NLP techniques.
        """
        if not text:
            return []
        
        # Fit TF-IDF if not already fitted (on a dummy corpus for mock, or actual data)
        # For a truly mock scenario without actual corpus, we can just split words
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        
        # Simple keyword extraction: common words excluding stop words
        # This is a very basic mock. A real system would use TF-IDF, RAKE, TextRank etc.
        stop_words = set(['the', 'is', 'and', 'a', 'an', 'to', 'in', 'for', 'with', 'on', 'of', 'from', 'by', 'that', 'this', 'are', 'it', 'or', 'as'])
        keywords = [word for word, count in word_counts.most_common() if word not in stop_words and len(word) > 2]
        
        return keywords[:num_keywords]


class FeatureExtractor:
    """
    Extrait diverses features à partir d'un chemin d'API, d'une méthode HTTP et d'un résumé,
    en les normalisant pour l'inférence bayésienne.
    """
    def __init__(self, intent_translator: IntentTranslator, embedding_dim: int = 128):
        self.intent_translator = intent_translator
        self.embedding_dim = embedding_dim
        
        # Scalers for numerical features
        self.path_depth_scaler = StandardScaler()
        self.num_segments_scaler = StandardScaler()
        self.num_keywords_scaler = StandardScaler()
        
        # One-hot encoder for HTTP methods
        self.method_encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self._fitted_method_encoder = False
        
        # Define common HTTP methods for the encoder
        self.known_http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        self.method_encoder.fit(np.array(self.known_http_methods).reshape(-1, 1))
        self._fitted_method_encoder = True

    def _extract_path_features(self, path: str) -> Dict[str, Any]:
        """
        Extrait les segments du chemin, la profondeur et les motifs regex.
        """
        features = {}
        
        if not path or not isinstance(path, str):
            path = ""
        
        # Normalise le chemin pour éviter les doubles slashes et les slashes finaux
        normalized_path = re.sub(r'/+', '/', path).strip('/')
        segments = [s for s in normalized_path.split('/') if s]
        
        features['path_segments'] = segments
        features['path_depth'] = len(segments)
        features['num_path_segments'] = len(segments)

        # Regex patterns
        features['has_id_in_path'] = 1 if re.search(r'/\d+|/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}|/{[a-zA-Z_]+Id}', path) else 0
        features['has_version_in_path'] = 1 if re.search(r'/v\d+', path, re.IGNORECASE) else 0
        features['has_plural_resource'] = 1 if any(s.endswith('s') for s in segments if len(s) > 2) else 0
        features['is_root_path'] = 1 if not segments else 0
        
        return features

    def _extract_method_features(self, method: str) -> Dict[str, Any]:
        """
        Encode la méthode HTTP en utilisant One-Hot Encoding.
        """
        features = {}
        if not method or not isinstance(method, str):
            method = "UNKNOWN" # Handle unknown methods
        
        method_array = np.array([method.upper()]).reshape(-1, 1)
        encoded_method = self.method_encoder.transform(method_array)
        
        for i, category in enumerate(self.method_encoder.categories_[0]):
            features[f'method_{category.lower()}'] = encoded_method[0, i]
            
        # Add a flag for unknown methods if it's not one of the known ones
        if method.upper() not in self.known_http_methods:
             features['method_unknown'] = 1
        else:
             features['method_unknown'] = 0

        return features

    def _extract_summary_features(self, summary: str) -> Dict[str, Any]:
        """
        Extrait les embeddings sémantiques et les mots-clés du résumé.
        """
        features = {}
        if not summary or not isinstance(summary, str):
            summary = ""

        # Embeddings sémantiques
        embedding = self.intent_translator.get_features_from_text(summary)
        for i, val in enumerate(embedding):
            features[f'summary_embedding_{i}'] = val

        # Mots-clés
        keywords = self.intent_translator.extract_keywords(summary)
        features['summary_keywords'] = keywords
        features['num_summary_keywords'] = len(keywords)
        
        # Add a flag for missing summary
        features['has_summary'] = 1 if summary else 0

        return features

    def normalize_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Normalise les features numériques pour les rendre prêtes à l'inférence bayésienne.
        """
        normalized_features = features.copy()
        
        # Apply scalers to numerical features
        # For simplicity, we'll fit_transform on a single data point.
        # In a real application, scalers would be fitted on a larger dataset.
        
        # Path depth
        depth_val = normalized_features.get('path_depth', 0)
        normalized_features['path_depth_normalized'] = self.path_depth_scaler.fit_transform(np.array([[depth_val]]))[0, 0]
        del normalized_features['path_depth'] # Remove original unnormalized feature

        # Number of path segments
        num_segments_val = normalized_features.get('num_path_segments', 0)
        normalized_features['num_path_segments_normalized'] = self.num_segments_scaler.fit_transform(np.array([[num_segments_val]]))[0, 0]
        del normalized_features['num_path_segments'] # Remove original unnormalized feature
        
        # Number of summary keywords
        num_keywords_val = normalized_features.get('num_summary_keywords', 0)
        normalized_features['num_summary_keywords_normalized'] = self.num_keywords_scaler.fit_transform(np.array([[num_keywords_val]]))[0, 0]
        del normalized_features['num_summary_keywords'] # Remove original unnormalized feature
        
        # Remove raw keywords and path segments, keep only processed numerical features
        if 'path_segments' in normalized_features:
            del normalized_features['path_segments']
        if 'summary_keywords' in normalized_features:
            del normalized_features['summary_keywords']

        return normalized_features

    def extract(self, path: str, method: str, summary: str) -> Dict[str, float]:
        """
        Extrait toutes les features nécessaires, les normalise et les retourne.

        Args:
            path (str): Le chemin de l'API (ex: "/users/{userId}/orders").
            method (str): La méthode HTTP (ex: "GET", "POST").
            summary (str): Un résumé textuel de l'opération de l'API.

        Returns:
            Dict[str, float]: Un dictionnaire de features normalisées prêtes pour l'inférence.
        """
        all_features = {}

        # 1. Extraire les features du chemin
        path_features = self._extract_path_features(path)
        all_features.update(path_features)

        # 2. Extraire les features de la méthode HTTP
        method_features = self._extract_method_features(method)
        all_features.update(method_features)

        # 3. Extraire les features du résumé
        summary_features = self._extract_summary_features(summary)
        all_features.update(summary_features)
        
        # 4. Normaliser les features numériques
        normalized_output = self.normalize_features(all_features)

        return normalized_output

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Initialiser l'IntentTranslator (mock)
    intent_translator = IntentTranslator(embedding_dim=64) # Using a smaller embedding for example

    # Initialiser le FeatureExtractor
    feature_extractor = FeatureExtractor(intent_translator=intent_translator, embedding_dim=64)

    print("--- Test Case 1: Standard API endpoint ---")
    path1 = "/api/v1/users/{userId}/products"
    method1 = "GET"
    summary1 = "Retrieve a list of products for a specific user. Supports pagination."
    features1 = feature_extractor.extract(path1, method1, summary1)
    for k, v in features1.items():
        print(f"{k}: {v}")
    print("\n")

    print("--- Test Case 2: Root path, POST method, short summary ---")
    path2 = "/"
    method2 = "POST"
    summary2 = "Create new resource."
    features2 = feature_extractor.extract(path2, method2, summary2)
    for k, v in features2.items():
        print(f"{k}: {v}")
    print("\n")

    print("--- Test Case 3: Complex path, PATCH method, missing summary ---")
    path3 = "/orgs/v2/departments/finance/reports/monthly_summary_2023"
    method3 = "PATCH"
    summary3 = "" # Missing summary
    features3 = feature_extractor.extract(path3, method3, summary3)
    for k, v in features3.items():
        print(f"{k}: {v}")
    print("\n")

    print("--- Test Case 4: Invalid path/method, long summary ---")
    path4 = "/some//path/with///empty///segments"
    method4 = "INVALID" # Unknown method
    summary4 = "This is a very long summary that describes a complex operation involving multiple microservices and data transformations. It highlights the importance of data consistency and real-time processing capabilities for critical business functions. The system ensures high availability and fault tolerance."
    features4 = feature_extractor.extract(path4, method4, summary4)
    for k, v in features4.items():
        print(f"{k}: {v}")
    print("\n")

    print("--- Test Case 5: Path with UUID ---")
    path5 = "/events/8c7e9b0a-3d2f-4c1e-8b7a-9d6c5b4a3e2d"
    method5 = "DELETE"
    summary5 = "Delete a specific event by its unique identifier."
    features5 = feature_extractor.extract(path5, method5, summary5)
    for k, v in features5.items():
        print(f"{k}: {v}")
    print("\n")

    print("--- Test Case 6: Empty inputs ---")
    path6 = ""
    method6 = ""
    summary6 = ""
    features6 = feature_extractor.extract(path6, method6, summary6)
    for k, v in features6.items():
        print(f"{k}: {v}")
    print("\n")

import re
from typing import Dict, List
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

class FeatureExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.scaler = StandardScaler()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def extract_path_features(self, path: str) -> Dict:
        """
        Extract features from a path.

        Args:
            path (str): The path to extract features from.

        Returns:
            Dict: A dictionary containing the extracted features.
        """
        features = {
            'path_length': len(path),
            'path_depth': path.count('/'),
            'path_segments': len(path.split('/'))
        }
        return features

    def extract_method_features(self, method: str) -> Dict:
        """
        Extract features from an HTTP method.

        Args:
            method (str): The HTTP method to extract features from.

        Returns:
            Dict: A dictionary containing the extracted features.
        """
        features = {
            'method': method
        }
        return features

    def extract_summary_features(self, summary: str) -> Dict:
        """
        Extract features from a summary.

        Args:
            summary (str): The summary to extract features from.

        Returns:
            Dict: A dictionary containing the extracted features.
        """
        tokens = word_tokenize(summary)
        tokens = [token.lower() for token in tokens if token.isalpha()]
        tokens = [token for token in tokens if token not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        summary_features = self.vectorizer.fit_transform([' '.join(tokens)])
        summary_features = self.scaler.fit_transform(summary_features.toarray())
        features = {
            'summary': summary_features.tolist()
        }
        return features

    def extract_regex_features(self, path: str, regex_patterns: List) -> Dict:
        """
        Extract features from a path using regex patterns.

        Args:
            path (str): The path to extract features from.
            regex_patterns (List): A list of regex patterns to use.

        Returns:
            Dict: A dictionary containing the extracted features.
        """
        features = {}
        for pattern in regex_patterns:
            match = re.search(pattern, path)
            if match:
                features[pattern] = 1
            else:
                features[pattern] = 0
        return features

    def extract_features(self, path: str, method: str, summary: str, regex_patterns: List) -> Dict:
        """
        Extract all features from a path, method, and summary.

        Args:
            path (str): The path to extract features from.
            method (str): The HTTP method to extract features from.
            summary (str): The summary to extract features from.
            regex_patterns (List): A list of regex patterns to use.

        Returns:
            Dict: A dictionary containing all the extracted features.
        """
        path_features = self.extract_path_features(path)
        method_features = self.extract_method_features(method)
        summary_features = self.extract_summary_features(summary)
        regex_features = self.extract_regex_features(path, regex_patterns)
        features = {**path_features, **method_features, **summary_features, **regex_features}
        return features

# Example usage:
if __name__ == "__main__":
    feature_extractor = FeatureExtractor()
    path = '/api/v1/users/123'
    method = 'GET'
    summary = 'This is a summary of the API endpoint.'
    regex_patterns = [r'\d+', r'[a-zA-Z]+']
    features = feature_extractor.extract_features(path, method, summary, regex_patterns)
    print(features)