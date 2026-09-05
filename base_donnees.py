"""
Module base_donnees.py - Base de données constructeurs (Pertes constructeur directes)
"""
import json
import os

DEFAULT_DB = {
    # ------------------------------------------------------------
    # 1. VARIATEURS DANFOSS FC202 (données que vous aviez déjà)
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # 2. DISJONCTEURS SCHNEIDER (extraits de votre fichier Excel)
    # ------------------------------------------------------------
    "disjoncteurs": [
        # --- Acti9 iC60N (modulaires 1-63A) ---
        {"fabricant": "Schneider Electric", "modele": "iC60N 1P 6A (C)", "pertes_w": 5.0},
        {"fabricant": "Schneider Electric", "modele": "iC60N 1P 16A (C)", "pertes_w": 10.0},
        {"fabricant": "Schneider Electric", "modele": "iC60N 3P 32A (C)", "pertes_w": 15.0},
        {"fabricant": "Schneider Electric", "modele": "iC60N 4P 63A (C)", "pertes_w": 25.0},
        {"fabricant": "Schneider Electric", "modele": "iC60N 1P+N 16A (C)", "pertes_w": 8.0},
        
        # --- ComPacT NSX (boîtier moulé 100-630A) ---
        {"fabricant": "Schneider Electric", "modele": "NSX100 3P 100A", "pertes_w": 15.0},
        {"fabricant": "Schneider Electric", "modele": "NSX160 3P 160A", "pertes_w": 22.0},
        {"fabricant": "Schneider Electric", "modele": "NSX250 3P 250A", "pertes_w": 35.0},
        {"fabricant": "Schneider Electric", "modele": "NSX400 3P 400A", "pertes_w": 60.0},
        {"fabricant": "Schneider Electric", "modele": "NSX630 3P 630A", "pertes_w": 90.0},
        
        # --- Masterpact MTZ (disjoncteurs ouverts TGBT) ---
        {"fabricant": "Schneider Electric", "modele": "MTZ1 06 (630-1000A)", "pertes_w": 150},
        {"fabricant": "Schneider Electric", "modele": "MTZ2 20 (1000-2000A)", "pertes_w": 450},
        {"fabricant": "Schneider Electric", "modele": "MTZ3 32 (1600-3200A)", "pertes_w": 900},
        {"fabricant": "Schneider Electric", "modele": "MTZ3 63 (4000-6300A)", "pertes_w": 1300},
        
        # --- TeSys GV (disjoncteurs moteur) ---
        {"fabricant": "Schneider Electric", "modele": "GV2ME14 (6-10A)", "pertes_w": 8.0},
        {"fabricant": "Schneider Electric", "modele": "GV2ME21 (17-23A)", "pertes_w": 12.0},
        {"fabricant": "Schneider Electric", "modele": "GV3P32 (25-32A)", "pertes_w": 15.0},
        {"fabricant": "Schneider Electric", "modele": "GV3P65 (48-65A)", "pertes_w": 30.0},
        {"fabricant": "Schneider Electric", "modele": "GV7RE100 (63-100A)", "pertes_w": 45.0},
        {"fabricant": "Schneider Electric", "modele": "GV7RE250 (160-250A)", "pertes_w": 80.0},
        
        # --- TeSys D (contacteurs) ---
        {"fabricant": "Schneider Electric", "modele": "LC1D09P7 (9A)", "pertes_w": 6.0},
        {"fabricant": "Schneider Electric", "modele": "LC1D18P7 (18A)", "pertes_w": 10.0},
        {"fabricant": "Schneider Electric", "modele": "LC1D32P7 (32A)", "pertes_w": 18.0},
        {"fabricant": "Schneider Electric", "modele": "LC1D65P7 (65A)", "pertes_w": 30.0},
        {"fabricant": "Schneider Electric", "modele": "LC1D150P7 (150A)", "pertes_w": 60.0}
    ],

    # ------------------------------------------------------------
    # 3. JEUX DE BARRES (cuivre, par mètre) - votre liste
    # ------------------------------------------------------------
    "jeux_de_barres": [
        {"courant": 250, "pertes_par_metre": 20},
        {"courant": 400, "pertes_par_metre": 40},
        {"courant": 630, "pertes_par_metre": 80},
        {"courant": 1000, "pertes_par_metre": 150},
        {"courant": 1250, "pertes_par_metre": 200},
        {"courant": 1600, "pertes_par_metre": 300},
        {"courant": 2000, "pertes_par_metre": 450},
        {"courant": 2500, "pertes_par_metre": 650},
        {"courant": 3200, "pertes_par_metre": 900},
        {"courant": 4000, "pertes_par_metre": 1300}
    ],

    # ------------------------------------------------------------
    # 4. ACCESSOIRES (ventilation, alimentation, etc.)
    # ------------------------------------------------------------
    "accessoires": [
        {"nom": "Interrupteur-sectionneur (630A)", "pertes_w": 100},
        {"nom": "Contacteur (puissance)", "pertes_w": 50},
        {"nom": "Contacteur (auxiliaire)", "pertes_w": 20},
        {"nom": "Parafoudre (type 1+2)", "pertes_w": 15},
        {"nom": "Transformateur de courant (TC)", "pertes_w": 5},
        {"nom": "Compteur / Analyseur", "pertes_w": 15},
        {"nom": "Bornier de raccordement (jeu)", "pertes_w": 10},
        {"nom": "Ventilateur d'armoire (230V)", "pertes_w": 30},
        {"nom": "Alimentation 24VDC", "pertes_w": 25},
        {"nom": "Coffret vide (enveloppe)", "pertes_w": 50}
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
