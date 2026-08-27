"""
Module templates.py - Définition de l'Armoire A standardisée (Unifilaire Clarke Energy)
"""

# Pertes calculées directement à partir des fiches constructeurs (Danfoss + Schneider 250A)
ARMOIRE_A_DEPARTS_STANDARDS = [
    {"depart": "Arrivée Générale 250A", "type": "Disjoncteur", "equipement": "Schneider NSX250A", "pertes_w": 35.0},
    {"depart": "AERO", "type": "Variateur", "equipement": "Danfoss FC-202 P30K (30 kW)", "pertes_w": 739.0},
    {"depart": "11-P-1", "type": "Variateur", "equipement": "Danfoss FC-202 P18K (18.5 kW)", "pertes_w": 465.0},
    {"depart": "11-P-2", "type": "Variateur", "equipement": "Danfoss FC-202 P18K (18.5 kW)", "pertes_w": 465.0},
    {"depart": "1G-P-1 (1.2 kW)", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 12.0},
    {"depart": "1G-P-2 (1.2 kW)", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 12.0},
    {"depart": "15-P-2 (1.2 kW)", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 12.0},
    {"depart": "12-P-1 (5.5 kW)", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 25.0},
    {"depart": "12-P-2 (5.5 kW)", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 25.0},
    {"depart": "Pompe Eau Refroidissement", "type": "Départ Direct", "equipement": "Disjoncteur + Contacteur", "pertes_w": 30.0},
]

# Calcul des pertes totales d'UNE seule Armoire A
PERTES_ARMOIRE_A_UNITAIRE_W = sum(item["pertes_w"] for item in ARMOIRE_A_DEPARTS_STANDARDS)
