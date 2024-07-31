"""Named after Sanjaya, the charioteer of King Dhritarashtra in the Indian epic Mahabharata.
Observes the battle of Kurukshetra and narrates the events to the blind king.

This engine observes how the Scenario develops 
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field 

@dataclass
class Sanjaya:
    """Sanjaya observes the Scenario
    """
    
    __post_init__(self): 
        self.observations = {
            'commodity': {'resource': {}, 'material': {}},
            'operation'
            
            
        } 
    
    def note(self, aspect, derived, commodity, operation, spatial, index):
        """Notice something being declared 
        """
        
        
    
    