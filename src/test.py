from classes.blob import Blob
from classes.candy import Candy

def test1():
    candy = Candy()
    blob = Blob()
    
    print(candy.id, candy.size)
    print(candy == candy)
    print(blob.id, blob.size)
    print(blob == blob)

def runtests():
    test1()
    
runtests()

