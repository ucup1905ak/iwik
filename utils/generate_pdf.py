from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os


def generate_pdf_report(data, filename='sales_report.pdf', title='Sales Report'):
    """
    Generate PDF report with sales data
    
    Args:
        data: List of tuples containing table rows
        filename: Output PDF filename (supports full path)
        title: Title of the report
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create directory if it doesn't exist
        filepath = os.path.normpath(filename)
        dirpath = os.path.dirname(filepath)
        
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Title
        title_para = Paragraph(title, title_style)
        elements.append(title_para)
        
        # Timestamp
        timestamp = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        elements.append(timestamp)
        elements.append(Spacer(1, 12))
        
        # Create table
        if data:
            table = Table(data, colWidths=[1.2*inch]*len(data[0]))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        return True, f"PDF berhasil dibuat: {filepath}"
    except Exception as e:
        return False, f"Error generating PDF: {str(e)}"
