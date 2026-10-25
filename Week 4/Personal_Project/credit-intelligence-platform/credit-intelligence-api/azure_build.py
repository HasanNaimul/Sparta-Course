"""Create and populate the Credit Intelligence Azure AI Search index.

Run from the project root:
python -m azure_build
"""

import azure_store
import knowledge_store
from config import settings


def main() -> None:
    loaded = azure_store.build_index(knowledge_store.CHUNK_STRATEGY)
    print(f"Loaded {loaded} chunks into '{settings.azure_search_index}' at {settings.azure_search_endpoint}")


if __name__ == "__main__":
    main()