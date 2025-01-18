from detaf.parser import many, maybe


class Phenomenon:
    @property
    def category(self):
        return self.__class__.__name__.lower()


def phenomena_parser(weather_types):
    return many(phenomenon_parser(weather_types))


def phenomenon_parser(weather_types):
    def inner(tokens, cursor=0):
        for weather_type in weather_types:
            parser = maybe(weather_type.taf_decode)
            phenomenon, cursor = parser(tokens, cursor)
            if phenomenon:
                return phenomenon, cursor
        return None, cursor
    return inner
