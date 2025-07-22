class Symbol:
    
    def __init__(self,ticker,price):
        self.ticker = ticker
        self.price = price

    def __str__(self):
        return f"{self.ticker} is ${self.price}"
    
apple = Symbol("AAPL",217.56)

print(apple)