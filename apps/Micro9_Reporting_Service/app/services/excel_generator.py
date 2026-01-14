"""
Excel Generator using openpyxl
KISS principle: Simple Excel file generation
"""
import logging
from typing import Dict, Any, List
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelGenerator:
    """
    Generate Excel reports using openpyxl
    """
    
    def generate_report(
        self,
        file_path: str,
        title: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Generate Excel report
        
        Args:
            file_path: Output file path
            title: Report title
            data: Report data with sheets
        
        Returns:
            bool: True if successful
        """
        try:
            # Create workbook
            wb = Workbook()
            
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Add metadata sheet
            ws_meta = wb.create_sheet("Información")
            ws_meta['A1'] = "Reporte"
            ws_meta['B1'] = title
            ws_meta['A2'] = "Generado"
            ws_meta['B2'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self._style_header(ws_meta, 'A1:B2')
            
            # Add data sheets
            if 'sheets' in data:
                for sheet_data in data['sheets']:
                    self._create_sheet(wb, sheet_data)
            
            # Save workbook
            wb.save(file_path)
            logger.info(f"Excel generated successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating Excel: {str(e)}")
            return False
    
    def _create_sheet(self, wb: Workbook, sheet_data: Dict):
        """Create a data sheet"""
        name = sheet_data.get('name', 'Data')
        headers = sheet_data.get('headers', [])
        rows = sheet_data.get('rows', [])
        
        ws = wb.create_sheet(name)
        
        # Add headers
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Add rows
        for row_idx, row in enumerate(rows, start=2):
            for col_idx, value in enumerate(row, start=1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # Auto-size columns
        for col_idx in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 15
    
    def _style_header(self, ws, range_str: str):
        """Style header cells"""
        for row in ws[range_str]:
            for cell in row:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="left")


# Global instance
excel_generator = ExcelGenerator()
