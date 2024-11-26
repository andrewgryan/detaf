class Phenomenon:
    @property
    def category(self):
        return self.__class__.__name__.lower()
