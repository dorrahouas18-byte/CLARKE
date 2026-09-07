"""
Module rapport.py - Génération de rapport PDF
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


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
        """
        Génère un rapport PDF reprenant la structure du site web.
        """
        # --- Gestion du dossier ---
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        # --- Configuration du document ---
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )

        # --- Styles ---
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0A1120'),
            spaceAfter=6,
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
            fontSize=13,
            textColor=colors.HexColor('#1A3A6B'),
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        normal_style = styles['Normal']
        normal_style.fontName = 'Helvetica'

        story = []

        # --- Logo ---
        logo_path = "assets/Logo1.png"
        if os.path.exists(logo_path):
            try:
                logo_img = Image(logo_path, width=4*cm, height=2*cm)
                logo_table = Table([[logo_img]], colWidths=[doc.width])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                story.append(logo_table)
                story.append(Spacer(1, 0.3*cm))
            except Exception:
                pass

        # --- Titre principal ---
        story.append(Paragraph("Bilan Thermique et Dimensionnement AC", title_style))
        story.append(Paragraph("Clarke Energy", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            f"<i>Rapport généré le {datetime.today().strftime('%d/%m/%Y à %H:%M')}</i>",
            normal_style
        ))
        story.append(Spacer(1, 0.8*cm))

        # ============================================================
        # 1. SECTION : PROJET 
        # ============================================================
        story.append(Paragraph("1. Projet & Identification", h2_style))
        proj_items = [
            ("Projet", project.get("nom", "N/A")),
            ("Client", project.get("client", "N/A")),
            ("N° Affaire", project.get("reference", "N/A")),
            ("Ingénieur", project.get("ingenieur", "N/A")),
            ("Date", project.get("date", "N/A")),
            ("Statut", project.get("statut", "APS")),
            ("T_ext", f"{project.get('t_ext', 40.0)} °C"),
            ("T_int", f"{project.get('t_int', 25.0)} °C"),
        ]
        # Affichage en tableau 4 colonnes
        proj_table = []
        for i in range(0, len(proj_items), 2):
            left_label, left_val = proj_items[i]
            if i+1 < len(proj_items):
                right_label, right_val = proj_items[i+1]
                proj_table.append([left_label, left_val, right_label, right_val])
            else:
                proj_table.append([left_label, left_val, "", ""])
        t_proj = Table(proj_table, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        t_proj.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#0A1120')),
            ('TEXTCOLOR', (3,0), (3,-1), colors.HexColor('#0A1120')),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
            ('FONTNAME', (3,0), (3,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_proj)
        story.append(Spacer(1, 0.8*cm))

        # ============================================================
        # 2. SECTION : LOCAL 
        # ============================================================
        story.append(Paragraph("2. Local Électrique & Enveloppe", h2_style))
        length = building.get('length', 0)
        width = building.get('width', 0)
        height = building.get('height', 0)
        surface = length * width
        volume = surface * height
        nb_luminaires = building.get('nb_luminaires', 0)
        puissance_light = building.get('puissance_luminaire', 40)
        total_lighting = nb_luminaires * puissance_light

        local_items = [
            ("Longueur", f"{length:.1f} m", "Largeur", f"{width:.1f} m"),
            ("Hauteur", f"{height:.1f} m", "Volume", f"{volume:.1f} m³"),
            ("Surface", f"{surface:.1f} m²", "Éclairage installé", f"{total_lighting:.0f} W"),
            ("Type murs", building.get('wall_type', 'N/A'), "Type toiture", building.get('roof_type', 'N/A')),
        ]
        t_local = Table(local_items, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
        t_local.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor('#1A3A6B')),
            ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#0A1120')),
            ('TEXTCOLOR', (3,0), (3,-1), colors.HexColor('#0A1120')),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
            ('FONTNAME', (3,0), (3,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_local)
        story.append(Spacer(1, 0.5*cm))

        # --- Bilan des apports du local ---
       
        story.append(Paragraph("Bilan des apports du local", h2_style))
        # On récupère les apports depuis le bilan (si présents)
        apports = building.get('apports', {})
        if apports:
            col_items = [
                ("Transmission", f"{apports.get('transmission_w', 0):.1f} W", f"{apports.get('transmission_w', 0)/1000:.2f} kW"),
                ("Éclairage + Occupants", f"{apports.get('lighting_w', 0):.1f} W", f"{apports.get('lighting_w', 0)/1000:.2f} kW"),
                ("Ventilation", f"{apports.get('ventilation_w', 0):.1f} W", f"{apports.get('ventilation_w', 0)/1000:.2f} kW"),
                ("Total local", f"{sum([apports.get('transmission_w',0), apports.get('lighting_w',0), apports.get('ventilation_w',0)]):.1f} W", 
                 f"{sum([apports.get('transmission_w',0), apports.get('lighting_w',0), apports.get('ventilation_w',0)])/1000:.2f} kW"),
            ]
            col_table = [["Poste", "Valeur (W)", "Valeur (kW)"]]
            for row in col_items:
                col_table.append([row[0], row[1], row[2]])
            t_col = Table(col_table, colWidths=[5*cm, 4*cm, 4*cm])
            t_col.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('ALIGN', (1,0), (2,-1), 'CENTER'),
            ]))
            story.append(t_col)
            story.append(Spacer(1, 0.5*cm))
        else:
            story.append(Paragraph("Aucun détail des apports disponible.", normal_style))
            story.append(Spacer(1, 0.5*cm))

        # ============================================================
        # 3. SECTION : ARMOIRES A 
        # ============================================================
        story.append(Paragraph("3. Armoires A (standard)", h2_style))
        nb_armoires = armoires.get('nb', 0)
        pertes_armoires = armoires.get('pertes_totales', 0)
        story.append(Paragraph(
            f"<b>Nombre d'armoires :</b> {nb_armoires} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Pertes totales :</b> {pertes_armoires:.1f} W ({pertes_armoires/1000:.2f} kW)",
            normal_style
        ))
        # Afficher la composition type 
        compo = armoires.get('composition', [])
        if compo:
            story.append(Paragraph("Composition type d'une armoire A :", normal_style))
            compo_data = [["Composant", "Puissance unit. (W)", "Qté", "Total (W)"]]
            for item in compo:
                compo_data.append([
                    item.get('nom', 'N/A'),
                    f"{item.get('puissance_unitaire', 0):.0f}",
                    str(item.get('quantite', 0)),
                    f"{item.get('total', 0):.0f}"
                ])
            t_compo = Table(compo_data, colWidths=[5*cm, 3*cm, 2*cm, 3*cm])
            t_compo.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_compo)
        story.append(Spacer(1, 0.8*cm))

        # ============================================================
        # 4. SECTION : TGBT 
        # ============================================================
        story.append(Paragraph("4. TGBT (Tableau Général Basse Tension)", h2_style))
        if disjoncteurs and len(disjoncteurs) > 0:
            disj_data = [["Composant", "Qté", "Puissance unit. (W)", "Total (W)"]]
            total_tgbt = 0
            for item in disjoncteurs:
                disj_data.append([
                    item.get('nom', 'N/A'),
                    str(item.get('quantite', 0)),
                    f"{item.get('puissance', item.get('puissance_unitaire', 0)):.0f}",
                    f"{item.get('total', 0):.0f}"
                ])
                total_tgbt += item.get('total', 0)
            t_disj = Table(disj_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
            t_disj.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_disj)
            story.append(Paragraph(f"<b>Total pertes TGBT :</b> {total_tgbt:.1f} W ({total_tgbt/1000:.2f} kW)", normal_style))
        else:
            story.append(Paragraph("Aucun composant TGBT configuré.", normal_style))
        story.append(Spacer(1, 0.8*cm))

        # ============================================================
        # 5. SECTION : ARMOIRES AUXILIAIRES 
        # ============================================================
        if auxiliaires:
            story.append(Paragraph("5. Armoires Auxiliaires", h2_style))
            qty = auxiliaires.get('quantite', 0)
            pertes_aux = auxiliaires.get('pertes_totales', 0)
            story.append(Paragraph(
                f"<b>Nombre d'armoires :</b> {qty} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Pertes totales :</b> {pertes_aux:.1f} W ({pertes_aux/1000:.2f} kW)",
                normal_style
            ))
            components = auxiliaires.get('components', [])
            if components:
                aux_data = [["Composant", "Qté", "Puissance unit. (W)", "Total (W)"]]
                for comp in components:
                    aux_data.append([
                        comp.get('nom', 'N/A'),
                        str(comp.get('quantite', 0)),
                        f"{comp.get('puissance_unitaire', 0):.0f}",
                        f"{comp.get('total', 0):.0f}"
                    ])
                t_aux = Table(aux_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
                t_aux.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('PADDING', (0,0), (-1,-1), 4),
                    ('FONTSIZE', (0,1), (-1,-1), 8),
                    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ]))
                story.append(t_aux)
            story.append(Spacer(1, 0.8*cm))

        # ============================================================
        # 6. SECTION : BILAN THERMIQUE 
        # ============================================================
        story.append(Paragraph("6. Bilan Thermique et Dimensionnement AC", h2_style))
        # Synthèse
        story.append(Paragraph("Synthèse du Bilan de Puissance", h2_style))
        units = bilan.get("units", {})
        total_equip = bilan.get("total_equipements", 0)
        apports_bat = bilan.get("apports_batiment", 0)
        margin = bilan.get("margin_pct", 15)
        total_design = total_equip + apports_bat
        total_avec_marge = total_design * (1 + margin/100)
        debit_air = total_avec_marge / (0.34 * (project.get("t_ext", 40) - project.get("t_int", 25))) if (project.get("t_ext", 40) - project.get("t_int", 25)) > 0 else 0

        synth_data = [
            ["Indicateur", "Valeur"],
            ["Puissance Frigorifique Nécessaire", f"{units.get('btu_h', 0):.0f} BTU/h / {units.get('kw', 0):.2f} kW"],
            ["Capacité Recommandée", f"{units.get('tr', 0):.2f} TR ({margin}% de marge)"],
            ["Équivalent en kW", f"{units.get('kw', 0):.2f} kW"],
            ["Débit d'Air Estimé", f"{debit_air:.0f} m³/h"],
        ]
        t_synth = Table(synth_data, colWidths=[7*cm, 8*cm])
        t_synth.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_synth)
        story.append(Spacer(1, 0.5*cm))

        # --- Détail des apports  ---
        story.append(Paragraph("Détail des Apports Thermiques", h2_style))
        # Tableau avec les différents postes
        apport_data = [
            ["Poste", "Valeur (W)", "Valeur (kW)"],
            ["Équipements électriques", f"{total_equip:.1f}", f"{total_equip/1000:.2f}"],
            ["Éclairage", f"0.0", "0.00"],  # On ne connaît pas le détail ici, on le récupère du bilan si on l'a stocké
            ["Total Interne", f"{total_equip:.1f}", f"{total_equip/1000:.2f}"],
            ["Murs & Toit", f"{apports_bat:.1f}", f"{apports_bat/1000:.2f}"],
            ["Ventilation", f"0.0", "0.00"],
            ["Total Enveloppe", f"{apports_bat:.1f}", f"{apports_bat/1000:.2f}"],
            ["Charge Totale (Brute)", f"{total_design:.1f}", f"{total_design/1000:.2f}"],
            [f"Charge avec marge ({margin}%)", f"{total_avec_marge:.1f}", f"{total_avec_marge/1000:.2f}"],
        ]
        t_apport = Table(apport_data, colWidths=[6*cm, 4*cm, 4*cm])
        t_apport.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (1,0), (2,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 4),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0,8), (-1,8), colors.HexColor('#E8F0FE')),
            ('TEXTCOLOR', (0,8), (-1,8), colors.HexColor('#1A3A6B')),
        ]))
        story.append(t_apport)
        story.append(Spacer(1, 0.5*cm))

        # --- Sensibilité à la température extérieure ---
        story.append(Paragraph("Sensibilité à la Température Extérieure", h2_style))
        story.append(Paragraph("La puissance nécessaire du climatiseur en fonction de la chaleur extérieure :", normal_style))
        # On simule quelques points si on a les données
        t_ext_base = project.get('t_ext', 40)
        t_int = project.get('t_int', 25)
        temps = [t_ext_base-10, t_ext_base-5, t_ext_base, t_ext_base+5, t_ext_base+10]
        sens_data = [["T_ext (°C)", "Puissance AC (kW)"]]
        for t in temps:
            dt = max(0, t - t_int)
            # Approximation simple
            p = total_equip + (apports_bat * dt / (t_ext_base - t_int)) if (t_ext_base - t_int) > 0 else 0
            sens_data.append([f"{t:.0f}", f"{p/1000:.2f}"])
        t_sens = Table(sens_data, colWidths=[5*cm, 10*cm])
        t_sens.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ]))
        story.append(t_sens)

        # ============================================================
        # 7. RÉFÉRENCES NORMATIVES 
        # ============================================================
        story.append(PageBreak())
        story.append(Paragraph("7. Références et Normes", h2_style))
        norm_text = """
        <b>Méthodologie ASHRAE CLTD/CLF</b> : calcul des apports de transmission, éclairage et ventilation.<br/>
        <b>IEC 61439</b> : pertes dans les tableaux de distribution (disjoncteurs, jeux de barres).<br/>
        <b>IEC 60076-7 / 60287</b> : pertes des transformateurs et câbles.<br/>
        <b>Dimensionnement HVAC</b> : marge de sécurité de 10 à 15 % (recommandation ASHRAE).
        """
        story.append(Paragraph(norm_text, normal_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Généré automatiquement par AC Sizing Pro – Clarke Energy – {datetime.today().strftime('%d/%m/%Y')}", normal_style))

        # ---- Construction du PDF ----
        doc.build(story)
