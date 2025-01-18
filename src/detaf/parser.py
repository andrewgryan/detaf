"""Parser helpers"""


def many(parser):
    def inner(tokens, cursor):
        items = []
        while cursor < len(tokens):
            item, cursor = parser(tokens, cursor)
            if item:
                items.append(item)
            else:
                break
        return items, cursor
    return inner


def maybe(decoder):
    def parser(tokens, cursor=0):
        token = peek(tokens, cursor)
        obj = decoder(token)
        if obj:
            return obj, cursor + 1
        else:
            return None, cursor

    return parser


def peek(tokens, cursor):
    try:
        return tokens[cursor]
    except IndexError:
        return None
