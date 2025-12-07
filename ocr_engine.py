"""
OCR module with multiple engines:
- Windows OCR (winocr) - Best for general text (Japanese, English, etc.)
- Manga OCR - Best for manga-style text (speech bubbles, stylized fonts)
- Tesseract - Fallback for other languages
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os


class OCREngine:
    """Text extraction with multiple OCR engines"""
    
    # Supported OCR engines
    ENGINE_AUTO = 'auto'           # Auto: Windows OCR (general) or Manga OCR (manga)
    ENGINE_WINDOWS = 'windows'     # Windows OCR - best for UI/documents
    ENGINE_MANGA_OCR = 'manga'     # Manga OCR - best for manga-style text
    ENGINE_TESSERACT = 'tesseract' # Tesseract - fallback
    
    # OCR source language
    LANG_JAPANESE = 'ja'
    LANG_ENGLISH = 'en'
    
    def __init__(self, engine='auto', source_lang='ja'):
        self.engine = engine
        self.source_lang = source_lang  # Language to recognize
        self._manga_ocr = None
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
    
    def set_source_language(self, lang):
        """Set source language for OCR (ja=Japanese, en=English)"""
        self.source_lang = lang
    
    def _get_manga_ocr(self):
        """Lazy load Manga OCR model"""
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
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Scale up small images
        min_dimension = min(image.width, image.height)
        if min_dimension < 100:
            scale_factor = 100 / min_dimension
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
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
            if self.engine == self.ENGINE_WINDOWS:
                return self._extract_with_windows_ocr(image)
            elif self.engine == self.ENGINE_MANGA_OCR:
                return self._extract_with_manga_ocr(image)
            elif self.engine == self.ENGINE_TESSERACT:
                return self._extract_with_tesseract(image)
            else:  # AUTO - try engines in order of reliability
                # Try Windows OCR first (best for general text)
                result = self._extract_with_windows_ocr(image)
                if result and not result.startswith("OCR Error"):
                    return result
                # Fallback to Tesseract (good for documents)
                result = self._extract_with_tesseract(image)
                if result and result.strip() and not result.startswith("OCR Error"):
                    return result
                # Final fallback to Manga OCR (only good for Japanese manga)
                if self.source_lang == self.LANG_JAPANESE:
                    return self._extract_with_manga_ocr(image)
                return result
                
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def _extract_with_windows_ocr(self, image):
        """Extract text using Windows OCR"""
        try:
            import winocr
            import asyncio
            
            # Preprocess
            processed = self._preprocess_image(image)
            
            # Windows OCR is async, need to run in event loop
            lang = self.source_lang  # 'ja' for Japanese, 'en' for English
            
            async def do_ocr():
                result = await winocr.recognize_pil(processed, lang)
                return result
            
            # Run async OCR
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(do_ocr())
            
            # Extract text from result
            if result and hasattr(result, 'text'):
                return result.text.strip()
            elif result:
                if hasattr(result, 'lines'):
                    return '\n'.join([line.text for line in result.lines]).strip()
                return str(result).strip()
            return ""
            
        except ImportError:
            return "OCR Error: winocr not installed. Run: pip install winocr"
        except Exception as e:
            error_msg = str(e)
            # Provide helpful message for missing language pack
            if "Language.OCR" in error_msg or "not installed" in error_msg.lower():
                lang_name = "Japanese (ja-JP)" if self.source_lang == 'ja' else "English (en-US)"
                lang_code = "ja-JP" if self.source_lang == 'ja' else "en-US"
                return f"OCR Error: {lang_name} OCR not installed.\n\nRun as Administrator:\nAdd-WindowsCapability -Online -Name \"Language.OCR~~~{lang_code}~0.0.1.0\""
            return f"OCR Error (Windows OCR): {error_msg}"
    
    def _extract_with_manga_ocr(self, image):
        """Extract text using Manga OCR (optimized for Japanese manga)"""
        try:
            manga_ocr = self._get_manga_ocr()
            if manga_ocr is None:
                return "OCR Error: Manga OCR not available"
            
            processed = self._preprocess_image(image)
            text = manga_ocr(processed)
            return text.strip() if text else ""
        except Exception as e:
            return f"OCR Error (MangaOCR): {str(e)}"
    
    def _extract_with_tesseract(self, image, lang=None):
        """Extract text using Tesseract"""
        try:
            processed = self._preprocess_image(image)
            
            if lang is None:
                # Use appropriate language based on source setting
                if self.source_lang == self.LANG_JAPANESE:
                    lang = 'jpn+jpn_vert+eng'
                else:
                    lang = 'eng'
            
            text = pytesseract.image_to_string(
                processed,
                lang=lang,
                config='--psm 6'
            )
            return text.strip()
        except Exception as e:
            try:
                text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
                return text.strip()
            except:
                return f"OCR Error (Tesseract): {str(e)}"
    
    def get_available_languages(self):
        """Get list of installed Tesseract languages"""
        try:
            return pytesseract.get_languages()
        except:
            return ['eng']
    
    def is_manga_ocr_available(self):
        """Check if Manga OCR is available"""
        try:
            from manga_ocr import MangaOcr
            return True
        except:
            return False
    
    def is_windows_ocr_available(self):
        """Check if Windows OCR is available"""
        try:
            import winocr
            return True
        except:
            return False
