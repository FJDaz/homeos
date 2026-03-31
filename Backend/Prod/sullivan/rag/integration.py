from typing import Dict, List, Tuple
from rag.pageindex_store import PageIndexStore
import numpy as np
from scipy import spatial

class RAGSetup:
    def __init__(self, page_index_store: PageIndexStore):
        """
        Initialisation du setup RAG avec un objet PageIndexStore existant.

        Args:
        page_index_store (PageIndexStore): Objet PageIndexStore existant.
        """
        self.page_index_store = page_index_store
        self.embeddings: Dict[str, np.ndarray] = {}  # Stockage des embeddings de composants

    def enrich_context(self, context: str, num_similar_components: int = 5) -> Dict[str, str]:
        """
        Enrichit le contexte avec des composants similaires.

        Args:
        context (str): Contexte à enrichir.
        num_similar_components (int, optional): Nombre de composants similaires à retourner. Defaults to 5.

        Returns:
        Dict[str, str]: Dictionnaire avec les composants similaires et leur contexte enrichi.
        """
        # Récupération des embeddings de composants similaires
        similar_components = self.page_index_store.get_similar_components(context, num_similar_components)
        
        # Calcul des embeddings pour les composants similaires
        similar_embeddings = [self.get_embedding(component) for component in similar_components]
        
        # Enrichissement du contexte avec les composants similaires
        enriched_context = {component: self.get_enriched_context(context, similar_embeddings[i]) for i, component in enumerate(similar_components)}
        
        return enriched_context

    def search_semantic(self, query: str, num_results: int = 5) -> List[Tuple[str, float]]:
        """
        Recherche sémantique dans les composants.

        Args:
        query (str): Query de recherche.
        num_results (int, optional): Nombre de résultats à retourner. Defaults to 5.

        Returns:
        List[Tuple[str, float]]: Liste de tuples avec les composants correspondants et leur score de similarité.
        """
        # Calcul de l'embedding de la query
        query_embedding = self.get_embedding(query)
        
        # Récupération des embeddings de composants
        component_embeddings = list(self.embeddings.values())
        
        # Calcul des scores de similarité entre la query et les composants
        scores = [1 - spatial.distance.cosine(query_embedding, component_embedding) for component_embedding in component_embeddings]
        
        # Récupération des composants correspondants et de leurs scores
        results = [(self.get_component_from_embedding(embedding), score) for embedding, score in zip(component_embeddings, scores)]
        
        # Tri des résultats par score de similarité
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:num_results]

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Calcul de l'embedding d'un texte.

        Args:
        text (str): Texte pour lequel calculer l'embedding.

        Returns:
        np.ndarray: Embedding du texte.
        """
        # Implémentation de l'algorithme d'embedding (par exemple, Word2Vec, BERT, etc.)
        # Ici, on utilise une implémentation simplifiée pour les besoins de l'exemple
        return np.array([ord(c) for c in text])

    def get_component_from_embedding(self, embedding: np.ndarray) -> str:
        """
        Récupération du composant associé à un embedding.

        Args:
        embedding (np.ndarray): Embedding du composant.

        Returns:
        str: Composant associé à l'embedding.
        """
        # Recherche de l'embedding dans le dictionnaire d'embeddings
        for component, embed in self.embeddings.items():
            if np.array_equal(embed, embedding):
                return component
        return None

    def get_enriched_context(self, context: str, similar_embedding: np.ndarray) -> str:
        """
        Enrichissement du contexte avec un composant similaire.

        Args:
        context (str): Contexte à enrichir.
        similar_embedding (np.ndarray): Embedding du composant similaire.

        Returns:
        str: Contexte enrichi.
        """
        # Implémentation de l'algorithme d'enrichissement de contexte
        # Ici, on utilise une implémentation simplifiée pour les besoins de l'exemple
        return context + " " + self.get_component_from_embedding(similar_embedding)

# Exemple d'utilisation
page_index_store = PageIndexStore()  # Initialisation de l'objet PageIndexStore
rag_setup = RAGSetup(page_index_store)  # Initialisation du setup RAG

# Enrichissement du contexte
context = "exemple de contexte"
enriched_context = rag_setup.enrich_context(context)
print(enriched_context)

# Recherche sémantique
query = "query de recherche"
results = rag_setup.search_semantic(query)
print(results)

# Backend/Prod/sullivan/rag/integration.py
from typing import List
from Backend.Prod.sullivan.rag.pageindex_store import PageIndexStore
from Backend.Prod.sullivan.rag.component import Component

class RAGIntegration:
    """
    Cette classe fournit des méthodes pour intégrer RAG (Retrieve, Augment, Generate) 
    dans le backend. Elle utilise PageIndexStore pour stocker et récupérer les embeddings 
    des composants.
    """

    def __init__(self, page_index_store: PageIndexStore):
        """
        Initialise l'intégration RAG avec un objet PageIndexStore.

        Args:
        page_index_store (PageIndexStore): Instance de PageIndexStore pour stocker et récupérer les embeddings.
        """
        self.page_index_store = page_index_store

    def enrich_context(self, intent: str, existing_components: List[Component]) -> str:
        """
        Enrichit le contexte avec des composants similaires trouvés via RAG.

        Args:
        intent (str): L'intention ou le contexte à enrichir.
        existing_components (List[Component]): La liste des composants existants.

        Returns:
        str: Le contexte enrichi avec des composants similaires.
        """
        # Récupère les embeddings des composants existants
        existing_embeddings = [component.embedding for component in existing_components]

        # Recherche des composants similaires dans PageIndexStore
        similar_components = self.page_index_store.search_semantic(intent, limit=5)

        # Enrichit le contexte avec les composants similaires
        enriched_context = intent
        for component in similar_components:
            if component not in existing_components:
                enriched_context += f" {component.text}"

        return enriched_context

    def search_semantic(self, query: str, limit: int = 5) -> List[Component]:
        """
        Recherche sémantique dans les composants.

        Args:
        query (str): La requête de recherche.
        limit (int, optional): Le nombre maximum de résultats. Defaults to 5.

        Returns:
        List[Component]: La liste des composants correspondant à la requête de recherche.
        """
        # Utilise PageIndexStore pour rechercher les composants similaires
        return self.page_index_store.search_semantic(query, limit=limit)


# Exemple d'utilisation
if __name__ == "__main__":
    # Crée une instance de PageIndexStore
    page_index_store = PageIndexStore()

    # Crée une instance de RAGIntegration
    rag_integration = RAGIntegration(page_index_store)

    # Exemple de recherche sémantique
    query = "example query"
    similar_components = rag_integration.search_semantic(query)
    print(f"Composants similaires pour '{query}':")
    for component in similar_components:
        print(component.text)

    # Exemple d'enrichissement de contexte
    intent = "example intent"
    existing_components = [Component("existing component 1"), Component("existing component 2")]
    enriched_context = rag_integration.enrich_context(intent, existing_components)
    print(f"Contexte enrichi pour '{intent}': {enriched_context}")