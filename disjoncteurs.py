"""
Module disjoncteurs.py - Calcul des pertes des appareils de coupure.
"""

class BreakerCalculator:
    @staticmethod
    def calculate_loss(p_nominal: float, i_nominal: float, i_real: float, load_factor: float = None) -> float:
        """
        Calcule la perte thermique réelle d'un disjoncteur.
        P_réelle = P_nominale * (I_réel / I_nominal)^2
        Si le facteur de charge est fourni : I_réel = I_nominal * load_factor
        """
        if load_factor is not None:
            return p_nominal * (load_factor ** 2)
        
        if i_nominal <= 0:
            return 0.0
        
        return p_nominal * ((i_real / i_nominal) ** 2)

    @staticmethod
    def effective_loss(p_nom_w: float, charge_pct: float) -> float:
        """
        Calcule les pertes effectives en fonction du taux de charge (%).
        """
        return p_nom_w * (charge_pct / 100.0) ** 2