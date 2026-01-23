"""
PDF Generator using ReportLab
KISS principle: Simple PDF generation with charts
"""
import io
import logging
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generate PDF reports using ReportLab
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_report(
        self,
        file_path: str,
        title: str,
        data: Dict[str, Any],
        include_charts: bool = True
    ) -> bool:
        """
        Generate PDF report
        
        Args:
            file_path: Output file path
            title: Report title
            data: Report data
            include_charts: Include charts in report
        
        Returns:
            bool: True if successful
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build story
            story = []
            
            # Title
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 0.2*inch))
            
            # Metadata
            metadata = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(metadata, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Add sections from data
            if 'summary' in data:
                story.append(Paragraph("Resumen Ejecutivo", self.styles['CustomHeading']))
                story.append(Paragraph(data['summary'], self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Add tables
            if 'tables' in data:
                for table_data in data['tables']:
                    story.append(self._create_table(table_data))
                    story.append(Spacer(1, 0.2*inch))
            
            # Add charts
            if include_charts and 'charts' in data:
                for chart_data in data['charts']:
                    chart_image = self._create_chart(chart_data)
                    if chart_image:
                        story.append(chart_image)
                        story.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF generated successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return False
    
    def _create_table(self, table_data: Dict) -> Table:
        """Create a formatted table"""
        title = table_data.get('title', '')
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        # Prepare data
        data = [headers] + rows
        
        # Create table
        table = Table(data)
        
        # Style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_chart(self, chart_data: Dict) -> Image:
        """Create a chart image"""
        try:
            chart_type = chart_data.get('type', 'bar')
            title = chart_data.get('title', '')
            labels = chart_data.get('labels', [])
            values = chart_data.get('values', [])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 5))
            
            if chart_type == 'bar':
                ax.bar(labels, values, color='#1976d2')
            elif chart_type == 'pie':
                ax.pie(values, labels=labels, autopct='%1.1f%%')
            elif chart_type == 'line':
                ax.plot(labels, values, marker='o', color='#1976d2')
            
            ax.set_title(title)
            plt.tight_layout()
            
            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150)
            buffer.seek(0)
            plt.close(fig)
            
            # Create Image
            img = Image(buffer, width=5*inch, height=3*inch)
            return img
            
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return None


# Global instance
pdf_generator = PDFGenerator()
