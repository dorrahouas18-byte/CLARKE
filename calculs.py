"""
Module calculs.py - Conversion d'unités et consolidation des bilans thermiques.
"""

class UnitConverter:
    @staticmethod
    def watts_to_kw(watts: float) -> float:
        return watts / 1000.0

    @staticmethod
    def watts_to_btu(watts: float) -> float:
        """1 Watt = 3.412142 BTU/h"""
        return watts * 3.412142

    @staticmethod
    def watts_to_tr(watts: float) -> float:
        """1 Ton of Refrigeration (TR) = 3516.85 Watts"""
        return watts / 3516.85

    @classmethod
    def convert_all(cls, watts: float) -> dict:
        return {
            "watts": round(watts, 2),
            "kw": round(cls.watts_to_kw(watts), 3),
            "btu_h": round(cls.watts_to_btu(watts), 2),
            "tr": round(cls.watts_to_tr(watts), 2)
        }


class ThermalEngine:
    def __init__(self, safety_margin: float = 0.10):
        self.safety_margin = safety_margin

    def compute_total(self, losses_components: float, building_gains: float) -> dict:
        """
        Calcule la charge thermique totale avec marge de sécurité.
        Formule: P_totale = (P_equipements + P_batiment) * (1 + marge)
        """
        raw_total = losses_components + building_gains
        design_total = raw_total * (1.0 + self.safety_margin)
        
        return {
            "raw_watts": raw_total,
            "design_watts": design_total,
            "units": UnitConverter.convert_all(design_total)
        }