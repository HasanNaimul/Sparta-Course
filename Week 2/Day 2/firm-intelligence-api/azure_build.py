"""THE ENTRY POINT

Create the Azure index and load every chunk into it.

Run from the project root:
python -m azure_build
"""

import azure_store
import settings
from routers import knowledge_store


def main() -> None:
    loaded = azure_store.build_index(knowledge_store.CHUNK_STRATEGY)

    print(
        f"Loaded {loaded} chunks into "
        f"'{settings.AZURE_SEARCH_INDEX}' "
        f"at {settings.AZURE_SEARCH_ENDPOINT}"
    )


if __name__ == "__main__":
    main()