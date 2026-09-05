"""
Module base_donnees.py - Base de données constructeurs (Pertes constructeur directes)
"""
import json
import os

DEFAULT_DB = {
    "variateurs_danfoss_fc202": [
        {"code": "PK37", "puissance_kw": 0.37, "pertes_w": 35},
        {"code": "PK55", "puissance_kw": 0.55, "pertes_w": 42},
        {"code": "PK75", "puissance_kw": 0.75, "pertes_w": 46},
        {"code": "P1K1", "puissance_kw": 1.10, "pertes_w": 58},
        {"code": "P1K5", "puissance_kw": 1.50, "pertes_w": 62},
        {"code": "P2K2", "puissance_kw": 2.20, "pertes_w": 88},
        {"code": "P3K0", "puissance_kw": 3.00, "pertes_w": 116},
        {"code": "P4K0", "puissance_kw": 4.00, "pertes_w": 124},
        {"code": "P5K5", "puissance_kw": 5.50, "pertes_w": 187},
        {"code": "P7K5", "puissance_kw": 7.50, "pertes_w": 225},
        {"code": "P11K", "puissance_kw": 11.0, "pertes_w": 392},
        {"code": "P15K", "puissance_kw": 15.0, "pertes_w": 392},
        {"code": "P18K", "puissance_kw": 18.5, "pertes_w": 465},
        {"code": "P22K", "puissance_kw": 22.0, "pertes_w": 525},
        {"code": "P30K", "puissance_kw": 30.0, "pertes_w": 739},
        {"code": "P37K", "puissance_kw": 37.0, "pertes_w": 698},
        {"code": "P45K", "puissance_kw": 45.0, "pertes_w": 843},
        {"code": "P55K", "puissance_kw": 55.0, "pertes_w": 1083},
        {"code": "P75K", "puissance_kw": 75.0, "pertes_w": 1384},
        {"code": "P90K", "puissance_kw": 90.0, "pertes_w": 1474}
    ],
    "disjoncteurs": [
        {"fabricant": "Schneider Electric", "modele": "NSX100 3P 100A", "pertes_w": 15.0},
        {"fabricant": "Schneider Electric", "modele": "NSX250 3P 250A", "pertes_w": 35.0},
        {"fabricant": "Schneider Electric", "modele": "iC60N 3P 16A", "pertes_w": 7.5},
        {"fabricant": "ABB", "modele": "XT2N 160 3P", "pertes_w": 22.0},
        {"fabricant": "ABB", "modele": "S203 16A", "pertes_w": 6.8}
    ]
}

class DatabaseManager:

    def get_unified_catalog(self) -> dict:
        data = self.load_data()
        catalog = {}

        # 1. Ajout des variateurs Danfoss
        for v in data.get("variateurs_danfoss_fc202", []):
            label = f"Variateur Danfoss FC202 - {v['code']} ({v['puissance_kw']} kW)"
            catalog[label] = v["pertes_w"]

        # 2. Ajout des disjoncteurs (Schneider, ABB, etc.)
        for d in data.get("disjoncteurs", []):
            label = f"Disj. {d['fabricant']} - {d['modele']}"
            catalog[label] = d["pertes_w"]

        # 3. Ajout des jeux de barres
        for b in data.get("jeux_de_barres", []):
            label = f"Jeu de barres - {b['courant']}A ({b['pertes_par_metre']} W/m)"
            catalog[label] = b["pertes_par_metre"]

        # 4. Ajout des accessoires (contacteurs, ventilateurs, etc.)
        for acc in data.get("accessoires", []):
            label = f"{acc['nom']} ({acc['pertes_w']} W)"
            catalog[label] = acc["pertes_w"]

        return catalog
