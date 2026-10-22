"""Notify Mini service primitives.

This module manages a simple in-memory set of subscribers and exposes a
minimal API for subscribing and querying the list.
"""

subscribers = set()


def subscribe(name):
    """Subscribe a non-empty name. Returns a success dict.

    Raises ValueError on empty/whitespace-only names.
    """
    if not name.strip():
        raise ValueError("empty name")
    subscribers.add(name.strip())
    return {"subscribed": True}



def list_subscribers():
    """Return a list of unique subscriber names.

    Order is not specified; callers should not rely on it.
    """
    return list(subscribers)



def count():
    """Return the number of unique subscribers."""
    return len(subscribers)
