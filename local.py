"""
Module local.py - Calculs des apports thermiques du bâtiment
"""

class BuildingThermalCalculator:
    U_VALUES = {
        "Mur non isolé (Béton 20cm)": 2.5,
        "Mur isolé (5 cm)": 0.5,
        "Mur très isolé (10 cm)": 0.28,
        "Toiture sandwich isolée": 0.35,
        "Toiture béton non isolée": 3.0
    }

    @classmethod
    def compute_building_gains(cls, length: float, width: float, height: float,
                               wall_type: str, roof_type: str,
                               t_ext: float, t_int: float,
                               lighting_w_m2: float = 10.0, ach: float = 1.5,
                               occupants: int = 1) -> dict:
        
        delta_t = max(0.0, t_ext - t_int)
        area_floor = length * width
        area_walls = 2 * (length + width) * height
        volume = area_floor * height

        # Pertes / Gains par transmission
        u_wall = cls.U_VALUES.get(wall_type, 0.5)
        u_roof = cls.U_VALUES.get(roof_type, 0.35)
        
        q_walls = area_walls * u_wall * delta_t
        q_roof = area_floor * u_roof * delta_t
        transmission_w = q_walls + q_roof

        # Éclairage et équipements internes
        lighting_w = area_floor * lighting_w_m2 + (occupants * 100.0)

        # Infiltration / Renouvellement d'air (Q = V * ACH / 3600 * rho * Cp * DeltaT)
        # 1.2 kg/m3 * 1005 J/kg.K / 3600 ~= 0.335
        ventilation_w = volume * ach * 0.335 * delta_t

        total_gains_w = transmission_w + lighting_w + ventilation_w

        return {
            "total_gains_w": total_gains_w,
            "details": {
                "transmission_w": transmission_w,
                "lighting_w": lighting_w,
                "ventilation_w": ventilation_w
            }
        }