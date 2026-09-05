"""
Module app.py - Interface AC Sizing Pro Clarke Energy
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

from calculs import UnitConverter, ThermalEngine
from local import BuildingThermalCalculator
from base_donnees import DatabaseManager
from rapport import PDFReportGenerator

# ----------------------------------------------------
# CONFIGURATION DE LA PAGE & THÈME CLARKE ENERGY
# ----------------------------------------------------
st.set_page_config(
    page_title="AC Sizing Pro | Clarke Energy",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GESTION DU LOGO ---
logo_path = "assets/Logo2.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.warning("Logo Clarke Energy non trouvé (assets/Logo2.png)")

st.sidebar.caption("Calcul Climatisation Local Technique")
st.sidebar.markdown("---")

# --- SÉLECTEUR DE THÈME ---
st.sidebar.markdown("### Apparence")
theme_choice = st.sidebar.radio(
    "Choisir le thème visuel :",
    ["☀️ Mode Clair", "🌙 Mode Sombre"],
    index=0
)
st.sidebar.markdown("---")

# --- INJECTION CSS DYNAMIQUE & THÈME PLOTLY ---
if theme_choice == "☀️ Mode Clair":
    plotly_template = "plotly_white"
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', -apple-system, sans-serif !important;
                background-color: #F8FAFC !important;
                color: #1E293B !important;
            }
            h1, h2, h3, h4, h5, h6, .stTitle {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 700 !important;
                color: #0F172A !important;
            }
            [data-testid="stSidebar"] {
                background-color: #F8FAFC !important;
                border-right: 1px solid #1E293B;
            }
            [data-testid="stSidebar"] * {
                color: #0F172A !important;
            }
            /* Forcer la couleur du texte sur tous les composants courants */
            p, div, span, label, .stMarkdown, .stCaption, .stDataFrame, .stTable,
            .stMetric, .stMetricValue, .stMetricLabel, .stSelectbox, .stNumberInput,
            .stTextInput, .stTextArea, .stSlider, .stRadio, .stCheckbox, .stMultiselect {
                color: #1E293B !important;
            }
            /* Valeurs des métriques en bleu, labels en gris */
            .stMetricValue {
                color: #2B6CB0 !important;
            }
            .stMetricLabel {
                color: #64748B !important;
            }

            .metric-card {
                background-color: #FFFFFF;
                border-radius: 8px;
                padding: 18px;
                border: 1px solid #E2E8F0;
                border-left: 5px solid #3182CE;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            }
            .metric-value {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-size: 26px;
                font-weight: 800;
                color: #2B6CB0;
                margin-top: 4px;
            }
            .metric-label {
                font-family: 'Inter', sans-serif !important;
                font-size: 12px;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
            }
            .stButton>button {
                font-family: 'Inter', sans-serif !important;
                background-color: #3182CE !important;
                color: #FFFFFF !important;
                border-radius: 6px;
                border: none;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    plotly_template = "plotly_dark"
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
            html, body, [class*="css"], .stApp {
                font-family: 'Inter', -apple-system, sans-serif !important;
                background-color: #0A1120 !important;
                color: #F7FAFC !important;
            }
            h1, h2, h3, h4, h5, h6, .stTitle {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-weight: 700 !important;
                color: #FFFFFF !important;
            }
            [data-testid="stSidebar"] {
                background-color: #0F172A !important;
                border-right: 1px solid #1E293B;
            }
            .metric-card {
                background-color: #162032;
                border-radius: 8px;
                padding: 18px;
                border: 1px solid #1E293B;
                border-left: 5px solid #4171DE;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            }
            .metric-value {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
                font-size: 26px;
                font-weight: 800;
                color: #63B3ED;
                margin-top: 4px;
            }
            .metric-label {
                font-family: 'Inter', sans-serif !important;
                font-size: 12px;
                font-weight: 600;
                color: #A0AEC0;
                text-transform: uppercase;
            }
            .stButton>button {
                font-family: 'Inter', sans-serif !important;
                background-color: #3182CE !important;
                color: #FFFFFF !important;
                border-radius: 6px;
                border: none;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

# Appliquer le template Plotly globalement
px.defaults.template = plotly_template

# ----------------------------------------------------
# INITIALISATION DES ÉTATS DE SESSION
# ----------------------------------------------------
if "project" not in st.session_state:
    st.session_state.project = {
        "nom": "Projet Clarke Energy",
        "client": "",
        "reference": "",
        "ingenieur": "",
        "date": datetime.today().strftime('%d/%m/%Y'),
        "statut": "Avant-Projet (APS)",
        "t_ext": 40.0,
        "t_int": 25.0
    }

if "local" not in st.session_state:
    st.session_state.local = {
        "length": 8.0, "width": 5.0, "height": 3.5,
        "wall_type": "Mur isolé (5 cm)", "roof_type": "Toiture sandwich isolée",
        "lighting_w_m2": 10.0, "ach": 1.5, "occupants": 1
    }

# --- Configuration des Armoires A ---
if "config_armoires" not in st.session_state:
    st.session_state.config_armoires = {
        "nb": 1,
        "pertes_unitaire": PERTES_ARMOIRE_A_UNITAIRE_W,
        "pertes_totales": PERTES_ARMOIRE_A_UNITAIRE_W
    }
if "nb_armoires_a" not in st.session_state:
    st.session_state.nb_armoires_a = 1  # Ancienne variable (plus utilisée par l'UI)

# --- Configuration TGBT ---
if "tgbt_components" not in st.session_state:
    st.session_state.tgbt_components = []
if "pertes_tgbt_w" not in st.session_state:
    st.session_state.pertes_tgbt_w = 0.0

# --- Configuration des Armoires A ---
if "config_armoires" not in st.session_state:
    st.session_state.config_armoires = {
        "nb": 1,
        "pertes_unitaire": PERTES_ARMOIRE_A_UNITAIRE_W,
        "pertes_totales": PERTES_ARMOIRE_A_UNITAIRE_W
    }
if "nb_armoires_a" not in st.session_state:
    st.session_state.nb_armoires_a = 1  

if "armoire_a_quantite" not in st.session_state:
    st.session_state.armoire_a_quantite = 1  

# --- Configuration Armoire Auxiliaire ---
if "armoires_aux_components" not in st.session_state:
    st.session_state.armoires_aux_components = []
if "armoires_aux_quantite" not in st.session_state:
    st.session_state.armoires_aux_quantite = 1
if "pertes_armoires_aux_w" not in st.session_state:
    st.session_state.pertes_armoires_aux_w = 0.0

# --- Résultats du Bilan Thermique ---
if "bilan_results" not in st.session_state:
    st.session_state.bilan_results = {
        'q_equipements': 0.0,
        'q_eclairage': 0.0,
        'q_interne': 0.0,
        'q_transmission': 0.0,
        'q_ventilation': 0.0,
        'q_enveloppe': 0.0,
        'q_totale_brut': 0.0,
        'q_totale_design': 0.0,
        'puissance_kw': 0.0,
        'puissance_btu': 0.0,
        'puissance_tr': 0.0,
        'debit_air': 0.0,
        'marge_pourcent': 15,
        'q_interne_display': 0.0,
        'q_enveloppe_display': 0.0,
        'pie_data': pd.DataFrame(),
        'sens_data': pd.DataFrame()
    }
if "bilan_computed" not in st.session_state:
    st.session_state.bilan_computed = False

# --- Résultats de calcul (pour les autres pages) ---
if "pertes_armoires_w" not in st.session_state:
    st.session_state.pertes_armoires_w = PERTES_ARMOIRE_A_UNITAIRE_W

if "apports_batiment_w" not in st.session_state:
    st.session_state.apports_batiment_w = 0.0

if "bilan" not in st.session_state:
    st.session_state.bilan = {}
# ----------------------------------------------------
# INITIALISATION DE LA BASE DE DONNÉES
# ----------------------------------------------------
db_mgr = DatabaseManager()

# ----------------------------------------------------
# MENU DE NAVIGATION
# ----------------------------------------------------

menu = st.sidebar.radio("Navigation", ["Projet", "Local", "TGBT", "Armoire A", "Armoire Auxiliaire", "Bilan Thermique", "Rapport"])  

# ----------------------------------------------------
# PAGE : Projet (données administratives)
# ----------------------------------------------------
if menu == "Projet":
    st.title("Projet & Identification")
    st.caption("Renseignez les données administratives du projet.")
    st.markdown("---")

    with st.form("project_details_form"):
        st.subheader("Informations Générales")
        c1, c2 = st.columns(2)
        with c1:
            nom_projet = st.text_input("Nom du Projet / Site", value=st.session_state.project.get("nom", ""))
            client_nom = st.text_input("Client / Société", value=st.session_state.project.get("client", ""))
            affaire_ref = st.text_input("N° d'Affaire / Référence", value=st.session_state.project.get("reference", ""))
        with c2:
            ingenieur = st.text_input("Ingénieur Études AC / Auteur", value=st.session_state.project.get("ingenieur", ""))
            date_projet = st.date_input("Date de l'Étude", value=datetime.today())
            statut_projet = st.selectbox("Statut du Document", ["Avant-Projet (APS)", "Étude Détaillée (APD)", "Conception Finale (EXE)"],
                                         index=["Avant-Projet (APS)", "Étude Détaillée (APD)", "Conception Finale (EXE)"].index(st.session_state.project.get("statut", "Avant-Projet (APS)")))

        # Températures de calcul
        st.subheader("Conditions de Dimensionnement")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            t_ext = st.number_input("Température extérieure (°C)", min_value=-10.0, max_value=60.0, value=float(st.session_state.project.get("t_ext", 40.0)), step=0.5)
        with col_t2:
            t_int = st.number_input("Température intérieure souhaitée (°C)", min_value=10.0, max_value=40.0, value=float(st.session_state.project.get("t_int", 25.0)), step=0.5)

        submit_btn = st.form_submit_button("💾 Enregistrer les données du Projet")

    if submit_btn:
        st.session_state.project["nom"] = nom_projet
        st.session_state.project["client"] = client_nom
        st.session_state.project["reference"] = affaire_ref
        st.session_state.project["ingenieur"] = ingenieur
        st.session_state.project["date"] = date_projet.strftime("%d/%m/%Y")
        st.session_state.project["statut"] = statut_projet
        st.session_state.project["t_ext"] = t_ext
        st.session_state.project["t_int"] = t_int
        st.success("Données du projet mises à jour avec succès !")
        st.rerun()

    # Aperçu du cartouche
    st.markdown("---")
    st.subheader("📋 Aperçu du Rapport")
    st.markdown(f"""
        <div style="background-color: var(--background-color, #162032); border: 1px solid #1E293B; border-radius: 8px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #3182CE; padding-bottom: 10px; margin-bottom: 15px;">
                <span style="font-weight: 700; font-size: 18px; color: #FFFFFF;">PROJET : {st.session_state.project.get('nom', 'N/A')}</span>
                <span style="background-color: #3182CE; color: white; padding: 2px 10px; border-radius: 4px; font-weight: 600; font-size: 13px;">{st.session_state.project.get('statut', 'APS')}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; font-size: 14px;">
                <div><strong style="color: #A0AEC0;">Client :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('client', 'N/A')}</span></div>
                <div><strong style="color: #A0AEC0;">N° Affaire :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('reference', 'N/A')}</span></div>
                <div><strong style="color: #A0AEC0;">Ingénieur BE :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('ingenieur', 'N/A')}</span></div>
                <div><strong style="color: #A0AEC0;">Date :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('date', datetime.today().strftime('%d/%m/%Y'))}</span></div>
                <div><strong style="color: #A0AEC0;">T_ext :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('t_ext', 40.0)} °C</span></div>
                <div><strong style="color: #A0AEC0;">T_int :</strong> <span style="color: #F7FAFC;">{st.session_state.project.get('t_int', 25.0)} °C</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
# ----------------------------------------------------
# PAGE : TGBT
# ----------------------------------------------------
elif menu == "TGBT":
    st.title("📊 Gestion du TGBT (Tableau Général Basse Tension)")
    st.caption("Composez votre TGBT en ajoutant ses composants. Les dissipations thermiques seront automatiquement sommées pour le bilan thermique.")
    st.markdown("---")

    # Initialisation
    if 'tgbt_components' not in st.session_state:
        st.session_state.tgbt_components = []
    if 'pertes_tgbt_w' not in st.session_state:
        st.session_state.pertes_tgbt_w = 0.0

    # Base de données des composants (avec les jeux de barres calibrés)
    COMPOSANTS_TGBT = {
        # Jeux de barres (Pertes par mètre, cuivre: loi de joule)
        "Jeu de barres - 250A (~20 W/m)": 20,
        "Jeu de barres - 400A (~40 W/m)": 40,
        "Jeu de barres - 630A (~80 W/m)": 80,
        "Jeu de barres - 1000A (~150 W/m)": 150,
        "Jeu de barres - 1250A (~200 W/m)": 200,
        "Jeu de barres - 1600A (~300 W/m)": 300,
        "Jeu de barres - 2000A (~450 W/m)": 450,
        "Jeu de barres - 2500A (~650 W/m)": 650,
        "Jeu de barres - 3200A (~900 W/m)": 900,   
        "Jeu de barres - 4000A (~1300 W/m)": 1300,
        # Disjoncteurs (pertes: loi de joule)
        "Disjoncteur de branchement (630A)": 220,
        "Disjoncteur de branchement (400A)": 150,
        "Disjoncteur général (250A)": 120,
        "Disjoncteur divisionnaire (63A)": 25,
        "Disjoncteur divisionnaire (32A)": 15,
        "Disjoncteur divisionnaire (16A)": 10,
        "Interrupteur-sectionneur (630A)": 100,
        # Contacteurs / Variateurs
        "Contacteur (puissance)": 50,
        "Contacteur (auxiliaire)": 20,
        # Autres
        "Parafoudre (type 1+2)": 15,
        "Transformateur de courant (TC)": 5,
        "Compteur / Analyseur": 15,
        "Bornier de raccordement (jeu)": 10,
        "Ventilateur d'armoire (230V)": 30,
        "Alimentation 24VDC": 25,
        "Coffret vide (enveloppe)": 50
    }

    # --- Formulaire d'ajout ---
    with st.form(key="add_tgbt_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            composant_choisi = st.selectbox("Sélectionnez le composant", list(COMPOSANTS_TGBT.keys()))
            puissance_unitaire = COMPOSANTS_TGBT[composant_choisi]
            st.caption(f"⚡ Dissipation typique : **{puissance_unitaire} W** par unité")
        with col2:
            quantite = st.number_input("Quantité", min_value=1, step=1, value=1)
        with col3:
            total_ligne = puissance_unitaire * quantite
            st.metric("Total pour ce composant", f"{total_ligne} W")
        
        submitted = st.form_submit_button("➕ Ajouter au TGBT", type="primary")
        if submitted:
            st.session_state.tgbt_components.append({
                "nom": composant_choisi,
                "puissance_unitaire": puissance_unitaire,
                "quantite": quantite,
                "total": total_ligne
            })
            st.success(f"✅ '{composant_choisi}' x{quantite} ajouté !")
            st.rerun()

    st.markdown("---")

    # --- Affichage de la composition ---
    if st.session_state.tgbt_components:
        df = pd.DataFrame(st.session_state.tgbt_components)
        df_display = df.rename(columns={
            "nom": "Composant",
            "puissance_unitaire": "Puissance unitaire (W)",
            "quantite": "Qté",
            "total": "Total (W)"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        total_general = df["total"].sum()
        st.session_state.pertes_tgbt_w = total_general
        st.metric("Puissance dissipée totale du TGBT", f"{total_general:.0f} W", delta=f"{total_general/1000:.2f} kW")
        
        if st.button("🗑️ Réinitialiser la composition", type="secondary"):
            st.session_state.tgbt_components = []
            st.session_state.pertes_tgbt_w = 0.0
            st.rerun()
    else:
        st.info("Aucun composant ajouté! Utilisez le formulaire pour composer votre TGBT.")
        st.session_state.pertes_tgbt_w = 0.0

# ----------------------------------------------------
# PAGE : Armoires A
# ----------------------------------------------------
elif menu == "Armoire A":
    st.title("Gestion des Armoires A")
    st.caption("La composition interne des Armoires A est fixe (selon plan type). Indiquez simplement le nombre d'armoires identiques installées.")
    st.markdown("---")

    # Composition FIXE d'UNE Armoire A (basée sur le plan SIDENOR)
    # Format: (Désignation, Puissance unitaire en W, Quantité dans 1 armoire)
    COMPOSANTS_ARMOIRE_A = [
        ("Disjoncteur général 400A", 150, 1),
        ("Disjoncteur 250A (départs)", 120, 2),
        ("Disjoncteur 100A (départs)", 40, 4),
        ("Départ moteur 11kW (protection + contacteur)", 25, 6),
        ("Départ moteur 9kW (protection + contacteur)", 20, 4),
        ("Départ moteur 1.2kW (protection + contacteur)", 10, 8),
        ("Variateurs 45kW", 450, 1),   # ~10W/kW
        ("Variateurs 18.5kW", 185, 4), # ~10W/kW
        ("Jeu de barres 400A (2m)", 80, 1),  # 40W/m * 2m
        ("Ventilation / Accessoires", 50, 1)
    ]

    # Calcul des pertes pour UNE armoire
    pertes_unitaire = 0.0
    st.subheader("📋 Composition type d'une Armoire A")
    
    data_rows = []
    for nom, pu, qte in COMPOSANTS_ARMOIRE_A:
        total_ligne = pu * qte
        pertes_unitaire += total_ligne
        data_rows.append({"Composant": nom, "Puissance unitaire (W)": pu, "Qté": qte, "Total (W)": total_ligne})
    
    df_unitaire = pd.DataFrame(data_rows)
    st.dataframe(df_unitaire, use_container_width=True, hide_index=True)
    st.metric("Pertes pour 1 Armoire A", f"{pertes_unitaire:.0f} W", delta=f"{pertes_unitaire/1000:.2f} kW")

    st.markdown("---")

    # --- Sélection de la quantité ---
    st.subheader("Nombre d'armoires identiques")
    quantite = st.number_input("Nombre d'Armoires A identiques", min_value=0, max_value=20, step=1, value=1)
    
    if st.button("💾 Enregistrer la quantité", type="primary"):
        st.session_state.armoire_a_quantite = quantite
        st.session_state.pertes_armoires_w = pertes_unitaire * quantite
        st.success(f"✅ {quantite} armoire(s) A enregistrée(s). Puissance totale : {st.session_state.pertes_armoires_w:.0f} W")

    st.markdown("---")

    # --- Affichage du total enregistré ---
    if 'armoire_a_quantite' in st.session_state and st.session_state.armoire_a_quantite > 0:
        st.subheader("Récapitulatif")
        st.metric("Nombre d'armoires", st.session_state.armoire_a_quantite)
        st.metric("Puissance dissipée totale (Armoires A)", f"{st.session_state.pertes_armoires_w:.0f} W", 
                  delta=f"{st.session_state.pertes_armoires_w/1000:.2f} kW")
    else:
        st.info("Aucune armoire A enregistrée pour le moment. Définissez le nombre ci-dessus.")
        st.session_state.pertes_armoires_w = 0.0
        
# ----------------------------------------------------
# PAGE : Armoire Auxiliaire
# ----------------------------------------------------
elif menu == "Armoire Auxiliaire":
    st.title("Gestion des Armoires Auxiliaires")
    st.caption("Définissez la composition d'une armoire auxiliaire type, puis indiquez le nombre d'exemplaires identiques.")
    st.markdown("---")

    # Initialisation
    if 'armoires_aux_components' not in st.session_state:
        st.session_state.armoires_aux_components = []
    if 'armoires_aux_quantite' not in st.session_state:
        st.session_state.armoires_aux_quantite = 1
    if 'pertes_armoires_aux_w' not in st.session_state:
        st.session_state.pertes_armoires_aux_w = 0.0

    # --- 1. Sélection de la quantité (multiplicateur) ---
    col_qty, _ = st.columns([1, 2])
    with col_qty:
        quantite = st.number_input("Nombre d'armoires auxiliaires identiques", min_value=1, step=1, value=st.session_state.armoires_aux_quantite)
        st.session_state.armoires_aux_quantite = quantite

    st.markdown("---")

    # --- 2. Composition libre ---
    COMPOSANTS_AUX = {
        "Disjoncteur général (160A)": 80,
        "Disjoncteur divisionnaire (63A)": 25,
        "Disjoncteur divisionnaire (32A)": 15,
        "Disjoncteur divisionnaire (16A)": 10,
        "Interrupteur-sectionneur (160A)": 60,
        "Contacteur (puissance)": 50,
        "Jeu de barres - 160A (~10 W/m)": 10,
        "Bornier de raccordement (jeu)": 10,
        "Ventilateur d'armoire (230V)": 30,
        "Alimentation 24VDC": 25,
        "Coffret vide (enveloppe)": 50
    }

    with st.form(key="add_aux_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            composant_choisi = st.selectbox("Sélectionnez un composant", list(COMPOSANTS_AUX))
            puissance_unitaire = COMPOSANTS_AUX[composant_choisi]
            st.caption(f"⚡ Dissipation : **{puissance_unitaire} W**")
        with col2:
            qte_composant = st.number_input("Qté", min_value=1, step=1, value=1)
        with col3:
            total_ligne = puissance_unitaire * qte_composant
            st.metric("Total", f"{total_ligne} W")
        
        submitted = st.form_submit_button("➕ Ajouter ce composant", type="primary")
        if submitted:
            st.session_state.armoires_aux_components.append({
                "nom": composant_choisi,
                "puissance_unitaire": puissance_unitaire,
                "quantite": qte_composant,
                "total": total_ligne
            })
            st.success(f"Ajouté !")
            st.rerun()

    st.markdown("---")

    # --- 3. Affichage de la composition de l'armoire type ---
    if st.session_state.armoires_aux_components:
        df = pd.DataFrame(st.session_state.armoires_aux_components)
        df_display = df.rename(columns={
            "nom": "Composant",
            "puissance_unitaire": "Puissance unitaire (W)",
            "quantite": "Qté",
            "total": "Total (W)"
        })
        st.subheader("Composition de l'armoire type")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        total_type = df["total"].sum()
        # Calcul du total multiplié par la quantité
        total_general = total_type * st.session_state.armoires_aux_quantite
        st.session_state.pertes_armoires_aux_w = total_general

        st.metric("Puissance pour 1 armoire type", f"{total_type:.0f} W")
        st.metric("Puissance totale (x{})".format(st.session_state.armoires_aux_quantite), 
                  f"{total_general:.0f} W", delta=f"{total_general/1000:.2f} kW")

        if st.button("🗑️ Réinitialiser la composition type", type="secondary"):
            st.session_state.armoires_aux_components = []
            st.session_state.pertes_armoires_aux_w = 0.0
            st.rerun()
    else:
        st.info("Aucun composant pour l'armoire auxiliaire! Utilisez le formulaire ci-dessus.")
        st.session_state.pertes_armoires_aux_w = 0.0

# ----------------------------------------------------
# PAGE : Local (bâtiment)
# ----------------------------------------------------
elif menu == "Local":
    st.title("Local Électrique & Enveloppe du Bâtiment")
    st.caption("Définissez les caractéristiques du local pour calculer les apports thermiques.")
    st.markdown("---")

    with st.form("local_parameters_form"):
        st.subheader("1. Géométrie et Parois")
        col_dim1, col_dim2 = st.columns(2)
        with col_dim1:
            length = st.number_input("Longueur (m)", min_value=1.0, max_value=100.0, value=float(st.session_state.local["length"]), step=0.5)
            width = st.number_input("Largeur (m)", min_value=1.0, max_value=100.0, value=float(st.session_state.local["width"]), step=0.5)
            height = st.number_input("Hauteur (m)", min_value=1.5, max_value=20.0, value=float(st.session_state.local["height"]), step=0.1)
        with col_dim2:
            wall_options = list(BuildingThermalCalculator.U_VALUES.keys())
            wall_type = st.selectbox("Type de Murs", wall_options, index=wall_options.index(st.session_state.local["wall_type"]))
            roof_type = st.selectbox("Type de Toiture", wall_options, index=wall_options.index(st.session_state.local["roof_type"]))

        st.subheader("2. Éclairage & Infiltration")
        col_int1, col_int2, col_int3 = st.columns(3)
        with col_int1:
            lighting = st.number_input("Éclairage (W/m²)", min_value=0.0, max_value=50.0, value=float(st.session_state.local["lighting_w_m2"]), step=1.0)
        with col_int2:
            ach = st.number_input("Renouvellement d'air (ACH)", min_value=0.0, max_value=10.0, value=float(st.session_state.local["ach"]), step=0.1)
        with col_int3:
            occupants = st.number_input("Nombre d'occupants", min_value=0, max_value=20, value=int(st.session_state.local["occupants"]), step=1)

        submit_local = st.form_submit_button("💾 Enregistrer & Calculer les apports")

    if submit_local:
        st.session_state.local["length"] = length
        st.session_state.local["width"] = width
        st.session_state.local["height"] = height
        st.session_state.local["wall_type"] = wall_type
        st.session_state.local["roof_type"] = roof_type
        st.session_state.local["lighting_w_m2"] = lighting
        st.session_state.local["ach"] = ach
        st.session_state.local["occupants"] = occupants
        st.success("Paramètres du local enregistrés !")
        st.rerun()

    # Calcul et affichage
    res_local = BuildingThermalCalculator.compute_building_gains(
        st.session_state.local["length"],
        st.session_state.local["width"],
        st.session_state.local["height"],
        st.session_state.local["wall_type"],
        st.session_state.local["roof_type"],
        st.session_state.project["t_ext"],
        st.session_state.project["t_int"],
        st.session_state.local["lighting_w_m2"],
        st.session_state.local["ach"],
        st.session_state.local["occupants"]
    )

    total_bat = res_local["total_gains_w"]
    st.session_state.apports_batiment_w = total_bat

    details = res_local["details"]
    st.markdown("---")
    st.subheader("Bilan des apports du local")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transmission", f"{details['transmission_w']:.1f} W", f"{details['transmission_w']/1000:.2f} kW")
    col2.metric("Éclairage + Occupants", f"{details['lighting_w']:.1f} W", f"{details['lighting_w']/1000:.2f} kW")
    col3.metric("Ventilation / Infiltration", f"{details['ventilation_w']:.1f} W", f"{details['ventilation_w']/1000:.2f} kW")
    col4.metric("Total local", f"{total_bat:.1f} W", f"{total_bat/1000:.2f} kW", delta_color="inverse")

    # Graphique de répartition
    df_chart = pd.DataFrame({
        "Poste": ["Transmission", "Éclairage+Occupants", "Ventilation"],
        "Watts": [details['transmission_w'], details['lighting_w'], details['ventilation_w']]
    })
    fig = px.bar(df_chart, x="Poste", y="Watts", text_auto=".1f", color="Poste", title="Répartition des apports du local")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# PAGE : Bilan Thermique (synthèse)
# ----------------------------------------------------
elif menu == "Bilan Thermique":
    st.title("Bilan Thermique et Dimensionnement AC")
    st.caption(f"Projet : {st.session_state.project.get('nom', 'Projet sans nom')}")
    st.markdown("---")

    # ------------------------------------------------------------
    # 1. INITIALIZE SESSION STATE FOR RESULTS (default = 0 / empty)
    # ------------------------------------------------------------
    if 'bilan_results' not in st.session_state:
        st.session_state.bilan_results = {
            'q_equipements': 0.0,
            'q_eclairage': 0.0,
            'q_interne': 0.0,
            'q_transmission': 0.0,
            'q_ventilation': 0.0,
            'q_enveloppe': 0.0,
            'q_totale_brut': 0.0,
            'q_totale_design': 0.0,
            'puissance_kw': 0.0,
            'puissance_btu': 0.0,
            'puissance_tr': 0.0,
            'debit_air': 0.0,
            'marge_pourcent': 15,
            'q_interne_display': 0.0,
            'q_enveloppe_display': 0.0,
            # for pie chart
            'pie_data': pd.DataFrame(),
            # for sensitivity line
            'sens_data': pd.DataFrame()
        }
        st.session_state.bilan_computed = False

    # ------------------------------------------------------------
    # 2. READ INPUTS FROM SESSION STATE 
    # ------------------------------------------------------------
    # Pertes des équipements
  
    pertes_armoires = st.session_state.get("pertes_armoires_w", 0.0) 
    pertes_tgbt = st.session_state.get("pertes_tgbt_w", 0.0)
    pertes_armoires_aux = st.session_state.get("pertes_armoires_aux_w", 0.0)

    # Données du local
    local_data = st.session_state.get("local", {})
    length = local_data.get("length", 0.0)
    width = local_data.get("width", 0.0)
    height = local_data.get("height", 0.0)
    wall_type = local_data.get("wall_type", "Mur isolé (5 cm)")
    roof_type = local_data.get("roof_type", "Toiture sandwich isolée")
    lighting_w_m2 = local_data.get("lighting_w_m2", 0.0)
    ach = local_data.get("ach", 0.0)

    # Données du projet (températures)
    project_data = st.session_state.get("project", {})
    t_ext = project_data.get("t_ext", 35.0)
    t_int = project_data.get("t_int", 22.0)
    delta_t = max(0.0, t_ext - t_int)

    # ------------------------------------------------------------
    # 3. BUTTON TO TRIGGER CALCULATION
    # ------------------------------------------------------------
    if st.button("🔄 Calculer le Bilan Thermique", type="primary"):
        # ---- Run all calculations ----
        # 3.1 Apports Internes
        q_equipements = pertes_armoires + pertes_tgbt + pertes_armoires_aux
        surface = length * width
        q_eclairage = lighting_w_m2 * surface
        q_interne = q_equipements + q_eclairage

        # 3.2 Apports par l'Enveloppe
        from local import BuildingThermalCalculator
        u_wall = BuildingThermalCalculator.U_VALUES.get(wall_type, 0.5)
        u_roof = BuildingThermalCalculator.U_VALUES.get(roof_type, 0.35)

        surface_murs = 2 * (length + width) * height
        surface_toit = surface
        q_murs = u_wall * surface_murs * delta_t
        q_toit = u_roof * surface_toit * delta_t
        q_transmission = q_murs + q_toit

        volume = surface * height
        debit_air = volume * ach
        q_ventilation = 0.34 * debit_air * delta_t
        q_enveloppe = q_transmission + q_ventilation

        # 3.3 Besoin de refroidissement
        q_totale_brut = q_interne + q_enveloppe
        marge_pourcent = 15
        facteur_marge = 1 + (marge_pourcent / 100.0)
        q_totale_design = q_totale_brut * facteur_marge

        # 3.4 Unités
        puissance_kw = q_totale_design / 1000
        puissance_btu = q_totale_design * 3.412142
        puissance_tr = q_totale_design / 3516.85
        debit_air_estime = q_totale_design / (0.34 * delta_t) if delta_t > 0 else 0.0

        # ---- Store results in session_state ----
        st.session_state.bilan_results.update({
            'q_equipements': q_equipements,
            'q_eclairage': q_eclairage,
            'q_interne': q_interne,
            'q_transmission': q_transmission,
            'q_ventilation': q_ventilation,
            'q_enveloppe': q_enveloppe,
            'q_totale_brut': q_totale_brut,
            'q_totale_design': q_totale_design,
            'puissance_kw': puissance_kw,
            'puissance_btu': puissance_btu,
            'puissance_tr': puissance_tr,
            'debit_air': debit_air_estime,
            'marge_pourcent': marge_pourcent,
            'q_interne_display': q_interne,
            'q_enveloppe_display': q_enveloppe,
        })

        # ---- Pie chart data ----
        df_pie = pd.DataFrame({
            "Source": ["Équipements", "Enveloppe", "Éclairage"],
            "Watts": [q_equipements, q_enveloppe, q_eclairage]
        })
        df_pie = df_pie[df_pie["Watts"] > 0]
        st.session_state.bilan_results['pie_data'] = df_pie

        # ---- Sensitivity data ----
        plage_temp = list(range(25, 51, 5))
        puissances = []
        for t in plage_temp:
            delta_t_sim = max(0.0, t - t_int)
            q_murs_sim = u_wall * surface_murs * delta_t_sim
            q_toit_sim = u_roof * surface_toit * delta_t_sim
            q_transmission_sim = q_murs_sim + q_toit_sim
            q_ventilation_sim = 0.34 * debit_air * delta_t_sim
            q_enveloppe_sim = q_transmission_sim + q_ventilation_sim
            q_totale_sim = (q_interne + q_enveloppe_sim) * facteur_marge
            puissances.append(q_totale_sim / 1000)
        df_sens = pd.DataFrame({"Température Extérieure (°C)": plage_temp, "Puissance AC (kW)": puissances})
        st.session_state.bilan_results['sens_data'] = df_sens

        st.session_state.bilan_computed = True

    # ------------------------------------------------------------
    # 4. DISPLAY RESULTS (ZERO BY DEFAULT)
    # ------------------------------------------------------------
    results = st.session_state.bilan_results
    computed = st.session_state.bilan_computed

    # ---- Display metrics ----
    st.subheader("Synthèse du Bilan de Puissance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="Puissance Frigorifique Nécessaire",
        value=f"{results['puissance_btu']:.0f} BTU/h" if computed else "0 BTU/h",
        delta=f"{results['puissance_kw']:.2f} kW" if computed else "0.00 kW"
    )
    col2.metric(
        label="Capacité Recommandée",
        value=f"{results['puissance_tr']:.2f} TR" if computed else "0.00 TR",
        delta=f"{results['marge_pourcent']}% de marge" if computed else "0% de marge"
    )
    col3.metric(
        label="Équivalent en kW",
        value=f"{results['puissance_kw']:.2f} kW" if computed else "0.00 kW"
    )
    col4.metric(
        label="Débit d'Air Estimé",
        value=f"{results['debit_air']:.0f} m³/h" if computed and results['debit_air'] > 0 else "N/A",
        help="Basé sur un écart de température de 10°C à la soufflante"
    )

    st.markdown("---")

    # ---- Detail of thermal loads ----
    st.subheader("Détail des Apports Thermiques")
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.caption("**Apports Internes (Équipements, éclairage)**")
        if computed:
            st.write(f"- 🖥️ Équipements électriques : **{results['q_equipements']:.0f} W**")
            st.write(f"- 💡 Éclairage : **{results['q_eclairage']:.0f} W**")
            st.write(f"**Total Interne : {results['q_interne']:.0f} W**")
        else:
            st.write("- 🖥️ Équipements électriques : **0 W**")
            st.write("- 💡 Éclairage : **0 W**")
            st.write("**Total Interne : 0 W**")

        st.caption("**Apports par l'Enveloppe (Bâtiment)**")
        if computed:
            st.write(f"- 🧱 Murs & Toit : **{results['q_transmission']:.0f} W**")
            st.write(f"- 🌬️ Renouvellement d'air : **{results['q_ventilation']:.0f} W**")
            st.write(f"**Total Enveloppe : {results['q_enveloppe']:.0f} W**")
        else:
            st.write("- 🧱 Murs & Toit : **0 W**")
            st.write("- 🌬️ Renouvellement d'air : **0 W**")
            st.write("**Total Enveloppe : 0 W**")

        st.divider()
        if computed:
            st.metric("**Charge Thermique Totale (Brute)**", f"{results['q_totale_brut']/1000:.2f} kW")
            st.metric(f"**Charge avec marge ({results['marge_pourcent']}%)**", f"{results['q_totale_design']/1000:.2f} kW")
        else:
            st.metric("**Charge Thermique Totale (Brute)**", "0.00 kW")
            st.metric("**Charge avec marge (15%)**", "0.00 kW")

    with col_right:
        if computed:
            df_pie = results['pie_data']
            if not df_pie.empty:
                fig_pie = px.pie(
                    df_pie,
                    values="Watts",
                    names="Source",
                    title="Répartition des Apports Thermiques",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie.update_layout(margin=dict(t=40, b=20, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Aucun apport positif à afficher.")
        else:
            st.info("Cliquez sur 'Calculer le Bilan Thermique' pour voir les graphiques.")

    st.markdown("---")

    # ---- Sensitivity graph ----
    st.subheader("Sensibilité à la Température Extérieure")
    st.caption("Comment la puissance nécessaire du climatiseur évolue avec la chaleur extérieure.")

    if computed and not results['sens_data'].empty:
        df_sens = results['sens_data']
        fig_line = px.line(
            df_sens,
            x="Température Extérieure (°C)",
            y="Puissance AC (kW)",
            markers=True,
            title="Puissance nécessaire en fonction de la chaleur extérieure"
        )
        fig_line.update_traces(line_color='#3182CE', line_width=3, marker_size=10)
        fig_line.update_layout(
            xaxis=dict(gridcolor='#E2E8F0'),
            yaxis=dict(gridcolor='#E2E8F0')
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Calculez le bilan pour visualiser la courbe de sensibilité.")

# ----------------------------------------------------
# PAGE : Rapport PDF
# ----------------------------------------------------
elif menu == "Rapport":
    st.title("📄 Génération du Rapport")
    st.caption("Téléchargez le bilan complet au format PDF.")

    # ------------------------------------------------------------
    # 1. Vérifier que le bilan thermique a été calculé
    # ------------------------------------------------------------
    bilan_disponible = (
        "bilan" in st.session_state 
        and st.session_state.bilan 
        and "total_equipements" in st.session_state.bilan
    )

    if not bilan_disponible:
        st.warning("⚠️ Le bilan thermique n'a pas encore été calculé.")
        st.info("Veuillez d'abord consulter la page **Bilan Thermique** et cliquer sur 'Calculer le Bilan Thermique'.")

        # Bouton de calcul rapide (utilise les nouvelles variables)
        if st.button("🔄 Calculer le bilan maintenant", type="primary"):
            pertes_armoires = st.session_state.get("pertes_armoires_w", 0.0)
            pertes_tgbt = st.session_state.get("pertes_tgbt_w", 0.0)
            pertes_armoires_aux = st.session_state.get("pertes_armoires_aux_w", 0.0)
            apports_bat = st.session_state.get("apports_batiment_w", 0.0)

            total_equip = pertes_armoires + pertes_tgbt + pertes_armoires_aux
            total_global = total_equip + apports_bat

            if total_global == 0:
                st.error("❌ Aucune donnée disponible. Veuillez configurer les équipements et le local.")
            else:
                # Calcul simplifié (sans l'engine complet)
                marge = 0.10  # 10% de marge
                total_design = total_global * (1 + marge)
                
                st.session_state.bilan = {
                    "total_equipements": total_equip,
                    "apports_batiment": apports_bat,
                    "margin_pct": int(marge * 100),
                    "units": {
                        "kw": round(total_design / 1000, 2),
                        "btu_h": round(total_design * 3.412142, 2),
                        "tr": round(total_design / 3516.85, 2)
                    }
                }
                st.success("✅ Bilan calculé avec succès ! Vous pouvez maintenant générer le PDF.")
                st.rerun()

        st.stop()  # Arrêter l'exécution ici si le bilan n'est pas disponible

    # ------------------------------------------------------------
    # 2. Données disponibles → Affichage du rapport
    # ------------------------------------------------------------
    project_data = st.session_state.project
    building_data = st.session_state.local
    bilan_data = st.session_state.bilan

    # --- Récupération des données structurées ---
    armoire_a_quantite = st.session_state.get("armoire_a_quantite", 0)
    pertes_armoires = st.session_state.get("pertes_armoires_w", 0.0)

    tgbt_components = st.session_state.get("tgbt_components", [])
    pertes_tgbt = st.session_state.get("pertes_tgbt_w", 0.0)

    aux_components = st.session_state.get("armoires_aux_components", [])
    aux_quantite = st.session_state.get("armoires_aux_quantite", 0)
    pertes_aux = st.session_state.get("pertes_armoires_aux_w", 0.0)

    # --- Aperçu du rapport ---
    st.subheader("📋 Aperçu du rapport")
    col1, col2, col3 = st.columns(3)
    col1.metric("Projet", project_data.get("nom", "N/A"))
    col2.metric("Client", project_data.get("client", "N/A"))
    col3.metric("Ingénieur", project_data.get("ingenieur", "N/A"))
    st.caption(f"T_ext : {project_data.get('t_ext', 0)} °C | T_int : {project_data.get('t_int', 0)} °C")

    # --- Détail des équipements configurés ---
    with st.expander("Détail des équipements configurés", expanded=False):
        # Armoires A
        st.write(f"**Armoires A :** {armoire_a_quantite} unité(s), pertes totales : **{pertes_armoires:.0f} W** ({pertes_armoires/1000:.2f} kW)")
        
        # TGBT
        if tgbt_components:
            st.write("**TGBT :**")
            df_tgbt = pd.DataFrame(tgbt_components)
            df_tgbt_display = df_tgbt.rename(columns={
                "nom": "Composant",
                "puissance_unitaire": "Puissance (W)",
                "quantite": "Qté",
                "total": "Total (W)"
            })
            st.dataframe(df_tgbt_display, use_container_width=True, hide_index=True)
            st.write(f"**Pertes totales TGBT :** {pertes_tgbt:.0f} W ({pertes_tgbt/1000:.2f} kW)")
        else:
            st.write("**TGBT :** Aucun composant configuré.")

        # Armoires Auxiliaires
        if aux_components:
            st.write(f"**Armoires Auxiliaires :** {aux_quantite} unité(s) identique(s)")
            df_aux = pd.DataFrame(aux_components)
            df_aux_display = df_aux.rename(columns={
                "nom": "Composant",
                "puissance_unitaire": "Puissance (W)",
                "quantite": "Qté",
                "total": "Total (W)"
            })
            st.dataframe(df_aux_display, use_container_width=True, hide_index=True)
            st.write(f"**Pertes totales Auxiliaires :** {pertes_aux:.0f} W ({pertes_aux/1000:.2f} kW)")
        else:
            st.write("**Armoires Auxiliaires :** Aucune configurée.")

    # --- Résumé du bilan ---
    st.markdown("---")
    st.subheader("Résumé du bilan thermique")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pertes équipements", f"{bilan_data['total_equipements']:.0f} W", f"{bilan_data['total_equipements']/1000:.2f} kW")
    col2.metric("Apports bâtiment", f"{bilan_data['apports_batiment']:.0f} W", f"{bilan_data['apports_batiment']/1000:.2f} kW")
    col3.metric("Puissance HVAC", f"{bilan_data['units']['kw']:.2f} kW")
    col4.metric("Capacité recommandée", f"{bilan_data['units']['tr']:.2f} TR")

    st.divider()

    # --- Génération du PDF ---
    if st.button("📄 Générer et télécharger le PDF", use_container_width=True, type="primary"):
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)

        clean_name = "".join(c for c in project_data.get("nom", "Projet") if c.isalnum() or c in (" ", "_")).rstrip()
        pdf_path = os.path.join(output_dir, f"Bilan_{clean_name.replace(' ', '_')}.pdf")

        # Construction des données pour le PDF (compatible avec l'ancienne interface)
        # On adapte les nouvelles données au format attendu par PDFReportGenerator
        armoires_data = {
            "nb": armoire_a_quantite,
            "pertes_totales": pertes_armoires
        }

        # On reconstruit une liste de disjoncteurs à partir des TGBT
        disjoncteurs_data = []
        for comp in tgbt_components:
            if "disjoncteur" in comp["nom"].lower() or "sectionneur" in comp["nom"].lower():
                disjoncteurs_data.append({
                    "nom": comp["nom"],
                    "puissance": comp["puissance_unitaire"],
                    "quantite": comp["quantite"],
                    "total": comp["total"]
                })

        # On reconstruit une liste de variateurs à partir des TGBT
        variateurs_data = []
        for comp in tgbt_components:
            if "contacteur" in comp["nom"].lower() or "variateurs" in comp["nom"].lower():
                variateurs_data.append({
                    "nom": comp["nom"],
                    "puissance": comp["puissance_unitaire"],
                    "quantite": comp["quantite"],
                    "total": comp["total"]
                })

        try:
            # Appel au générateur de PDF
            PDFReportGenerator.generate(
                pdf_path,
                project_data,
                building_data,
                armoires_data,
                disjoncteurs_data,
                variateurs_data,
                bilan_data
            )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="💾 Télécharger le PDF",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.success(f"✅ PDF généré avec succès : {os.path.basename(pdf_path)}")
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération du PDF : {e}")
