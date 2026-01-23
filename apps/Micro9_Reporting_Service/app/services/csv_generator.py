"""
CSV Generator using pandas
KISS principle: Simple CSV export
"""
import logging
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CSVGenerator:
    """
    Generate CSV reports using pandas
    """
    
    def generate_report(
        self,
        file_path: str,
        title: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Generate CSV report
        
        Args:
            file_path: Output file path  
            title: Report title (added as comment)
            data: Report data
        
        Returns:
            bool: True if successful
        """
        try:
            headers = data.get('headers', [])
            rows = data.get('rows', [])
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Save to CSV
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            logger.info(f"CSV generated successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating CSV: {str(e)}")
            return False


# Global instance
csv_generator = CSVGenerator()
