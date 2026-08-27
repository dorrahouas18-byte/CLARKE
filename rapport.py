"""
Module rapport.py - Génération de rapport PDF professionnel pour AC Sizing Pro
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from templates import ARMOIRE_A_DEPARTS_STANDARDS

class PDFReportGenerator:
    @staticmethod
    def generate(filename, project, building, armoires, disjoncteurs, variateurs, bilan):
        """
        Génère un rapport PDF 
        """
        # --- Gestion du dossier de sortie ---
        folder = os.path.dirname(filename)
        if folder:
            if os.path.exists(folder) and not os.path.isdir(folder):
                os.remove(folder)
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

        # --- Styles personnalisés ---
        styles = getSampleStyleSheet()
        
        # Style du titre principal
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0A1120'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style du sous-titre
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2B6CB0'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica'
        )
        
        # Style des titres de section
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1A3A6B'), 
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Style normal
        normal_style = styles['Normal']
        normal_style.fontName = 'Helvetica'
        
        # Style pour les valeurs importantes
        value_style = ParagraphStyle(
            'ValueStyle',
            parent=normal_style,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2B6CB0')
        )

        story = []

        # --- Ajout du logo Clarke Energy ---
        logo_path = "assets/Logo1.png"
        try:
            if os.path.exists(logo_path):
                logo_img = Image(logo_path, width=4*cm, height=2*cm)
                # Centrer le logo
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
            pass  # Si le logo n'est pas trouvé, on continue sans

        # --- Titre et date ---
        story.append(Paragraph("Bilan Thermique et Dimensionnement AC", title_style))
        story.append(Paragraph("Clarke Energy", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            f"<i>Rapport généré le {datetime.today().strftime('%d/%m/%Y à %H:%M')}</i>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.8*cm))

        # ---- 1. Cartouche Projet ----
        story.append(Paragraph("1. Identification du Projet", h2_style))
        # Données sous forme de tableau 2 colonnes
        proj_items = [
            ("Projet", project.get("nom", "N/A")),
            ("Client", project.get("client", "N/A")),
            ("N° Affaire", project.get("reference", "N/A")),
            ("Ingénieur", project.get("ingenieur", "N/A")),
            ("Date", project.get("date", "N/A")),
            ("Statut", project.get("statut", "APS")),
            ("Température extérieure", f"{project.get('t_ext', 40.0)} °C"),
            ("Température intérieure", f"{project.get('t_int', 25.0)} °C"),
        ]
        # Transformer en tableau 4 colonnes
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

        # ---- 2. Caractéristiques du Local ----
        story.append(Paragraph("2. Caractéristiques du Local", h2_style))
        length = building.get('length', 0)
        width = building.get('width', 0)
        height = building.get('height', 0)
        volume = length * width * height
        local_items = [
            ("Longueur", f"{length:.1f} m", "Largeur", f"{width:.1f} m"),
            ("Hauteur", f"{height:.1f} m", "Volume", f"{volume:.1f} m³"),
            ("Type murs", building.get('wall_type', 'N/A'), "Type toiture", building.get('roof_type', 'N/A')),
            ("Éclairage", f"{building.get('lighting_w_m2', 0):.1f} W/m²", "ACH", f"{building.get('ach', 0):.1f} vol/h"),
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
        story.append(Spacer(1, 0.8*cm))

        # ---- 3. Armoires A ----
        story.append(Paragraph("3. Armoires A", h2_style))
        nb_armoires = armoires.get('nb', 0)
        pertes_unitaire = armoires.get('pertes_unitaire', 0)
        pertes_totales = armoires.get('pertes_totales', 0)
        armoires_text = f"""
        <b>Nombre d'armoires A :</b> {nb_armoires}<br/>
        <b>Pertes unitaires :</b> {pertes_unitaire:.1f} W<br/>
        <b>Pertes totales :</b> {pertes_totales:.1f} W ({pertes_totales/1000:.2f} kW)
        """
        story.append(Paragraph(armoires_text, normal_style))
        story.append(Spacer(1, 0.3*cm))

        if ARMOIRE_A_DEPARTS_STANDARDS:
            story.append(Paragraph("Détail des départs (1 armoire) :", normal_style))
            dep_data = [["Départ", "Type", "Équipement", "Pertes (W)"]]
            for d in ARMOIRE_A_DEPARTS_STANDARDS:
                dep_data.append([d['depart'], d['type'], d['equipement'], f"{d['pertes_w']:.1f}"])
            t_dep = Table(dep_data, colWidths=[4*cm, 3*cm, 6*cm, 3*cm])
            t_dep.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (3,0), (3,-1), 'CENTER'),
            ]))
            story.append(t_dep)
        story.append(Spacer(1, 0.8*cm))

        # ---- 4. Disjoncteurs configurés ----
        story.append(Paragraph("4. Disjoncteurs configurés", h2_style))
        if disjoncteurs and len(disjoncteurs) > 0:
            disj_data = [["Modèle", "Qté", "Charge (%)", "Pertes unit. (W)", "Total (W)"]]
            total_disj = 0
            for item in disjoncteurs:
                disj_data.append([
                    item.get('modele', 'N/A'),
                    str(item.get('quantite', 0)),
                    f"{item.get('charge_pct', 0)}%",
                    f"{item.get('pertes_effectives_unit', 0):.1f}",
                    f"{item.get('total_w', 0):.1f}"
                ])
                total_disj += item.get('total_w', 0)
            t_disj = Table(disj_data, colWidths=[5*cm, 2*cm, 2.5*cm, 3*cm, 3*cm])
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
            story.append(Paragraph(f"<b>Total pertes disjoncteurs :</b> {total_disj:.1f} W ({total_disj/1000:.2f} kW)", normal_style))
        else:
            story.append(Paragraph("Aucun disjoncteur configuré.", normal_style))
        story.append(Spacer(1, 0.8*cm))

        # ---- 5. Variateurs configurés ----
        story.append(Paragraph("5. Variateurs configurés", h2_style))
        if variateurs and len(variateurs) > 0:
            vfd_data = [["Modèle", "Qté", "Charge (%)", "Pertes unit. (W)", "Total (W)"]]
            total_vfd = 0
            for item in variateurs:
                vfd_data.append([
                    item.get('modele', 'N/A'),
                    str(item.get('quantite', 0)),
                    f"{item.get('charge_pct', 0)}%",
                    f"{item.get('pertes_effectives_unit', 0):.1f}",
                    f"{item.get('total_w', 0):.1f}"
                ])
                total_vfd += item.get('total_w', 0)
            t_vfd = Table(vfd_data, colWidths=[5*cm, 2*cm, 2.5*cm, 3*cm, 3*cm])
            t_vfd.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 4),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t_vfd)
            story.append(Paragraph(f"<b>Total pertes variateurs :</b> {total_vfd:.1f} W ({total_vfd/1000:.2f} kW)", normal_style))
        else:
            story.append(Paragraph("Aucun variateur configuré.", normal_style))
        story.append(Spacer(1, 0.8*cm))

        # ---- 6. Bilan Thermique Global ----
        story.append(Paragraph("6. Bilan Thermique Global", h2_style))
        units = bilan.get("units", {})
        total_equip = bilan.get("total_equipements", 0)
        apports_bat = bilan.get("apports_batiment", 0)
        margin = bilan.get("margin_pct", 10)
        total_design = total_equip + apports_bat
        total_avec_marge = total_design * (1 + margin/100)

        # Tableau bilan
        bilan_data = [
            ["Poste", "Valeur (W)", "Valeur (kW)"],
            ["Pertes équipements", f"{total_equip:.1f}", f"{total_equip/1000:.2f}"],
            ["Apports bâtiment", f"{apports_bat:.1f}", f"{apports_bat/1000:.2f}"],
            ["Sous-total (sans marge)", f"{total_design:.1f}", f"{total_design/1000:.2f}"],
            [f"Marge de sécurité ({margin}%)", "", ""],
            ["<b>Total dimensionnement</b>", f"<b>{total_avec_marge:.1f}</b>", f"<b>{total_avec_marge/1000:.2f}</b>"],
            ["", "", ""],
            ["Capacité en kW", f"{units.get('kw', 0):.2f}", "kW"],
            ["Capacité en BTU/h", f"{units.get('btu_h', 0):.2f}", "BTU/h"],
            ["Capacité en TR", f"{units.get('tr', 0):.2f}", "TR"],
        ]
        t_bilan = Table(bilan_data, colWidths=[6*cm, 4*cm, 4*cm])
        t_bilan.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (1,0), (2,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 5),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#E8F0FE')),  
            ('TEXTCOLOR', (0,5), (-1,5), colors.HexColor('#1A3A6B')),
            ('BACKGROUND', (0,7), (-1,-1), colors.HexColor('#F8FAFC')),
        ]))
        story.append(t_bilan)
        story.append(Spacer(1, 0.8*cm))

        # ---- 7. Résumé des capacités  ----
        story.append(Paragraph("7. Résumé des Capacités", h2_style))
        kw_val = units.get('kw', 0)
        btu_val = units.get('btu_h', 0)
        tr_val = units.get('tr', 0)
        summary_text = f"""
        <font size=12><b>Puissance frigorifique nécessaire :</b> 
        <font color="#2B6CB0">{kw_val:.2f} kW</font>/
        <font color="#2B6CB0">{btu_val:.0f} BTU/h</font>
        (<font color="#2B6CB0">{tr_val:.2f} TR</font>)
        </font>
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 0.5*cm))

        # ---- 8. Références normatives ----
        story.append(Paragraph("8. Références et Normes", h2_style))
        norm_text = """
        <b>Méthodologie ASHRAE CLTD/CLF</b> : calcul des apports de transmission, éclairage et ventilation.<br/>
        <b>IEC 61439</b> : pertes dans les tableaux de distribution (disjoncteurs, jeux de barres).<br/>
        <b>IEC 60076-7 / 60287</b> : pertes des transformateurs et câbles.<br/>
        <b>Dimensionnement HVAC</b> : marge de sécurité de 10 à 15 % (recommandation ASHRAE).
        """
        story.append(Paragraph(norm_text, normal_style))

        # ---- Construction du PDF ----
        doc.build(story)