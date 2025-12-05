"""
Translation module with multiple backends
"""
import requests
import json
from typing import Optional


class TranslationEngine:
    """Handle translation with multiple backends"""
    
    def __init__(self, config):
        self.config = config
        self.backend = config.get('translation_backend', 'ollama')
        
    def set_backend(self, backend):
        """Set translation backend"""
        self.backend = backend
        
    def translate(self, text, target_lang=None):
        """
        Translate text using configured backend
        
        Args:
            text: Text to translate
            target_lang: Target language code
            
        Returns:
            str: Translated text
        """
        if not text or not text.strip():
            return ""
        
        target_lang = target_lang or self.config.get('target_language', 'es')
        
        try:
            if self.backend == 'google':
                return self._translate_google(text, target_lang)
            elif self.backend == 'ollama':
                return self._translate_ollama(text, target_lang)
            else:
                return f"Unknown backend: {self.backend}"
        except Exception as e:
            return f"Translation Error: {str(e)}"
    
    def _translate_google(self, text, target_lang):
        """Translate using Google Translate (free deep-translator library)"""
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='auto', target=target_lang)
            result = translator.translate(text)
            return result
        except Exception as e:
            return f"Google Translate Error: {str(e)}"
    
    def _translate_ollama(self, text, target_lang):
        """Translate using Ollama (offline)"""
        url = self.config.get('ollama_url', 'http://localhost:11434')
        model = self.config.get('ollama_model', 'gemma')
        
        # Language code to full name mapping
        lang_names = {
            'es': 'Spanish',
            'en': 'English',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
        }
        
        lang_name = lang_names.get(target_lang, target_lang)
        
        try:
            prompt = f"Translate the following text to {lang_name}. Return only the translation, no explanations or additional text:\n\n{text}"
            
            response = requests.post(
                f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                translation = result.get('response', '').strip()
                return translation
            elif response.status_code == 404:
                # Model not found - try to provide helpful error
                try:
                    tags_response = requests.get(f"{url}/api/tags", timeout=5)
                    if tags_response.status_code == 200:
                        available_models = [m['name'] for m in tags_response.json().get('models', [])]
                        return f"Ollama Error: Model '{model}' not found.\n\nAvailable models: {', '.join(available_models)}\n\nPlease update the model name in Settings."
                except:
                    pass
                return f"Ollama Error: Model '{model}' not found (HTTP 404).\n\nPlease check the model name in Settings or run: ollama pull {model}"
            else:
                return f"Ollama Error: HTTP {response.status_code} - {response.text[:200]}"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Is it running?"
        except requests.exceptions.Timeout:
            return "Error: Ollama request timed out. The model might be loading or the prompt is too long."
        except Exception as e:
            return f"Ollama Error: {str(e)}"
    
    def test_connection(self):
        """Test if the current backend is accessible"""
        if self.backend == 'google':
            return True, "OK"
        elif self.backend == 'ollama':
            try:
                url = self.config.get('ollama_url', 'http://localhost:11434')
                response = requests.get(f"{url}/api/tags", timeout=5)
                return response.status_code == 200, "OK" if response.status_code == 200 else "Cannot connect"
            except:
                return False, "Cannot connect to Ollama"
        return False, "Unknown backend"
