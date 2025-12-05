"""
OCR module with Manga OCR for Japanese and Tesseract for other languages
"""
import pytesseract
from PIL import Image
import os


class OCREngine:
    """Text extraction with Manga OCR (Japanese) and Tesseract fallback"""
    
    # Supported OCR engines
    ENGINE_AUTO = 'auto'        # Auto-detect: use MangaOCR for Japanese
    ENGINE_MANGA_OCR = 'manga'  # Force Manga OCR (best for Japanese)
    ENGINE_TESSERACT = 'tesseract'  # Force Tesseract
    
    def __init__(self, engine='auto'):
        self.engine = engine
        self._manga_ocr = None  # Lazy loaded (takes a few seconds first time)
        self._manga_ocr_loading = False
        
        # Set Tesseract path for Windows
        if os.name == 'nt':
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def set_engine(self, engine):
        """Set OCR engine"""
        self.engine = engine
    
    def _get_manga_ocr(self):
        """Lazy load Manga OCR model (downloads on first use)"""
        if self._manga_ocr is None and not self._manga_ocr_loading:
            self._manga_ocr_loading = True
            try:
                from manga_ocr import MangaOcr
                self._manga_ocr = MangaOcr()
            except Exception as e:
                print(f"Failed to load Manga OCR: {e}")
                self._manga_ocr = None
            finally:
                self._manga_ocr_loading = False
        return self._manga_ocr
    
    def extract_text(self, image):
        """
        Extract text from image
        
        Args:
            image: PIL Image object
            
        Returns:
            str: Extracted text
        """
        if image is None:
            return ""
        
        try:
            if self.engine == self.ENGINE_MANGA_OCR:
                return self._extract_with_manga_ocr(image)
            elif self.engine == self.ENGINE_TESSERACT:
                return self._extract_with_tesseract(image)
            else:  # AUTO
                # Try Manga OCR first (best for Japanese)
                result = self._extract_with_manga_ocr(image)
                if result and not result.startswith("OCR Error"):
                    return result
                # Fallback to Tesseract
                return self._extract_with_tesseract(image)
                
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def _extract_with_manga_ocr(self, image):
        """Extract text using Manga OCR (optimized for Japanese)"""
        try:
            manga_ocr = self._get_manga_ocr()
            if manga_ocr is None:
                return "OCR Error: Manga OCR not available"
            
            # Manga OCR works directly with PIL images
            text = manga_ocr(image)
            return text.strip() if text else ""
        except Exception as e:
            return f"OCR Error (MangaOCR): {str(e)}"
    
    def _extract_with_tesseract(self, image, lang=None):
        """Extract text using Tesseract"""
        try:
            if lang is None:
                # Use Japanese + English for best results
                lang = 'jpn+jpn_vert+eng'
            
            text = pytesseract.image_to_string(
                image,
                lang=lang,
                config='--psm 6'  # Assume uniform block of text
            )
            return text.strip()
        except Exception as e:
            # Try with just English if Japanese isn't installed
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang='eng',
                    config='--psm 6'
                )
                return text.strip()
            except:
                return f"OCR Error (Tesseract): {str(e)}"
    
    def get_available_languages(self):
        """Get list of installed Tesseract languages"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except:
            return ['eng']
    
    def is_manga_ocr_available(self):
        """Check if Manga OCR is available"""
        try:
            from manga_ocr import MangaOcr
            return True
        except:
            return False
