"""
Module local.py - Calcul des apports thermiques du bâtiment (enveloppe, éclairage, ventilation).
"""

class BuildingThermalCalculator:
    # Dictionnaire des valeurs U (W/m².K) adapté à la Tunisie
    U_VALUES = {
        # Murs
        "Parpaing creux non isolé (U=2.19)": 2.19,
        "Brique creuse non isolée (U=1.58)": 1.58,
        "Brique creuse + isolation 5cm (U=0.56)": 0.56,
        "Parpaing + isolation 8cm (U=0.40)": 0.40,
        "Béton cellulaire 30cm (U≈0.36)": 0.36,
        "Mur haute performance >8cm isolant (U=0.20-0.30)": 0.25,
        # Toitures
        "Toiture terrasse non isolée (U=1.11)": 1.11,
        "Toiture terrasse isolée (U=0.60-0.80)": 0.70,
        "Toiture isolée haute perf. (U=0.56-0.64)": 0.60,
    }

    @classmethod
    def compute_building_gains(
        cls,
        length: float,
        width: float,
        height: float,
        wall_type: str,
        roof_type: str,
        t_ext: float,
        t_int: float,
        lighting_w_m2: float = 10.0,
        ach: float = 1.5,
        occupants: int = 1
    ) -> dict:
        """
        Calcule les apports thermiques du bâtiment.
        Retourne un dictionnaire avec les détails et le total.
        """
        surface = length * width
        volume = surface * height

        # 1. Transmission par les murs et la toiture
        u_wall = cls.U_VALUES.get(wall_type, 0.5)
        u_roof = cls.U_VALUES.get(roof_type, 0.35)

        surface_murs = 2 * (length + width) * height
        surface_toit = surface

        delta_t = max(0.0, t_ext - t_int)

        q_murs = u_wall * surface_murs * delta_t
        q_toit = u_roof * surface_toit * delta_t
        q_transmission = q_murs + q_toit

        # 2. Éclairage
        q_lighting = surface * lighting_w_m2

        # 3. Occupation (chaleur dégagée par les occupants, environ 100 W/personne)
        q_occupants = occupants * 100.0

        # 4. Ventilation / Infiltration
        # ACH = renouvellement d'air par heure, débit_air = volume * ACH / 3600 (m³/s)
        # Chaleur pour chauffer l'air : Q = 0.34 * débit_air (m³/h) * delta_t
        # ou plus précisément : Q = 0.34 * (volume * ACH) * delta_t
        q_ventilation = 0.34 * (volume * ach) * delta_t

        # Total des gains
        q_total = q_transmission + q_lighting + q_occupants + q_ventilation

        return {
            "total_gains_w": q_total,
            "details": {
                "transmission_w": q_transmission,
                "lighting_w": q_lighting + q_occupants,  # On regroupe éclairage + occupants
                "ventilation_w": q_ventilation,
                "occupants_w": q_occupants,
                "surface_m2": surface,
                "volume_m3": volume,
            }
        }
