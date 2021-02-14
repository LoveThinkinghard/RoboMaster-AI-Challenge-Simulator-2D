
class Cache:
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
