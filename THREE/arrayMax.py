"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""


def arrayMax(array):
    if len(array) == 0:
        return float('-inf')

    m = array[0]

    for i in range(len(array)):
        if array[i] > m:
            m = array[i]

    return m
