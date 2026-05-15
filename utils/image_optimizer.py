import os
from PIL import Image
from pathlib import Path


class ImageOptimizer:
    
    MAX_WIDTH = 400
    MAX_HEIGHT = 400
    MAX_FILE_SIZE = 200 * 1024
    QUALITY = 85
    OUTPUT_DIR = "assets/image/products"
    ALLOWED_FORMATS = {'jpg', 'jpeg', 'png', 'webp'}
    
    @staticmethod
    def ensure_output_dir():
        os.makedirs(ImageOptimizer.OUTPUT_DIR, exist_ok=True)
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"
    
    @staticmethod
    def optimize_image(source_path: str, product_id: int) -> tuple[str, bool, str]:
        try:
            if not os.path.exists(source_path):
                return "", False, "File tidak ditemukan"
            
            ext = Path(source_path).suffix.lower().lstrip('.')
            if ext not in ImageOptimizer.ALLOWED_FORMATS:
                return "", False, f"Format gambar tidak didukung. Gunakan: {', '.join(ImageOptimizer.ALLOWED_FORMATS)}"
            
            ImageOptimizer.ensure_output_dir()
            
            img = Image.open(source_path)
            
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            img.thumbnail((ImageOptimizer.MAX_WIDTH, ImageOptimizer.MAX_HEIGHT), Image.Resampling.LANCZOS)
            
            output_filename = f"product_{product_id}.jpg"
            output_path = os.path.join(ImageOptimizer.OUTPUT_DIR, output_filename)
            
            quality = ImageOptimizer.QUALITY
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            while ImageOptimizer.get_file_size(output_path) > ImageOptimizer.MAX_FILE_SIZE and quality > 50:
                quality -= 5
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            final_size = ImageOptimizer.get_file_size(output_path)
            size_str = ImageOptimizer.format_file_size(final_size)
            
            return output_path, True, f"Gambar berhasil disimpan ({size_str})"
            
        except Exception as e:
            return "", False, f"Gagal mengkompresi gambar: {str(e)}"
    
    @staticmethod
    def delete_image(image_path: str) -> bool:
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                return True
        except Exception as e:
            print(f"Gagal menghapus gambar: {e}")
        return False
    
    @staticmethod
    def file_size_valid(filepath: str) -> tuple[bool, str]:
        if not os.path.exists(filepath):
            return False, "File tidak ditemukan"
        
        size = ImageOptimizer.get_file_size(filepath)
        max_initial = 500 * 1024  # 500 KB untuk upload awal
        
        if size > max_initial:
            return False, f"Ukuran gambar terlalu besar ({ImageOptimizer.format_file_size(size)}). Maksimal 500 KB"
        
        return True, f"Ukuran file: {ImageOptimizer.format_file_size(size)}"
