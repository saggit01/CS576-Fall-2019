import random

def sample_categorical(distribution):
    """Randomly sample from a categorical distribution (a discrete distribution over K categories).
    
    Args:
        distribution: a list of probabilities representing a discrete distribution over K categories.
    Returns:
        The index of the category sampled."""
    
    r = random.random()
    for i, prob in enumerate(distribution):
        if r < prob:
            return i
        else:
            r -= prob
    # in case we encounter floating point issues return the last index
    return len(distribution) - 1
