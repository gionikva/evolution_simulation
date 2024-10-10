from uuid import uuid4

class MutationSdvs():
    def __init__(self,*,
                 size_sdv: float = 5.0,
                 speed_sdv: float = 2.0):
        self.size = size_sdv
        self.speed = speed_sdv

class BlobTraits():
    def __init__(self, *, 
                 size: float,
                 speed: float):
        self.size = size
        self.speed = speed

# Represents a single individual
# Will be rendered as a moving circle
class Blob():
    
    # The lifespan of a single blob.
    # If a blob manages to survive this long, \
    # it splits into floor(energy/size) offspring.
    LIFESPAN = 10.0
    
    # Defines the energy/size ratio.
    ENERGY_SIZE_R = 10.0
    
    # Defines the energy_expenditure/size ratio.
    ENERGY_EXP_SIZE_R = 2.0
    
    # The ratio of the above two values will equal \
    # the time a blob will survive moving at full speed \
    # given that it started with full energy.
    
    # Traits:
    #
    # size:
    # Radius of the blob.
    # Must be at least 50% larger than a piece \
    # of candy or prey to consume it.  
    # 
    # speed:
    # Represents the top speed of the blob.
    # This can affect energy expenditure.
    #
    # Dependent values:
    #
    # energy:
    # Represents the total energy this blob can store.
    # If the blob runs out of energy, it dies.
    # This also determines how many offspring the blob \
    # can produce. Depends on size. Size also determines \
    # energy expenditure.
    #
    # 
    def __init__(self, *,
                 traits = BlobTraits(size = 20.0,
                                    speed = 5.0),
                 position=(0.0, 0.0)):
        # phenotypic traits:
        self.traits = traits
        # internal variables:
        self.position = position
        # unique identifier
        self.id = uuid4().int

    def from_traits(size: float,
                    speed: float,
                    position: tuple[float, float]):
        return Blob(traits=BlobTraits(size=size,
                                      speed=speed),
                    position=position)
        
    def __hash__(self):
        return self.id

        