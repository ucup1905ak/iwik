import csv
import os
from datetime import datetime


def export_to_csv(data, filename='sales_export.csv'):
    """
    Export data to CSV file
    
    Args:
        data: List of tuples/lists containing table rows
        filename: Output CSV filename
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Create assets/csv directory if it doesn't exist
        csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'csv')
        os.makedirs(csv_dir, exist_ok=True)
        
        filepath = os.path.join(csv_dir, filename)
        
        if not data:
            return False, "Data kosong, tidak ada yang diekspor"
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        
        return True, f"CSV berhasil dibuat: {filepath}"
    except Exception as e:
        return False, f"Error exporting to CSV: {str(e)}"
