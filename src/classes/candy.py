# 
from uuid import uuid4
class Candy():
    # Determines how much energy a piece \
    # of candy will provide per unit size.
    ENERGY_SIZE_RATIO = 10
    
    # The time it takes for a piece of candy \
    # to perish after it appears.
    SHELF_LIFE = 15
    
    def __init__(self, *,
                 size = 2.0,
                 position=(0.0, 0.0)):
        self.size = size
        self.time_to_perish = self.SHELF_LIFE
        self.position = position
        
        self.id = uuid4().int

        
    def __hash__(self):
        return self.id
        