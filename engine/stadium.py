from dataclasses import dataclass

@dataclass(frozen=True)
class Stadium:
    name: str
    location: str
    
    # Dimensions in meters
    width_m: float
    length_m: float
    straight_boundary_m: float
    square_boundary_m: float
    
    # --- New Fields for Weather (with defaults) ---
    lat: float = 0.0
    lon: float = 0.0
    
