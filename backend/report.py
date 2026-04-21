# HR Report Generation
# Generate professional HR reports in PDF format for employees

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models import Employee
from database import get_db
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import random

router = APIRouter()


def get_performance(score):
    """Calculate performance based on score"""
    if score >= 80:
        return "Élevée"
    elif score >= 50:
        return "Moyenne"
    else:
        return "Faible"


def get_potential(niveau):
    """Calculate potential based on niveau"""
    niveau = (niveau or "").lower()
    if niveau in ["senior", "lead"]:
        return "Élevé"
    elif niveau in ["confirmé", "intermédiaire"]:
        return "Moyen"
    else:
        return "Faible"


def get_turnover_risk(score):
    """Calculate turnover risk based on score"""
    if score < 50:
        return "Élevé"
    elif score <= 75:
        return "Moyen"
    else:
        return "Faible"


def get_recommendation(performance, potential, turnover_risk):
    """Get HR recommendation based on metrics"""
    if turnover_risk == "Élevé":
        return "Attention RH requise - risque de départ élevé"
    elif performance == "Élevée" and potential == "Élevé":
        return "Promotion recommandée - employé à fort potentiel"
    elif performance == "Moyenne" and turnover_risk == "Moyen":
        return "Suivi régulier conseillé"
    elif performance == "Élevée":
        return "Maintien et développement recommandé"
    else:
        return "Plan d'amélioration de performance suggéré"


@router.get("/api/employees/{employee_id}/report")
def generate_report(employee_id: int):
    """Generate HR report for an employee"""
    db = next(get_db())
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Calculate metrics
        score = employee.score if employee.score is not None else 50
        performance = get_performance(score)
        potential = get_potential(employee.niveau)
        turnover_risk = get_turnover_risk(score)
        recommendation = get_recommendation(performance, potential, turnover_risk)
        
        # Calculate total salary
        salaire_base = employee.salaire_base or 0
        prime = employee.prime or 0
        transport = employee.transport or 0
        assurance = employee.assurance or 0
        salaire_total = salaire_base + prime + transport + assurance
        
        # Generate report ID and date
        report_date = datetime.now().strftime("%d/%m/%Y")
        report_id = f"RH-2026-{random.randint(1000, 9999)}"
        
        # Generate PDF
        filename = f"report_{employee.name.replace(' ', '_')}.pdf"
        doc = SimpleDocTemplate(
            filename, 
            pagesize=letter,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        
        # Custom styles
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6c5ce7'),
            alignment=1,
            spaceAfter=12
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            alignment=1,
            spaceAfter=6
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.white,
            backgroundColor=colors.HexColor('#6c5ce7'),
            spaceBefore=12,
            spaceAfter=6,
            leftIndent=0,
            rightIndent=0
        )
        
        story = []
        
        # HEADER PROFESSIONNEL
        story.append(Paragraph("HRControl", header_style))
        story.append(Paragraph("RAPPORT RH OFFICIEL", subtitle_style))
        story.append(Paragraph("Fiche Employé", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
        
        header_info_data = [
            ["Date:", report_date],
            ["ID Rapport:", report_id]
        ]
        header_info_table = Table(header_info_data, colWidths=[1.5*inch, 3*inch])
        header_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ]))
        story.append(header_info_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Ligne de séparation
        separator = Table([[""]], colWidths=[6.5*inch])
        separator.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#6c5ce7')),
        ]))
        story.append(separator)
        story.append(Spacer(1, 0.2 * inch))
        
        # RÉSUMÉ RH
        summary_text = f"""
        <b>Résumé RH</b><br/>
        Employé avec performance <b>{performance.lower()}</b> et potentiel <b>{potential.lower()}</b>.<br/>
        Risque de départ : <b>{turnover_risk.lower()}</b>.<br/>
        Recommandation : <b>{recommendation}</b>.
        """
        summary_para = Paragraph(summary_text, styles['Normal'])
        summary_frame = Table([[summary_para]], colWidths=[6.5*inch])
        summary_frame.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(summary_frame)
        story.append(Spacer(1, 0.3 * inch))
        
        # Fonction pour créer une section
        def create_section(title, data):
            section_story = []
            
            # Header de section avec fond
            header = Table([[title]], colWidths=[6.5*inch])
            header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#6c5ce7')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            section_story.append(header)
            
            # Tableau de données
            table = Table(data, colWidths=[2*inch, 4.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 0), (1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            section_story.append(table)
            
            return section_story
        
        # Section 1: Informations Personnelles
        info_data = [
            ["Nom:", employee.name],
            ["Email:", employee.email],
            ["Date d'embauche:", employee.date_embauche or "N/A"],
            ["Date de naissance:", employee.date_naissance or "N/A"],
            ["Statut familial:", employee.statut_familial or "N/A"]
        ]
        story.extend(create_section("1. INFORMATIONS PERSONNELLES", info_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 2: Informations Poste
        position_data = [
            ["Poste:", employee.poste or "N/A"],
            ["Département:", employee.departement or "N/A"],
            ["Niveau:", employee.niveau or "N/A"],
            ["Statut:", employee.statut or "N/A"]
        ]
        story.extend(create_section("2. INFORMATIONS POSTE", position_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 3: Rémunération
        salary_data = [
            ["Salaire de base:", f"{salaire_base:.2f} $"],
            ["Prime:", f"{prime:.2f} $"],
            ["Transport:", f"{transport:.2f} $"],
            ["Assurance:", f"{assurance:.2f} $"],
            ["TOTAL:", f"{salaire_total:.2f} $"]
        ]
        salary_table = Table(salary_data, colWidths=[2*inch, 4.5*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#6c5ce7')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 11),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(salary_table)
        
        salary_details = Table(salary_data[:-1], colWidths=[2*inch, 4.5*inch])
        salary_details.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(salary_details)
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 4: Métriques de Performance
        metrics_data = [
            ["Score:", f"{score}/100"],
            ["Performance:", performance],
            ["Potentiel:", potential],
            ["Risque Turnover:", turnover_risk]
        ]
        story.extend(create_section("4. MÉTRIQUES DE PERFORMANCE", metrics_data))
        story.append(Spacer(1, 0.2 * inch))
        
        # Section 5: Commentaire
        comment_text = f"""
        <b>5. COMMENTAIRE</b><br/><br/>
        {employee.name} a un score de {score}/100 avec une performance {performance.lower()} et un potentiel {potential.lower()}.<br/><br/>
        """
        if turnover_risk == "Élevé":
            comment_text += "Le risque de départ est élevé, une attention particulière est recommandée."
        elif turnover_risk == "Moyen":
            comment_text += "Le risque de départ est moyen, un suivi régulier est conseillé."
        else:
            comment_text += "Le risque de départ est faible, l'employé est stable."
        
        comment_para = Paragraph(comment_text, styles['Normal'])
        comment_frame = Table([[comment_para]], colWidths=[6.5*inch])
        comment_frame.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(comment_frame)
        story.append(Spacer(1, 0.3 * inch))
        
        # Section 6: Approbations RH
        approval_header = Table([["6. APPROBATIONS"]], colWidths=[6.5*inch])
        approval_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#6c5ce7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(approval_header)
        
        approval_data = [
            ["Manager :", "_________________________"],
            ["RH :", "_________________________"],
            ["Direction :", "_________________________"],
            ["Date :", "_________________________"]
        ]
        approval_table = Table(approval_data, colWidths=[2*inch, 4.5*inch])
        approval_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(approval_table)
        story.append(Spacer(1, 0.4 * inch))
        
        # Footer
        footer_text = "Document généré automatiquement par HRControl – confidentiel"
        footer_para = Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        ))
        story.append(footer_para)
        
        # Build PDF
        doc.build(story)
        
        return FileResponse(filename, media_type='application/pdf', filename=filename)
    finally:
        db.close()
