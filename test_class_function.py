def hello():
    print("hello")

class Person:
    
    hello()

    def __init__(self):
        self.bag = []
        hello()
 
    def put_bag(self, stuff):
        self.bag.append(stuff)

james = Person()
james.put_bag('book')

