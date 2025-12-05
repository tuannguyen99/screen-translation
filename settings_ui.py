"""
Settings UI for configuration - Modern dark theme
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QComboBox, QPushButton, QGroupBox,
                              QSpinBox, QMessageBox, QFormLayout, QApplication,
                              QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class OllamaTestThread(QThread):
    """Background thread for testing Ollama connection"""
    finished = pyqtSignal(bool, str, list)  # success, message, model_names
    
    def __init__(self, url, model):
        super().__init__()
        self.url = url
        self.model = model
    
    def run(self):
        """Run the test in background"""
        import requests
        
        try:
            # Test connection
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            if response.status_code != 200:
                self.finished.emit(False, f"HTTP {response.status_code}", [])
                return
            
            # Check if model exists
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            model_exists = any(self.model in name or name in self.model for name in model_names)
            
            if not model_exists:
                msg = f"Model '{self.model}' is not installed.\n\nAvailable models:\n" + "\n".join(model_names) + f"\n\nTo install:\nollama pull {self.model}"
                self.finished.emit(False, msg, model_names)
                return
            
            # Test the model with a simple query
            test_response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "Hello",
                    "stream": False
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                msg = f"✓ Connection to Ollama: OK\n✓ Model '{self.model}': Available and Working\n\nAll models:\n" + "\n".join(model_names)
                self.finished.emit(True, msg, model_names)
            else:
                msg = f"Model '{self.model}' exists but failed to respond.\nHTTP {test_response.status_code}"
                self.finished.emit(False, msg, model_names)
                
        except Exception as e:
            self.finished.emit(False, f"Cannot connect to Ollama at {self.url}\n\nError: {str(e)}\n\nMake sure Ollama is running.", [])


class SettingsWidget(QWidget):
    """Settings configuration UI with modern dark theme"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.test_thread = None
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components with modern styling"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Apply dark theme to settings
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 12px;
                margin-top: 12px;
                padding: 16px;
                font-weight: 600;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #9090b0;
            }
            QLabel {
                color: #b0b0c0;
            }
            QComboBox {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 20px;
                color: #e0e0e0;
            }
            QComboBox:hover {
                border: 1px solid #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                selection-background-color: #6366f1;
            }
            QLineEdit {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
            }
            QSpinBox {
                background-color: #252540;
                border: 1px solid #3a3a5a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e0e0e0;
            }
            QSpinBox:focus {
                border: 1px solid #6366f1;
            }
            QPushButton {
                background-color: #2a2a4a;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3a3a5a;
            }
            QPushButton:pressed {
                background-color: #4a4a6a;
            }
        """)
        
        # OCR Settings - NEW SECTION
        ocr_group = QGroupBox("🔍 OCR Settings (Text Recognition)")
        ocr_layout = QFormLayout()
        ocr_layout.setSpacing(12)
        
        self.ocr_engine_combo = QComboBox()
        self.ocr_engine_combo.addItems([
            'auto (Recommended - Best for general use)',
            'windows (Windows OCR - UI/documents)',
            'manga (MangaOCR - Manga speech bubbles)',
            'tesseract (Tesseract - Other languages)'
        ])
        ocr_layout.addRow("OCR Engine:", self.ocr_engine_combo)
        
        ocr_note = QLabel("💡 Windows OCR works best for UI text and documents.\n    MangaOCR is for manga-style text in speech bubbles.")
        ocr_note.setStyleSheet("font-size: 11px; color: #6a6a8a; padding: 4px 0;")
        ocr_note.setWordWrap(True)
        ocr_layout.addRow("", ocr_note)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Translation Settings
        trans_group = QGroupBox("🌐 Translation Settings")
        trans_layout = QFormLayout()
        trans_layout.setSpacing(12)
        
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems([
            'en (English)',
            'es (Spanish)',
            'fr (French)',
            'de (German)',
            'it (Italian)',
            'pt (Portuguese)',
            'ru (Russian)',
            'ja (Japanese)',
            'ko (Korean)',
            'zh (Chinese)',
            'ar (Arabic)',
            'hi (Hindi)'
        ])
        trans_layout.addRow("Target Language:", self.target_lang_combo)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(['google', 'ollama'])  # Google first as default
        self.backend_combo.currentTextChanged.connect(self.on_backend_changed)
        trans_layout.addRow("Translation Backend:", self.backend_combo)
        
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)
        
        # Ollama Settings
        self.ollama_group = QGroupBox("🤖 Ollama Settings (Offline Translation)")
        ollama_layout = QFormLayout()
        ollama_layout.setSpacing(12)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_url_input.textChanged.connect(self.on_ollama_url_changed)
        ollama_layout.addRow("Ollama URL:", self.ollama_url_input)
        
        # Model selection with refresh button
        model_layout = QHBoxLayout()
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.setPlaceholderText("Select or enter model name")
        model_layout.addWidget(self.ollama_model_combo, 1)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.clicked.connect(self.refresh_ollama_models)
        model_layout.addWidget(refresh_btn)
        
        ollama_layout.addRow("Model:", model_layout)
        
        # Test connection button
        test_btn = QPushButton("🧪 Test Connection & Model")
        test_btn.clicked.connect(self.test_ollama_connection)
        ollama_layout.addRow("", test_btn)
        
        self.ollama_group.setLayout(ollama_layout)
        layout.addWidget(self.ollama_group)
        
        # Display Settings
        display_group = QGroupBox("🎨 Display Settings")
        display_layout = QFormLayout()
        display_layout.setSpacing(12)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 36)
        self.font_size_spin.setValue(16)
        display_layout.addRow("Result Font Size:", self.font_size_spin)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c7ff7, stop:1 #9d6ff9);
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("↩️ Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_backend_changed(self, backend):
        """Show/hide backend-specific settings"""
        self.ollama_group.setVisible(backend == 'ollama')
        
        # Load Ollama models when backend is selected
        if backend == 'ollama':
            self.refresh_ollama_models()
    
    def load_settings(self):
        """Load settings from config"""
        config = self.config_manager.config
        
        # OCR Engine
        ocr_engine = config.get('ocr_engine', 'auto')
        for i in range(self.ocr_engine_combo.count()):
            if self.ocr_engine_combo.itemText(i).startswith(ocr_engine):
                self.ocr_engine_combo.setCurrentIndex(i)
                break
        
        # Target language - default to English for Japanese translation use case
        target_lang = config.get('target_language', 'en')
        for i in range(self.target_lang_combo.count()):
            if self.target_lang_combo.itemText(i).startswith(target_lang):
                self.target_lang_combo.setCurrentIndex(i)
                break
        
        # Backend - default to Google for better online translation
        backend = config.get('translation_backend', 'google')
        self.backend_combo.setCurrentText(backend)
        
        # Ollama
        self.ollama_url_input.setText(config.get('ollama_url', 'http://localhost:11434'))
        
        # Load available models first
        self.refresh_ollama_models()
        
        # Set saved model
        saved_model = config.get('ollama_model', 'gemma')
        self.ollama_model_combo.setCurrentText(saved_model)
        
        # Display
        self.font_size_spin.setValue(config.get('result_font_size', 16))
        
        # Show/hide groups
        self.on_backend_changed(backend)
    
    def save_settings(self):
        """Save settings to config"""
        # Extract engine and language codes
        ocr_engine = self.ocr_engine_combo.currentText().split(' ')[0]
        target_lang = self.target_lang_combo.currentText().split(' ')[0]
        
        updates = {
            'ocr_engine': ocr_engine,
            'target_language': target_lang,
            'translation_backend': self.backend_combo.currentText(),
            'ollama_url': self.ollama_url_input.text(),
            'ollama_model': self.ollama_model_combo.currentText(),
            'result_font_size': self.font_size_spin.value()
        }
        
        self.config_manager.update(updates)
        
        QMessageBox.information(self, "✓ Success", "Settings saved successfully!")
    
    def reset_settings(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config = self.config_manager.load_config()
            self.config_manager.save_config()
            self.load_settings()
            QMessageBox.information(self, "✓ Success", "Settings reset to defaults!")
    
    def refresh_ollama_models(self):
        """Refresh available Ollama models"""
        import requests
        
        url = self.ollama_url_input.text() or "http://localhost:11434"
        current_text = self.ollama_model_combo.currentText()
        
        self.ollama_model_combo.clear()
        
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    model_names = [m['name'] for m in models]
                    self.ollama_model_combo.addItems(model_names)
                    
                    if current_text:
                        index = self.ollama_model_combo.findText(current_text)
                        if index >= 0:
                            self.ollama_model_combo.setCurrentIndex(index)
                        else:
                            self.ollama_model_combo.setCurrentText(current_text)
                    elif model_names:
                        self.ollama_model_combo.setCurrentIndex(0)
                else:
                    self.ollama_model_combo.setPlaceholderText("No models found - run 'ollama pull <model>'")
        except Exception as e:
            self.ollama_model_combo.setPlaceholderText(f"Cannot connect - {str(e)[:30]}")
    
    def on_ollama_url_changed(self):
        """Called when Ollama URL changes"""
        pass
    
    def test_ollama_connection(self):
        """Test Ollama connection and model availability"""
        url = self.ollama_url_input.text() or "http://localhost:11434"
        model = self.ollama_model_combo.currentText()
        
        if not model:
            QMessageBox.warning(
                self,
                "No Model Selected",
                "Please select or enter a model name to test."
            )
            return
        
        test_btn = self.sender()
        if test_btn:
            test_btn.setEnabled(False)
            test_btn.setText("Testing...")
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        self.test_thread = OllamaTestThread(url, model)
        self.test_thread.finished.connect(lambda success, msg, models: self._on_test_complete(success, msg, models, test_btn))
        self.test_thread.start()
    
    def _on_test_complete(self, success, message, model_names, test_btn):
        """Handle test completion"""
        QApplication.restoreOverrideCursor()
        
        if test_btn:
            test_btn.setEnabled(True)
            test_btn.setText("🧪 Test Connection & Model")
        
        if success:
            QMessageBox.information(self, "✓ Test Successful", message)
        else:
            QMessageBox.warning(self, "✗ Test Failed", message)
