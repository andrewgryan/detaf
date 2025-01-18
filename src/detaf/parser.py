"""Parser helpers"""


def peek(tokens, cursor):
    try:
        return tokens[cursor]
    except IndexError:
        return None
