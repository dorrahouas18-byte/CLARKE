"""
Module variateurs.py - Pertes thermiques des VFD (Variable Frequency Drives).
"""

class VFDCalculator:
    @staticmethod
    def calculate_loss(power_kw: float, efficiency: float = 0.97, custom_loss_w: float = None) -> float:
        """
        Pertes = P_moteur * (1 - rendement) OU valeur constructeur directe.
        """
        if custom_loss_w is not None and custom_loss_w > 0:
            return custom_loss_w
        
        power_w = power_kw * 1000.0
        return power_w * (1.0 - efficiency)

    @staticmethod
    def effective_loss(p_nom_w: float, charge_pct: float) -> float:
        """
        Calcule les pertes effectives en fonction du taux de charge (%).
        """
        return p_nom_w * (charge_pct / 100.0) ** 1.5