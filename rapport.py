"""
Module rapport.py - Génération de rapport PDF épuré et professionnel
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFReportGenerator:
    @staticmethod
    def generate(
        filename: str,
        project: dict,
        building: dict,
        armoires: dict,
        disjoncteurs: list,
        variateurs: list,
        bilan: dict,
        auxiliaires: dict = None
    ):
        """Génère un rapport PDF clair, épuré et professionnel."""

        # --- Création du dossier ---
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        # --- Configuration du document ---
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2 * cm
        )

        # --- Styles ---
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0A1120'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2B6CB0'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        )
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1A3A6B'),
            spaceBefore=10,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )
        normal_style = styles['Normal']
        normal_style.fontName = 'Helvetica'
        normal_style.fontSize = 9

        story = []

        # --- En-tête ---
        # Logo 
        logo_path = "assets/Logo1.png"
        if os.path.exists(logo_path):
            try:
                logo_img = Image(logo_path, width=4 * cm, height=2 * cm)
                logo_table = Table([[logo_img]], colWidths=[doc.width])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                story.append(logo_table)
                story.append(Spacer(1, 0.3 * cm))
            except Exception:
                pass

        story.append(Paragraph("Bilan Thermique et Dimensionnement AC", title_style))
        story.append(Paragraph("Clarke Energy", subtitle_style))
        story.append(Spacer(1, 0.5 * cm))

        # --- 1. IDENTIFICATION DU PROJET ---
        story.append(Paragraph("1. Identification du projet", h2_style))
        proj_data = [
            ["Projet", project.get("nom", "N/A"), "Client", project.get("client", "N/A")],
            ["N° Affaire", project.get("reference", "N/A"), "Ingénieur", project.get("ingenieur", "N/A")],
            ["Date", project.get("date", "N/A"), "Statut", project.get("statut", "APS")],
            ["T° extérieure", f"{project.get('t_ext', 40.0)} °C", "T° intérieure", f"{project.get('t_int', 25.0)} °C"],
        ]
        t_proj = Table(proj_data, colWidths=[3.5 * cm, 4.5 * cm, 3.5 * cm, 4.5 * cm])
        t_proj.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0A1120')),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#0A1120')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_proj)
        story.append(Spacer(1, 0.6 * cm))

        # --- 2. CARACTÉRISTIQUES DU LOCAL ---
        story.append(Paragraph("2. Caractéristiques du local", h2_style))
        length = building.get('length', 0)
        width = building.get('width', 0)
        height = building.get('height', 0)
        surface = length * width
        volume = surface * height
        nb_luminaires = building.get('nb_luminaires', 0)
        puissance_light = building.get('puissance_luminaire', 40)
        lighting_total = nb_luminaires * puissance_light

        local_data = [
            ["Longueur", f"{length:.1f} m", "Surface", f"{surface:.1f} m²"],
            ["Largeur", f"{width:.1f} m", "Volume", f"{volume:.1f} m³"],
            ["Hauteur", f"{height:.1f} m", "Éclairage installé", f"{lighting_total:.0f} W"],
            ["Murs", building.get('wall_type', 'N/A'), "Toiture", building.get('roof_type', 'N/A')],
        ]
        t_local = Table(local_data, colWidths=[3.5 * cm, 4.5 * cm, 3.5 * cm, 4.5 * cm])
        t_local.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0A1120')),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor('#0A1120')),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_local)
        story.append(Spacer(1, 0.6 * cm))

        # --- 3. SYNTHESE DES EQUIPEMENTS  ---
        story.append(Paragraph("3. Synthèse des équipements", h2_style))

        # Calcul des totaux
        armoire_a_quantite = armoires.get('nb', 0)
        pertes_armoires = armoires.get('pertes_totales', 0.0)

        # Totaux TGBT (calculés à partir des pertes de la session)
        pertes_tgbt = 0.0
        for comp in disjoncteurs:
            pertes_tgbt += comp.get('total', 0.0)
        for comp in variateurs:
            pertes_tgbt += comp.get('total', 0.0)

        # Totaux Auxiliaires
        if auxiliaires:
            pertes_aux = auxiliaires.get('pertes_totales', 0.0)
            aux_quantite = auxiliaires.get('quantite', 0)
        else:
            pertes_aux = 0.0
            aux_quantite = 0

        total_equip = pertes_armoires + pertes_tgbt + pertes_aux

        equip_data = [
            ["Poste", "Quantité", "Pertes (W)", "Pertes (kW)"],
            ["Armoires A", f"{armoire_a_quantite}", f"{pertes_armoires:.1f}", f"{pertes_armoires/1000:.2f}"],
            ["TGBT", "1", f"{pertes_tgbt:.1f}", f"{pertes_tgbt/1000:.2f}"],
            ["Armoires Auxiliaires", f"{aux_quantite}", f"{pertes_aux:.1f}", f"{pertes_aux/1000:.2f}"],
            ["", "", "", ""],
            ["TOTAL ÉQUIPEMENTS", "", f"{total_equip:.1f}", f"{total_equip/1000:.2f}"],
        ]
        t_equip = Table(equip_data, colWidths=[5 * cm, 2.5 * cm, 3 * cm, 3 * cm])
        t_equip.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#E8F0FE')),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTNAME', (2, 5), (3, 5), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.HexColor('#1A3A6B')),
        ]))
        story.append(t_equip)
        story.append(Spacer(1, 0.6 * cm))

        # --- 4. BILAN THERMIQUE FINAL ---
        story.append(Paragraph("4. Bilan thermique global", h2_style))

        apports_bat = bilan.get("apports_batiment", 0.0)
        margin = bilan.get("margin_pct", 10)
        units = bilan.get("units", {})
        kw_val = units.get('kw', 0.0)
        btu_val = units.get('btu_h', 0.0)
        tr_val = units.get('tr', 0.0)

        total_design = total_equip + apports_bat
        total_avec_marge = total_design * (1 + margin / 100.0)

        bilan_data = [
            ["Poste", "Valeur (W)", "Valeur (kW)"],
            ["Apports du bâtiment", f"{apports_bat:.1f}", f"{apports_bat/1000:.2f}"],
            ["Pertes équipements", f"{total_equip:.1f}", f"{total_equip/1000:.2f}"],
            ["Sous-total (brut)", f"{total_design:.1f}", f"{total_design/1000:.2f}"],
            [f"Marge de sécurité ({margin}%)", "-", "-"],
            ["Total dimensionnement", f"{total_avec_marge:.1f}", f"{total_avec_marge/1000:.2f}"],
        ]
        t_bilan = Table(bilan_data, colWidths=[5 * cm, 4 * cm, 4 * cm])
        t_bilan.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#E8F0FE')),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTNAME', (1, 5), (2, 5), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.HexColor('#1A3A6B')),
            ('BACKGROUND', (0, 6), (-1, 8), colors.HexColor('#F8FAFC')),
        ]))
        story.append(t_bilan)
        story.append(Spacer(1, 0.4 * cm))

        # --- 5. RÉSUMÉ DES CAPACITÉS ---
        story.append(Paragraph("5. Résumé des capacités", h2_style))
        cap_text = f"""
        <b>Puissance frigorifique nécessaire :</b> 
        <font color="#2B6CB0">{kw_val:.2f} kW</font> / 
        <font color="#2B6CB0">{btu_val:.0f} BTU/h</font> / 
        <font color="#2B6CB0">{tr_val:.2f} TR</font>
        """
        story.append(Paragraph(cap_text, normal_style))
        story.append(Spacer(1, 0.4 * cm))

        # --- 6. RÉFÉRENCES (une ligne) ---
        story.append(Paragraph("6. Références", h2_style))
        story.append(Paragraph(
            "Méthode ASHRAE CLTD/CLF – Normes IEC 61439 / EN 12464-1 – Marge de 10%",
            normal_style
        ))
        story.append(Spacer(1, 0.3 * cm))

        # --- Pied de page (date) ---
        story.append(Paragraph(
            f"<i>Rapport généré le {datetime.today().strftime('%d/%m/%Y à %H:%M')}</i>",
            normal_style
        ))

        # --- Construction du PDF ---
        doc.build(story)
