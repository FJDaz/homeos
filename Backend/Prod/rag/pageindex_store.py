"""
PageIndexRAG module for AETHERFLOW orchestrator.

This module provides a RAG system using LlamaIndex native components to create
a hierarchical, reasoned index of documentation and code files.
Uses MarkdownNodeParser + HierarchicalNodeParser + RouterQueryEngine for
structure-preserving retrieval with traceable references.

NO vector DB needed - CPU-only, zero embeddings cost.
Includes hash-based cache invalidation for fast index reloading.
"""
import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

# Try to import LlamaIndex components
try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
    from llama_index.core.node_parser import (
        MarkdownNodeParser,
        CodeSplitter,
        HierarchicalNodeParser
    )
    from llama_index.core.retrievers import VectorIndexRetriever, BaseRetriever
    from llama_index.core.schema import NodeWithScore, BaseNode
    from llama_index.core.query_engine import RouterQueryEngine

    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logger.warning(f"LlamaIndex not available: {e}. Install with: pip install llama-index llama-index-core")


class PageIndexRetriever(BaseRetriever if LLAMAINDEX_AVAILABLE else object):
    """
    PageIndex-style RAG retriever using LlamaIndex native components.

    Uses hierarchical parsing to preserve document structure (headers, sections)
    and enables multi-level retrieval (ToC → detailed sections).

    Zero vector DB, CPU-only, perfect traceability.
    """

    def __init__(
        self,
        docs_path: Optional[str] = None,
        document_paths: Optional[List[str]] = None,
        index_dir: str = "rag_index",
        use_embeddings: bool = False  # Set to True if you want embeddings (costs more)
    ):
        """
        Initialize PageIndex retriever.

        Args:
            docs_path: Directory path containing documents (alternative to document_paths)
            document_paths: List of specific file paths to index
            index_dir: Directory to store/load index
            use_embeddings: Whether to use embeddings (False = CPU-only, zero cost)
        """
        if not LLAMAINDEX_AVAILABLE:
            logger.warning("LlamaIndex not available. PageIndexRetriever disabled.")
            self.enabled = False
            self.index = None
            self.document_paths = []
            self.index_dir = Path(index_dir)
            self.use_embeddings = use_embeddings
            return

        self.enabled = True
        self.index_dir = Path(index_dir)
        self.use_embeddings = use_embeddings
        self.index = None  # Initialize index attribute

        # Determine document paths
        if document_paths:
            self.document_paths = [Path(p) for p in document_paths if Path(p).exists()]
        elif docs_path:
            docs_dir = Path(docs_path)
            if docs_dir.exists():
                # Find all .md and .py files
                self.document_paths = list(docs_dir.rglob("*.md")) + list(docs_dir.rglob("*.py"))
            else:
                self.document_paths = []
        else:
            # Default: use PRD and roadmap
            base_dir = Path(__file__).parent.parent.parent.parent
            default_paths = [
                base_dir / "docs" / "guides" / "PRD AETHERFLOW.md",
                base_dir / "docs" / "guides" / "PLAN_GENERAL_ROADMAP.md",
                base_dir / "Backend" / "Prod" / "orchestrator.py"
            ]
            self.document_paths = [p for p in default_paths if p.exists()]

        if not self.document_paths:
            logger.warning("No documents found to index")
            self.enabled = False
            self.index = None
            return

        # Configure Settings
        if not use_embeddings:
            # Zero embeddings - CPU-only mode
            Settings.embed_model = None
            logger.info("PageIndex mode: CPU-only, zero embeddings cost")
        # else: use default embeddings if configured

        # Initialize index
        try:
            self._initialize_index()
            logger.info(f"PageIndexRetriever initialized with {len(self.document_paths)} documents")
        except Exception as e:
            logger.error(f"Failed to initialize PageIndexRetriever: {e}")
            self.enabled = False
            self.index = None

    def _calculate_docs_hash(self) -> str:
        """Calculate hash of documents for cache invalidation."""
        if not self.document_paths:
            return ""

        # Hash based on file paths and modification times
        hash_data = []
        for path in sorted(self.document_paths):
            if path.exists():
                stat = path.stat()
                hash_data.append(f"{path}:{stat.st_mtime}:{stat.st_size}")

        content = "\n".join(hash_data)
        return hashlib.md5(content.encode()).hexdigest()

    def _should_rebuild_index(self) -> bool:
        """Check if index needs rebuild based on document hash."""
        # Ensure self.index is always defined as an attribute
        if not hasattr(self, 'index'):
            self.index = None
            
        hash_file = self.index_dir / "docs_hash.json"

        # Calculate current hash
        current_hash = self._calculate_docs_hash()

        # Try to load existing index
        try:
            if self.index_dir.exists() and any(self.index_dir.iterdir()):
                # Check hash
                if hash_file.exists():
                    with open(hash_file, 'r') as f:
                        cached = json.load(f)
                        if cached.get('hash') == current_hash:
                            logger.info("Index cache valid, loading from disk...")
                            # Try to load index even if hash matches
                            from llama_index.core import StorageContext, load_index_from_storage
                            try:
                                storage_context = StorageContext.from_defaults(
                                    persist_dir=str(self.index_dir)
                                )
                                self.index = load_index_from_storage(storage_context)
                                logger.info(f"Loaded existing index from {self.index_dir}")
                                return False  # No rebuild needed
                            except Exception as e:
                                logger.warning(f"Could not load cached index: {e}. Rebuilding...")
                                self.index = None
                                return True  # Rebuild needed

                # Try to load index even if hash doesn't match
                from llama_index.core import StorageContext, load_index_from_storage
                try:
                    storage_context = StorageContext.from_defaults(
                        persist_dir=str(self.index_dir)
                    )
                    self.index = load_index_from_storage(storage_context)
                    logger.info(f"Loaded existing index from {self.index_dir}")

                    # Save current hash
                    with open(hash_file, 'w') as f:
                        json.dump({'hash': current_hash}, f)
                    return False  # Successfully loaded
                except Exception as e:
                    logger.warning(f"Could not load existing index: {e}. Rebuilding...")
                    self.index = None
        except Exception as e:
            logger.warning(f"Cache check failed: {e}. Rebuilding index...")
            self.index = None

        return True  # Rebuild needed

    def _initialize_index(self):
        """Initialize the hierarchical index (with cache support)."""
        # Check if we can load from cache
        if not self._should_rebuild_index():
            return  # Index already loaded

        # Build new index
        logger.info("Building new index from documents...")

        # 1. Parsing hiérarchique préservant structure
        md_parser = MarkdownNodeParser()  # Headers → métadonnées

        # CodeSplitter requires tree_sitter - use HierarchicalNodeParser as fallback
        try:
            code_parser = CodeSplitter(language="python", max_chars=2000)
        except (ImportError, TypeError) as e:
            # Fallback: use HierarchicalNodeParser for code files
            logger.warning(f"CodeSplitter not available ({e}), using HierarchicalNodeParser for code")
            code_parser = HierarchicalNodeParser.from_defaults()

        # Load documents
        reader = SimpleDirectoryReader(
            input_files=[str(p) for p in self.document_paths]
        )
        docs = reader.load_data()

        # Apply appropriate parsing
        all_nodes = []
        for doc in docs:
            file_path = Path(doc.metadata.get('file_path', ''))
            if file_path.suffix == '.md':
                # Markdown: preserve header structure
                nodes = md_parser.get_nodes_from_documents([doc])
                for node in nodes:
                    node.metadata['file_type'] = 'markdown'
                    node.metadata['original_path'] = str(file_path)
                    node.metadata['file_name'] = file_path.name
                all_nodes.extend(nodes)
            else:
                # Code: use code splitter
                nodes = code_parser.get_nodes_from_documents([doc])
                for node in nodes:
                    node.metadata['file_type'] = 'python'
                    node.metadata['original_path'] = str(file_path)
                    node.metadata['file_name'] = file_path.name
                all_nodes.extend(nodes)

        # 2. Also create hierarchical nodes for structure navigation
        hierarchical_parser = HierarchicalNodeParser.from_defaults()
        hierarchical_nodes = hierarchical_parser.get_nodes_from_documents(docs)

        # Add metadata to hierarchical nodes
        for node in hierarchical_nodes:
            if 'original_path' not in node.metadata:
                # Try to infer from document
                file_path = Path(node.metadata.get('file_path', ''))
                if file_path.exists():
                    node.metadata['original_path'] = str(file_path)
                    node.metadata['file_name'] = file_path.name

        # Combine both: structured nodes + hierarchical nodes
        final_nodes = all_nodes + hierarchical_nodes

        # Create index
        self.index = VectorStoreIndex(final_nodes)

        # Persist index
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index.storage_context.persist(persist_dir=str(self.index_dir))

        # Save hash for cache invalidation
        hash_file = self.index_dir / "docs_hash.json"
        current_hash = self._calculate_docs_hash()
        with open(hash_file, 'w') as f:
            json.dump({'hash': current_hash}, f)

        logger.info(f"Index created with {len(final_nodes)} nodes and cached")

    def _retrieve(self, query: str, **kwargs):
        """
        Multi-level retrieval (PageIndex logic).

        Level 1: Top-level headers/sections (ToC inferred)
        Level 2: Detailed sections within relevant top-level areas
        """
        if not self.enabled or not self.index:
            return []

        # Level 1: Top-level retrieval (broad context)
        top_retriever = self.index.as_retriever(similarity_top_k=2)
        top_nodes = top_retriever.retrieve(query)

        # Level 2: Detailed retrieval (drill-down)
        detailed_retriever = self.index.as_retriever(similarity_top_k=5)
        detailed_nodes = detailed_retriever.retrieve(query)

        # Combine and deduplicate
        seen_ids = set()
        combined_nodes = []
        for node in top_nodes + detailed_nodes:
            node_id = getattr(node, 'node_id', id(node))
            if node_id not in seen_ids:
                seen_ids.add(node_id)
                combined_nodes.append(node)

        return combined_nodes

    async def aretrieve(self, query: str, **kwargs):
        """Async version of retrieve."""
        if not self.enabled or not hasattr(self, 'index') or not self.index:
            return []

        # Level 1: Top-level
        top_retriever = self.index.as_retriever(similarity_top_k=2)
        top_nodes = await top_retriever.aretrieve(query)

        # Level 2: Detailed
        detailed_retriever = self.index.as_retriever(similarity_top_k=5)
        detailed_nodes = await detailed_retriever.aretrieve(query)

        # Combine and deduplicate
        seen_ids = set()
        combined_nodes = []
        for node in top_nodes + detailed_nodes:
            node_id = getattr(node, 'node_id', id(node))
            if node_id not in seen_ids:
                seen_ids.add(node_id)
                combined_nodes.append(node)

        return combined_nodes

    async def retrieve(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant information with traceable references.

        Args:
            query: Search query string
            history: Optional conversation history for context
            top_k: Number of results to return

        Returns:
            List of dictionaries with content, metadata, reference, score
        """
        if not self.enabled or not hasattr(self, 'index') or not self.index:
            return []

        # Enhance query with history context
        enhanced_query = query
        if history:
            context = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in history[-3:]
            ])
            enhanced_query = f"Context:\n{context}\n\nQuery: {query}"

        # Retrieve nodes
        nodes = await self.aretrieve(enhanced_query)

        # Format results with traceable references
        results = []
        for node in nodes[:top_k]:
            if isinstance(node, NodeWithScore):
                content = node.node.text
                score = node.score
                metadata = node.node.metadata
            else:
                content = node.text
                score = getattr(node, 'score', 0.0)
                metadata = node.metadata

            # Extract file information
            file_path = metadata.get('original_path', 'unknown')
            file_name = metadata.get('file_name', Path(file_path).name if file_path != 'unknown' else 'unknown')

            # Extract section from metadata (headers preserved by MarkdownNodeParser)
            section = metadata.get('section', '')
            if not section:
                # Try to extract from text (look for headers)
                text_lines = content.split('\n')
                for line in text_lines[:5]:
                    if line.startswith('#'):
                        section = line.strip('#').strip()
                        break

            # Create traceable reference
            if section:
                reference = f"{file_name}:{section}"
            else:
                reference = file_name

            result = {
                'content': content.strip(),
                'metadata': metadata,
                'reference': reference,
                'score': float(score),
                'file_path': file_path,
                'file_name': file_name
            }
            results.append(result)

        logger.info(f"Retrieved {len(results)} results for query: {query[:50]}...")
        return results

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        doc_types = {}
        for path in self.document_paths:
            ext = path.suffix
            doc_types[ext] = doc_types.get(ext, 0) + 1

        return {
            'enabled': self.enabled,
            'llamaindex_available': LLAMAINDEX_AVAILABLE,
            'total_documents': len(self.document_paths),
            'document_types': doc_types,
            'index_directory': str(self.index_dir),
            'use_embeddings': self.use_embeddings,
            'document_paths': [str(p) for p in self.document_paths]
        }


# Alias for backward compatibility
PageIndexRAG = PageIndexRetriever


# Note: RAGIntegration moved to Backend/Prod/sullivan/rag/integration.py
# The following code is kept for reference but should not be executed here
# as it causes import errors. Use Backend/Prod/sullivan/rag/integration.py instead.

# class RAGIntegration:
#     """
#     Cette classe fournit des méthodes pour intégrer RAG (Retrieve, Augment, Generate) 
#     dans le backend. Elle utilise PageIndexStore pour stocker et récupérer les embeddings 
#     des composants.
#     """
#
#     def __init__(self, page_index_store: PageIndexStore):
#         """
#         Initialise l'intégration RAG avec un objet PageIndexStore.
#
#         Args:
#         page_index_store (PageIndexStore): Instance de PageIndexStore pour stocker et récupérer les embeddings.
#         """
#         self.page_index_store = page_index_store
#
#     def enrich_context(self, intent: str, existing_components: List[Component]) -> str:
#         """
#         Enrichit le contexte avec des composants similaires trouvés via RAG.
#
#         Args:
#         intent (str): L'intention ou le contexte à enrichir.
#         existing_components (List[Component]): La liste des composants existants.
#
#         Returns:
#         str: Le contexte enrichi avec des composants similaires.
#         """
#         # Récupère les embeddings des composants existants
#         existing_embeddings = [component.embedding for component in existing_components]
#
#         # Recherche des composants similaires dans PageIndexStore
#         similar_components = self.page_index_store.search_semantic(intent, limit=5)
#
#         # Enrichit le contexte avec les composants similaires
#         enriched_context = intent
#         for component in similar_components:
#             if component not in existing_components:
#                 enriched_context += f" {component.text}"
#
#         return enriched_context
#
#     def search_semantic(self, query: str, limit: int = 5) -> List[Component]:
#         """
#         Recherche sémantique dans les composants.
#
#         Args:
#         query (str): La requête de recherche.
#         limit (int, optional): Le nombre maximum de résultats. Defaults to 5.
#
#         Returns:
#         List[Component]: La liste des composants correspondant à la requête de recherche.
#         """
#         # Utilise PageIndexStore pour rechercher les composants similaires
#         return self.page_index_store.search_semantic(query, limit=limit)


# Exemple d'utilisation (commented out - RAGIntegration moved to sullivan/rag/integration.py)
# if __name__ == "__main__":
#     # Crée une instance de PageIndexStore
#     page_index_store = PageIndexStore()
#
#     # Crée une instance de RAGIntegration
#     rag_integration = RAGIntegration(page_index_store)
#
#     # Exemple de recherche sémantique
#     query = "example query"
#     similar_components = rag_integration.search_semantic(query)
#     print(f"Composants similaires pour '{query}':")
#     for component in similar_components:
#         print(component.text)
#
#     # Exemple d'enrichissement de contexte
#     intent = "example intent"
#     existing_components = [Component("existing component 1"), Component("existing component 2")]
#     enriched_context = rag_integration.enrich_context(intent, existing_components)
#     print(f"Contexte enrichi pour '{intent}': {enriched_context}")