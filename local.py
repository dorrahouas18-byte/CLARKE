"""
Module local.py - Calculs des apports thermiques du bâtiment
"""

class BuildingThermalCalculator:
     U_VALUES = {
        # Murs
        "Parpaing creux non isolé": 2.19,
        "Brique creuse non isolée": 1.58,
        "Brique creuse + isolation 5cm": 0.56,
        "Parpaing + isolation 8cm": 0.40,
        "Béton cellulaire 30cm": 0.36,
        "Mur haute performance >8cm isolant": 0.25,  # Valeur moyenne
        # Toitures
        "Toiture terrasse non isolée": 1.11,
        "Toiture terrasse isolée": 0.70,  # Valeur moyenne
        "Toiture isolée haute perf": 0.60,  # Valeur moyenne
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
