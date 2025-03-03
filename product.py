class Product:
    def __init__(self, name, price, available):
        self.name = name
        self.price = price
        self.available = available

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price}, available={self.available})"