import numpy as np


def cdf_from_histogram(hist, bins):
    """
    Compute the cumulative distribution function for the given histogram.

    The CDF is computed over linearly interpolated/extrapolated values at
    bin edges (as opposed to using bin center values directly), and
    contains as many elements as the `bins` array.

    To sample from the distribution, use linear interpolation, e.g.
    ```
    np.interp(random_values, cdf, bins)
    ```
    where first argument is a random number (or array of random numbers)
    on interval [0, 1].
    """

    # Calculate half bin sizes
    steps = np.diff(bins) / 2

    # Calculate slope between bin mid-points (centers)
    slopes = np.diff(hist) / (steps[:-1] + steps[1:])

    # Compute heights at bin edges by means of linear interpolation/extrapolation:
    edge_values = np.concatenate((
        # Extrapolation before first bin's mid-point (between lower
        # boundary and first mid-point) using slope between first and
        # second bin's mid-point.
        [hist[0] - steps[0] * slopes[0]],
        # Interpolation between left and right mid-point
        hist[:-1] + steps[:-1] * slopes,
        # Extrapolation after last mid-point (between the last mid-point
        # and the upper boundary) using slope between penultimate and
        # last bin's mid-point.
        [hist[-1] + steps[-1] * slopes[-1]]
    ))

    # Calculate cumulative sum
    cdf = np.cumsum(edge_values)

    # Subtract the lower bound and scale by upper bound
    cdf -= cdf[0]
    cdf /= cdf[-1]

    # Return the CDF
    return cdf
