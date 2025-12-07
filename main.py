"""
Main Application - Screen Translation for Japanese Text
Modern, intuitive UI designed for reading Japanese papers/newspapers
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QTextEdit, QLabel,
                              QTabWidget, QFrame, QSplitter, QGraphicsDropShadowEffect,
                              QSizePolicy, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QKeySequence, QShortcut, QPainter, QLinearGradient

from screen_capture import ScreenSelector
from ocr_engine import OCREngine
from translation_engine import TranslationEngine
from config_manager import ConfigManager
from settings_ui import SettingsWidget


class ProcessingThread(QThread):
    """Background thread for OCR and translation"""
    progress = pyqtSignal(str)  # Status updates
    finished = pyqtSignal(str, str, str)  # original, translated, status
    
    def __init__(self, image, ocr_engine, translation_engine, target_lang):
        super().__init__()
        self.image = image
        self.ocr_engine = ocr_engine
        self.translation_engine = translation_engine
        self.target_lang = target_lang
    
    def run(self):
        """Process image in background"""
        # OCR
        self.progress.emit("Extracting Japanese text...")
        original_text = self.ocr_engine.extract_text(self.image)
        
        if not original_text or original_text.startswith("OCR Error"):
            self.finished.emit(original_text, "", "OCR failed")
            return
        
        # Translation
        self.progress.emit("Translating to English...")
        translated_text = self.translation_engine.translate(original_text, self.target_lang)
        
        self.finished.emit(original_text, translated_text, "Completed")


class ImagePreviewWidget(QFrame):
    """Widget to show preview of captured image"""
    
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.setMinimumSize(200, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 2px dashed #4a4a6a;
                border-radius: 12px;
            }
        """)
        
    def set_image(self, pixmap):
        """Set the preview image"""
        self.pixmap = pixmap
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 2px solid #6366f1;
                border-radius: 12px;
            }
        """)
        self.update()
        
    def clear_image(self):
        """Clear the preview"""
        self.pixmap = None
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 2px dashed #4a4a6a;
                border-radius: 12px;
            }
        """)
        self.update()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.pixmap:
            # Scale pixmap to fit while maintaining aspect ratio
            scaled = self.pixmap.scaled(
                self.size() - self.size() * 0.1,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Draw placeholder text
            painter.setPen(QColor("#6a6a8a"))
            font = QFont("Segoe UI", 11)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                           "📷 Captured image\nwill appear here")


class MainWindow(QMainWindow):
    """Main application window with modern UI for Japanese translation"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.ocr_engine = OCREngine(engine='auto')  # Auto: Windows OCR or Manga OCR
        self.translation_engine = TranslationEngine(self.config_manager.config)
        self.screen_selector = ScreenSelector()
        
        # Connect screen selector
        self.screen_selector.hide()
        
        self.processing_thread = None
        self.captured_pixmap = None
        
        self.init_ui()
        self.setup_shortcuts()
        self.update_language_labels()  # Set labels based on config
        
    def init_ui(self):
        """Initialize modern UI"""
        self.setWindowTitle("📖 Screen Translator")
        self.setGeometry(100, 100, 1000, 750)
        
        # Dark theme with gradient accents
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f1a;
            }
            QWidget {
                font-family: 'Segoe UI', 'Meiryo UI', sans-serif;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: none;
                background-color: #16162a;
                border-radius: 12px;
            }
            QTabBar::tab {
                background-color: #1a1a2e;
                color: #8888aa;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #16162a;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #202040;
            }
            QTextEdit {
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                selection-background-color: #6366f1;
            }
            QTextEdit:focus {
                border: 1px solid #6366f1;
            }
            QPushButton {
                background-color: #2a2a4a;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a5a;
            }
            QPushButton:pressed {
                background-color: #4a4a6a;
            }
            QLabel {
                color: #b0b0c0;
            }
            QSplitter::handle {
                background-color: #2a2a4a;
                height: 2px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Main tab
        main_tab = self.create_main_tab()
        tabs.addTab(main_tab, "🎯 Capture & Translate")
        
        # Settings tab
        self.settings_widget = SettingsWidget(self.config_manager)
        self.settings_widget.settings_changed.connect(self.update_language_labels)  # Live refresh
        tabs.addTab(self.settings_widget, "⚙️ Settings")
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
        
    def create_main_tab(self):
        """Create main capture tab with modern design"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Header with title and shortcut hint
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("English ↔ Japanese Screen Translator")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            padding: 8px 0;
        """)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        shortcut_hint = QLabel("💡 Tip: Press Ctrl+Shift+C to capture")
        shortcut_hint.setStyleSheet("""
            background-color: #252540;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            color: #8888aa;
        """)
        header_layout.addWidget(shortcut_hint)
        
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Main content area
        content = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        # Left side: Capture button and preview
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        
        # Big capture button
        self.capture_btn = QPushButton("📷  Start Capture")
        self.capture_btn.setMinimumHeight(70)
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
                font-size: 18px;
                font-weight: 600;
                border-radius: 16px;
                padding: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c7ff7, stop:1 #9d6ff9);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5558e3, stop:1 #7a4fd3);
            }
            QPushButton:disabled {
                background: #3a3a5a;
                color: #6a6a8a;
            }
        """)
        self.capture_btn.clicked.connect(self.start_capture)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(99, 102, 241, 100))
        shadow.setOffset(0, 4)
        self.capture_btn.setGraphicsEffect(shadow)
        
        left_layout.addWidget(self.capture_btn)
        
        # Image preview
        preview_label = QLabel("📸 Captured Region")
        preview_label.setStyleSheet("font-weight: 600; color: #9090b0; margin-top: 8px;")
        left_layout.addWidget(preview_label)
        
        self.image_preview = ImagePreviewWidget()
        self.image_preview.setMinimumSize(280, 200)
        left_layout.addWidget(self.image_preview)
        
        # Status label
        self.status_label = QLabel("Ready - Select a screen area to translate")
        self.status_label.setStyleSheet("""
            background-color: #1a2a1a;
            color: #4ade80;
            padding: 12px 16px;
            border-radius: 10px;
            font-weight: 500;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.status_label)
        
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(320)
        
        content_layout.addWidget(left_panel)
        
        # Right side: Text results
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)
        
        # Vertical splitter for original and translated text
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)
        
        # Original text box (dynamically labeled)
        original_group = QWidget()
        original_layout = QVBoxLayout()
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.setSpacing(8)
        
        original_header = QHBoxLayout()
        self.original_label = QLabel("🇯🇵 Original Japanese Text")
        self.original_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #9090b0;")
        original_header.addWidget(self.original_label)
        original_header.addStretch()
        
        copy_original_btn = QPushButton("📋 Copy")
        copy_original_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_original_btn.clicked.connect(lambda: self.copy_text(self.original_text))
        original_header.addWidget(copy_original_btn)
        original_layout.addLayout(original_header)
        
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("Original Japanese text will appear here...")
        self.original_text.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                font-family: 'Meiryo UI', 'Yu Gothic UI', 'Segoe UI', sans-serif;
                line-height: 1.6;
            }
        """)
        original_layout.addWidget(self.original_text)
        
        original_group.setLayout(original_layout)
        splitter.addWidget(original_group)
        
        # Translated text box (dynamically labeled)
        translated_group = QWidget()
        translated_layout = QVBoxLayout()
        translated_layout.setContentsMargins(0, 0, 0, 0)
        translated_layout.setSpacing(8)
        
        translated_header = QHBoxLayout()
        self.translated_label = QLabel("🇬🇧 English Translation")
        self.translated_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #9090b0;")
        translated_header.addWidget(self.translated_label)
        translated_header.addStretch()
        
        copy_translated_btn = QPushButton("📋 Copy")
        copy_translated_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_translated_btn.clicked.connect(lambda: self.copy_text(self.translated_text))
        translated_header.addWidget(copy_translated_btn)
        translated_layout.addLayout(translated_header)
        
        self.translated_text = QTextEdit()
        self.translated_text.setReadOnly(True)
        self.translated_text.setPlaceholderText("English translation will appear here...")
        font_size = self.config_manager.get('result_font_size', 16)
        self.translated_text.setStyleSheet(f"""
            QTextEdit {{
                font-size: {font_size}px;
                line-height: 1.6;
            }}
        """)
        translated_layout.addWidget(self.translated_text)
        
        translated_group.setLayout(translated_layout)
        splitter.addWidget(translated_group)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 300])
        
        right_layout.addWidget(splitter)
        
        # Action buttons row
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_results)
        action_layout.addWidget(clear_btn)
        
        action_layout.addStretch()
        
        right_layout.addLayout(action_layout)
        
        right_panel.setLayout(right_layout)
        content_layout.addWidget(right_panel)
        
        content.setLayout(content_layout)
        layout.addWidget(content)
        
        widget.setLayout(layout)
        return widget
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+Shift+C for capture
        capture_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        capture_shortcut.activated.connect(self.start_capture)
        
        # Escape to cancel
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.cancel_capture)
    
    def update_language_labels(self):
        """Update UI labels based on source/target language settings"""
        source_lang = self.config_manager.get('source_language', 'ja')
        target_lang = self.config_manager.get('target_language', 'en')
        
        # Language display names and flags
        lang_info = {
            'ja': ('🇯🇵', 'Japanese'),
            'en': ('🇬🇧', 'English'),
            'es': ('🇪🇸', 'Spanish'),
            'fr': ('🇫🇷', 'French'),
            'de': ('🇩🇪', 'German'),
            'it': ('🇮🇹', 'Italian'),
            'pt': ('🇵🇹', 'Portuguese'),
            'ru': ('🇷🇺', 'Russian'),
            'ko': ('🇰🇷', 'Korean'),
            'zh': ('🇨🇳', 'Chinese'),
            'ar': ('🇸🇦', 'Arabic'),
            'hi': ('🇮🇳', 'Hindi'),
        }
        
        source_flag, source_name = lang_info.get(source_lang, ('🌐', source_lang.upper()))
        target_flag, target_name = lang_info.get(target_lang, ('🌐', target_lang.upper()))
        
        # Update original text label
        self.original_label.setText(f"{source_flag} Original {source_name} Text")
        
        # Update translated text label
        self.translated_label.setText(f"{target_flag} {target_name} Translation")
        
        # Update placeholder text
        self.original_text.setPlaceholderText(f"Original {source_name} text will appear here...")
        self.translated_text.setPlaceholderText(f"{target_name} translation will appear here...")
    
    def start_capture(self):
        """Start screen capture"""
        self.update_status("Select screen area...", "warning")
        self.capture_btn.setEnabled(False)
        
        # Hide main window and wait for it to disappear
        self.hide()
        QApplication.processEvents()
        
        # Delay to ensure window is fully hidden
        QTimer.singleShot(200, self._do_capture)
    
    def _do_capture(self):
        """Perform the actual screen capture after delay"""
        self.screen_selector.start_capture()
        
        # Wait for capture completion
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_capture_complete)
        self.check_timer.start(100)
    
    def check_capture_complete(self):
        """Check if capture is complete"""
        if not self.screen_selector.isVisible():
            self.check_timer.stop()
            self.show()
            self.raise_()
            self.activateWindow()
            
            # Get captured image
            image = self.screen_selector.get_selected_image()
            
            if image:
                # Store pixmap for preview
                self.captured_pixmap = self.screen_selector.selected_area
                if self.captured_pixmap:
                    self.image_preview.set_image(self.captured_pixmap)
                
                self.process_image(image)
            else:
                self.update_status("Capture cancelled", "error")
                self.capture_btn.setEnabled(True)
    
    def cancel_capture(self):
        """Cancel ongoing capture"""
        if hasattr(self, 'check_timer') and self.check_timer.isActive():
            self.check_timer.stop()
            self.screen_selector.hide()
            self.show()
            self.update_status("Capture cancelled", "error")
            self.capture_btn.setEnabled(True)
    
    def process_image(self, image):
        """Process captured image"""
        # Get source language for appropriate status message
        source_lang = self.config_manager.get('source_language', 'ja')
        target_lang = self.config_manager.get('target_language', 'en')
        
        if source_lang == 'ja':
            self.update_status("Extracting Japanese text...", "info")
        else:
            self.update_status("Extracting English text...", "info")
        
        # DEBUG: Save captured image for inspection
        try:
            debug_path = "debug_capture.png"
            image.save(debug_path)
            print(f"DEBUG: Captured image saved to {debug_path}")
            print(f"DEBUG: Image size: {image.size}, mode: {image.mode}")
        except Exception as e:
            print(f"DEBUG: Could not save debug image: {e}")
        
        # Update engines with latest config
        ocr_engine_setting = self.config_manager.get('ocr_engine', 'auto')
        self.ocr_engine.set_engine(ocr_engine_setting)
        self.ocr_engine.set_source_language(source_lang)  # Set source language for OCR
        
        self.translation_engine.config = self.config_manager.config
        self.translation_engine.backend = self.config_manager.get('translation_backend', 'google')
        
        # Process in background thread
        self.processing_thread = ProcessingThread(
            image,
            self.ocr_engine,
            self.translation_engine,
            target_lang
        )
        self.processing_thread.progress.connect(lambda msg: self.update_status(msg, "info"))
        self.processing_thread.finished.connect(self.on_processing_complete)
        self.processing_thread.start()
    
    def on_processing_complete(self, original, translated, status):
        """Handle processing completion"""
        self.original_text.setText(original)
        self.translated_text.setText(translated)
        
        if status == "Completed":
            self.update_status("✓ Translation completed!", "success")
        else:
            self.update_status(f"✗ {status}", "error")
        
        self.capture_btn.setEnabled(True)
        
        # Update font size
        font_size = self.config_manager.get('result_font_size', 16)
        self.translated_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1a1a2e;
                border: 1px solid #2a2a4a;
                border-radius: 10px;
                padding: 12px;
                font-size: {font_size}px;
                line-height: 1.6;
                selection-background-color: #6366f1;
            }}
            QTextEdit:focus {{
                border: 1px solid #6366f1;
            }}
        """)
    
    def update_status(self, message, status_type="info"):
        """Update status label with colored background"""
        colors = {
            "success": ("#1a2a1a", "#4ade80"),
            "error": ("#2a1a1a", "#f87171"),
            "warning": ("#2a2a1a", "#fbbf24"),
            "info": ("#1a1a2a", "#60a5fa"),
        }
        bg, fg = colors.get(status_type, colors["info"])
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            padding: 12px 16px;
            border-radius: 10px;
            font-weight: 500;
        """)
    
    def copy_text(self, text_edit):
        """Copy text from a text edit to clipboard"""
        text = text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.update_status("✓ Copied to clipboard!", "success")
    
    def clear_results(self):
        """Clear all results"""
        self.original_text.clear()
        self.translated_text.clear()
        self.image_preview.clear_image()
        self.captured_pixmap = None
        self.update_status("Ready - Select a screen area to translate", "success")


def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Japanese Screen Translator")
    app.setStyle("Fusion")  # Modern look across platforms
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
