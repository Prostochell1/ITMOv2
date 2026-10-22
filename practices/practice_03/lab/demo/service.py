subscribers = set()


def subscribe(name):
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
