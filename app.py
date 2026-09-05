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
from templates import ARMOIRE_A_DEPARTS_STANDARDS, PERTES_ARMOIRE_A_UNITAIRE_W
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

# --- Configurations détaillées des équipements ---
if "config_armoires" not in st.session_state:
    st.session_state.config_armoires = {
        "nb": 1,
        "pertes_unitaire": PERTES_ARMOIRE_A_UNITAIRE_W,
        "pertes_totales": PERTES_ARMOIRE_A_UNITAIRE_W
    }

if "nb_armoires_a" not in st.session_state:
    st.session_state.nb_armoires_a = 1

if "config_disjoncteurs" not in st.session_state:
    st.session_state.config_disjoncteurs = []

if "config_variateurs" not in st.session_state:
    st.session_state.config_variateurs = []

# --- Résultats des calculs ---
if "pertes_armoires_w" not in st.session_state:
    st.session_state.pertes_armoires_w = PERTES_ARMOIRE_A_UNITAIRE_W

if "pertes_disjoncteurs_w" not in st.session_state:
    st.session_state.pertes_disjoncteurs_w = 0.0

if "pertes_variateurs_w" not in st.session_state:
    st.session_state.pertes_variateurs_w = 0.0

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
menu = st.sidebar.radio("Navigation", [
    "Bilan Thermique", "Projet", "Armoires A",
    "Base Disjoncteurs", "Base Variateurs", "Local", "Rapport"
])

# ----------------------------------------------------
# Fonctions de calcul ajoutées 
# ----------------------------------------------------

from disjoncteurs import BreakerCalculator
from variateurs import VFDCalculator

def compute_breaker_effective_loss(p_nom_w, charge_pct):
    return BreakerCalculator.effective_loss(p_nom_w, charge_pct)

def compute_vfd_effective_loss(p_nom_w, charge_pct):
    return VFDCalculator.effective_loss(p_nom_w, charge_pct)

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
        <div style="background-color: #162032; border: 1px solid #1E293B; border-radius: 8px; padding: 20px;">
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
# PAGE : Armoires A
# ----------------------------------------------------
elif menu == "Armoires A":
    st.title("Configuration des Armoires A")
    st.caption("Définissez le nombre d'armoires A et consultez leur détail unifilaire.")
    st.markdown("---")

    # Récupérer les valeurs actuelles
    nb_actuel = st.session_state.config_armoires.get("nb", 1)
    pertes_unitaire = PERTES_ARMOIRE_A_UNITAIRE_W

    st.subheader("Nombre d'Armoires A")
    nb = st.number_input("Nombre d'armoires A", min_value=0, max_value=20, value=nb_actuel, step=1)
    st.session_state.nb_armoires_a = nb   # pour compatibilité
    pertes_totales = nb * pertes_unitaire

    # Mise à jour du dictionnaire config_armoires
    st.session_state.config_armoires["nb"] = nb
    st.session_state.config_armoires["pertes_unitaire"] = pertes_unitaire
    st.session_state.config_armoires["pertes_totales"] = pertes_totales
    st.session_state.pertes_armoires_w = pertes_totales   # pour le bilan

    col1, col2 = st.columns(2)
    col1.metric("Pertes unitaires", f"{pertes_unitaire:.1f} W", f"{pertes_unitaire/1000:.2f} kW")
    col2.metric("Pertes totales", f"{pertes_totales:.1f} W", f"{pertes_totales/1000:.2f} kW", delta_color="inverse")

    st.markdown("---")
    st.subheader("📋 Détail unifilaire d'une Armoire A standard")
    st.table(pd.DataFrame(ARMOIRE_A_DEPARTS_STANDARDS))

# ----------------------------------------------------
# PAGE : Base Disjoncteurs (bibliothèque + configuration projet)
# ----------------------------------------------------
elif menu == "Base Disjoncteurs":
    st.title(" Configuration des Disjoncteurs")
    st.markdown("---")

    # Initialisation de la liste de configuration si absente
    if "disjoncteurs_config" not in st.session_state:
        st.session_state.disjoncteurs_config = []  # liste de dict

    # --- Formulaire d'ajout ---
    st.subheader("Ajouter un disjoncteur")
    with st.form("add_breaker_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            designation = st.text_input("Désignation / Modèle", value="Disjoncteur", key="new_desig")
        with col2:
            qty = st.number_input("Quantité", min_value=0, max_value=100, value=1, step=1, key="new_qty")
        with col3:
            p_nom = st.number_input("Pertes nominales (W) à 100%", min_value=0.0, value=15.0, step=1.0, key="new_pnom")
        with col4:
            charge = st.slider("Taux de charge (%)", 10, 100, 80, key="new_charge")

        # Bouton Ajouter (à l'intérieur du formulaire)
        add_clicked = st.form_submit_button("➕ Ajouter")

    if add_clicked:
        if designation.strip():
            # Calcul des pertes effectives
            pertes_eff = p_nom * (charge / 100.0) ** 2
            total_ligne = qty * pertes_eff

            # Ajouter à la liste
            st.session_state.disjoncteurs_config.append({
                "nom": designation,
                "quantite": qty,
                "p_nom": p_nom,
                "charge": charge,
                "pertes_eff": pertes_eff,
                "total": total_ligne
            })
            st.success(f"Ligne ajoutée : {designation}")
            st.rerun()
        else:
            st.warning("⚠️ Veuillez saisir une désignation.")

    st.markdown("---")

    # --- Affichage du tableau des lignes configurées ---
    st.markdown("---")
    st.subheader("📋 Disjoncteurs configurés")
    if st.session_state.disjoncteurs_config:

        # Construire un DataFrame pour l'affichage
        df = pd.DataFrame(st.session_state.disjoncteurs_config)

       # Afficher le tableau avec un bouton de suppression par ligne
        for idx, row in enumerate(df.to_dict(orient="records")):
            cols = st.columns([3, 1, 1, 1, 1, 1, 1, 1])
            cols[0].write(row["nom"])
            cols[1].write(row["quantite"])
            cols[2].write(f"{row['p_nom']:.1f} W")
            cols[3].write(f"{row['charge']}%")
            cols[4].write(f"{row['pertes_eff']:.1f} W")
            cols[5].write(f"{row['total']:.1f} W")
            if cols[6].button("X", key=f"del_disjoncteur_{idx}"):
                del st.session_state.disjoncteurs_config[idx]
                st.rerun()

        # Calcul du total
        total_global = sum(item["total"] for item in st.session_state.disjoncteurs_config)
        st.metric("Total pertes disjoncteurs (projet)", f"{total_global:.1f} W", f"{total_global/1000:.2f} kW", delta_color="inverse")


        # Bouton pour tout effacer
        if st.button("🗑️ Effacer toute la configuration"):
            st.session_state.disjoncteurs_config = []
            st.rerun()

        # --- Bouton Enregistrer la configuration ---
        if st.button("💾 Enregistrer la configuration pour le bilan thermique"):
            # Mettre à jour les clés utilisées par le bilan et le rapport
            st.session_state.pertes_disjoncteurs_w = total_global
            st.session_state.config_disjoncteurs = st.session_state.disjoncteurs_config
            st.success("Configuration enregistrée ! Le bilan thermique est mis à jour.")
            
    else:
        st.info("Aucun Disjoncteur configuré pour le moment. Ajoutez-en via le formulaire ci‑dessus.")
# ----------------------------------------------------
# PAGE : Base Variateurs (bibliothèque + configuration projet)
# ----------------------------------------------------
elif menu == "Base Variateurs":
    st.title("Configuration des Variateurs")
    st.markdown("---")

    # Initialiser la liste de configuration si absente
    if "variateurs_config" not in st.session_state:
        st.session_state.variateurs_config = []

    # --- Formulaire d'ajout ---
    with st.form("add_vfd_form", clear_on_submit=False):
        st.subheader("Ajouter un variateur")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nom = st.text_input("Désignation / Modèle", value="Variateur 1", key="vfd_nom")
        with col2:
            qty = st.number_input("Quantité", min_value=1, max_value=100, value=1, step=1, key="vfd_qty")
        with col3:
            p_nom = st.number_input("Pertes nominales (W) à 100%", min_value=0.0, value=50.0, step=1.0, key="vfd_pnom")
        with col4:
            charge = st.slider("Taux de charge (%)", 10, 100, 80, key="vfd_charge")

        # Deux boutons dans le formulaire
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            add_btn = st.form_submit_button("➕ Ajouter")
        with col_btn2:
            reset_btn = st.form_submit_button("🔄 Réinitialiser le formulaire")

    # Traitement du bouton "Ajouter"
    if add_btn and nom.strip():
        # Calcul des pertes effectives avec la bonne formule (exposant 1.5 pour les variateurs)
        pertes_eff = p_nom * (charge / 100.0) ** 1.5
        total_ligne = qty * pertes_eff

        # Ajouter à la liste
        st.session_state.variateurs_config.append({
            "nom": nom,
            "quantite": qty,
            "p_nom": p_nom,
            "charge": charge,
            "pertes_eff": pertes_eff,
            "total": total_ligne
        })
        st.rerun()

    # --- Affichage du tableau des lignes ajoutées ---
    st.markdown("---")
    st.subheader("📋 Variateurs configurés")

    if st.session_state.variateurs_config:
        # Créer un DataFrame pour l'affichage
        df_vfd = pd.DataFrame(st.session_state.variateurs_config)

        # Ajouter une colonne pour le bouton de suppression
        df_vfd["Supprimer"] = ""

        # Afficher le tableau avec un bouton de suppression par ligne
        for idx, row in enumerate(df_vfd.to_dict(orient="records")):
            cols = st.columns([3, 1, 1, 1, 1, 1, 1, 1])
            cols[0].write(row["nom"])
            cols[1].write(row["quantite"])
            cols[2].write(f"{row['p_nom']:.1f} W")
            cols[3].write(f"{row['charge']}%")
            cols[4].write(f"{row['pertes_eff']:.1f} W")
            cols[5].write(f"{row['total']:.1f} W")
            if cols[6].button("X", key=f"del_vfd_{idx}"):
                del st.session_state.variateurs_config[idx]
                st.rerun()

        # Calcul et affichage du total
        total_global = sum(item["total"] for item in st.session_state.variateurs_config)
        st.metric("Total pertes variateurs", f"{total_global:.1f} W", f"{total_global/1000:.2f} kW", delta_color="inverse")

        # Bouton pour tout effacer
        if st.button("🗑️ Effacer toute la configuration"):
            st.session_state.variateurs_config = []
            st.rerun()

        # Bouton Enregistrer pour valider la configuration
        if st.button("💾 Enregistrer pour le bilan thermique"):
            st.session_state.pertes_variateurs_w = total_global
            st.session_state.config_variateurs = st.session_state.variateurs_config.copy()
            st.success(f"Configuration enregistrée ! Total des pertes variateurs : {total_global:.1f} W")
            # On ne fait pas de rerun pour garder l'affichage

    else:
        st.info("Aucun variateur configuré. Ajoutez-en via le formulaire ci‑dessus.")

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
    # 2. READ INPUTS FROM SESSION STATE (always available)
    # ------------------------------------------------------------
    # Pertes des équipements
    pertes_armoires = st.session_state.get("pertes_armoires_w", 0.0)
    pertes_disj = st.session_state.get("pertes_disjoncteurs_w", 0.0)
    pertes_vfd = st.session_state.get("pertes_variateurs_w", 0.0)

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
        q_equipements = pertes_armoires + pertes_disj + pertes_vfd
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

    # Vérifier que le bilan est disponible
    if not st.session_state.get("bilan") or "total_equipements" not in st.session_state.bilan:
        st.warning("⚠️ Le bilan thermique n'a pas encore été calculé.")
        st.info("Veuillez d'abord consulter la page **Bilan Thermique** pour calculer le bilan.")
        
        if st.button("Calculer le bilan maintenant"):
            pertes_armoires = st.session_state.get("pertes_armoires_w", 0.0)
            pertes_disj = st.session_state.get("pertes_disjoncteurs_w", 0.0)
            pertes_vfd = st.session_state.get("pertes_variateurs_w", 0.0)
            apports_bat = st.session_state.get("apports_batiment_w", 0.0)
            
            if pertes_armoires == 0 and pertes_disj == 0 and pertes_vfd == 0 and apports_bat == 0:
                st.error("Aucune donnée disponible. Veuillez configurer les équipements et le local.")
            else:
                engine = ThermalEngine(safety_margin=0.10)
                total_equip = pertes_armoires + pertes_disj + pertes_vfd
                result = engine.compute_total(total_equip, apports_bat)
                st.session_state.bilan = {
                    "total_equipements": total_equip,
                    "apports_batiment": apports_bat,
                    "margin_pct": 10,
                    "units": result["units"]
                }
                st.success("Bilan calculé avec succès ! Vous pouvez maintenant générer le PDF.")
                st.rerun()
    else:
        # Données disponibles
        project_data = st.session_state.project
        building_data = st.session_state.local
        armoires_data = st.session_state.get("config_armoires", {"nb": 0, "pertes_totales": 0})
        disjoncteurs_data = st.session_state.get("config_disjoncteurs", [])
        variateurs_data = st.session_state.get("config_variateurs", [])
        bilan_data = st.session_state.bilan

        # Aperçu 
        st.subheader("Aperçu du rapport")
        col1, col2, col3 = st.columns(3)
        col1.metric("Projet", project_data.get("nom", "N/A"))
        col2.metric("Client", project_data.get("client", "N/A"))
        col3.metric("Ingénieur", project_data.get("ingenieur", "N/A"))
        st.caption(f"T_ext : {project_data.get('t_ext', 0)} °C | T_int : {project_data.get('t_int', 0)} °C")

        with st.expander("Détail des équipements configurés", expanded=False):
            st.write("**Armoires A :**", armoires_data.get("nb", 0), "unités, pertes totales :", f"{armoires_data.get('pertes_totales', 0):.0f} W")
            if disjoncteurs_data:
                st.write("**Disjoncteurs :**")
                st.dataframe(pd.DataFrame(disjoncteurs_data), use_container_width=True)
            else:
                st.write("Aucun disjoncteur configuré.")
            if variateurs_data:
                st.write("**Variateurs :**")
                st.dataframe(pd.DataFrame(variateurs_data), use_container_width=True)
            else:
                st.write("Aucun variateur configuré.")

        st.markdown("---")
        st.subheader("Résumé du bilan")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Pertes équipements", f"{bilan_data['total_equipements']:.0f} W", f"{bilan_data['total_equipements']/1000:.2f} kW")
        col2.metric("Apports bâtiment", f"{bilan_data['apports_batiment']:.0f} W", f"{bilan_data['apports_batiment']/1000:.2f} kW")
        col3.metric("Puissance HVAC", f"{bilan_data['units']['kw']:.2f} kW")
        col4.metric("Capacité recommandée", f"{bilan_data['units']['tr']:.2f} TR")

        st.divider()

        if st.button("Générer et télécharger le PDF", use_container_width=True):
            output_dir = "reports"
            if os.path.exists(output_dir) and not os.path.isdir(output_dir):
                os.remove(output_dir)
            os.makedirs(output_dir, exist_ok=True)

            clean_name = "".join(c for c in project_data["nom"] if c.isalnum() or c in (" ", "_")).rstrip()
            pdf_path = os.path.join(output_dir, f"Bilan_{clean_name.replace(' ', '_')}.pdf")

            try:
                PDFReportGenerator.generate(
                    pdf_path,          # filename (positionnel)
                    project_data,      # project
                    building_data,     # building
                    armoires_data,     # armoires
                    disjoncteurs_data, # disjoncteurs
                    variateurs_data,   # variateurs
                    bilan_data         # bilan
                )
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="💾 Télécharger le PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        use_container_width=True,
                    )
                st.success(f"PDF généré avec succès : {os.path.basename(pdf_path)}")
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF : {e}")
    
