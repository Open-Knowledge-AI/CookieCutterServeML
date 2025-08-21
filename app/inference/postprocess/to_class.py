from numpy import argmax


def probability_to_class(probabilities):
    """
    Convert a list of probabilities to the class with the highest probability.

    Args:
        probabilities (np.ndarray): A list of probabilities.

    Returns:

    """
    return argmax(probabilities) if probabilities else None
