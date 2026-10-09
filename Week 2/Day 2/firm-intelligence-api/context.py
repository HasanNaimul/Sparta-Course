"""How retrieved hits become the text the model reads.
Failure: lost in the middle.
"""

def order_for_context(hits: list[dict]) -> list[dict]:
    """Put the strongest evidence near the beginning and end."""
    ranked = sorted(hits, key=lambda hit: hit["score"], reverse=True)

    front = ranked[0::2]
    back = ranked[1::2]

    return front + back[::-1]