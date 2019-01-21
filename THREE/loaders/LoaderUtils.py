"""
 * @author Don McCurdy / https://www.donmccurdy.com
"""


def decodeText( array ):
    """
    // Avoid the String.fromCharCode.apply(null, array) shortcut, which
    // throws a "maximum call stack size exceeded" error for large arrays.
    """
    s = ''

    for i in range(len(array)):
        # Implicitly assumes little-endian.
        s += String.fromCharCode( array[ i ] )

    # Merges multi-byte utf-8 characters.
    return decodeURIComponent( escape( s ) )


def extractUrlBase(url):
    index = url.rfind('/')

    if index == - 1:
        return './'

    return url[0:index + 1]
