class ProductNotFound(Exception):
    pass


class InsufficientStock(Exception):
    def __init__(self, message: str):
        self.message = message
