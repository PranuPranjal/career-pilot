from .greenhouse import GreenhouseAdapter
from .lever import LeverAdapter
from .ashby import AshbyAdapter

ADAPTERS = {"greenhouse": GreenhouseAdapter(), "lever": LeverAdapter(), "ashby": AshbyAdapter()}
