class OutOfStockException(Exception):
    def __str__(self):
        return "Out of Stock"
