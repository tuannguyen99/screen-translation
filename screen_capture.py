"""
Screen capture module with drag & drop selection
"""
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, QBuffer, QIODevice
from PyQt6.QtGui import QPainter, QColor, QPen, QScreen, QPixmap
from PIL import Image
import io


class ScreenSelector(QWidget):
    """Transparent overlay for selecting screen area"""
    
    def __init__(self):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()
        self.is_capturing = False
        self.screenshot = None
        self.selected_area = None
        
        # Setup window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        # Make fullscreen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setCursor(Qt.CursorShape.CrossCursor)
        
    def start_capture(self):
        """Start screen capture mode"""
        # Capture full screen using PyQt6 method
        screen = QApplication.primaryScreen()
        
        # Get the window ID of the root window (desktop)
        # In Windows, 0 represents the entire screen
        self.screenshot = screen.grabWindow(0)
        
        # Reset state
        self.begin = QPoint()
        self.end = QPoint()
        self.is_capturing = False
        self.selected_area = None
        
        # Show overlay fullscreen
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        
        # Force update
        self.update()
        
    def paintEvent(self, event):
        """Draw selection rectangle"""
        painter = QPainter(self)
        
        # Draw semi-transparent dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # If capturing, draw selection rectangle
        if self.is_capturing:
            rect = QRect(self.begin, self.end).normalized()
            
            # Clear the selected area (make it fully transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            
            # Draw border around selection
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.PenStyle.SolidLine))
            painter.drawRect(rect)
            
    def mousePressEvent(self, event):
        """Start selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.is_capturing = True
            self.update()
            
    def mouseMoveEvent(self, event):
        """Update selection"""
        if self.is_capturing:
            self.end = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Complete selection and capture area"""
        if event.button() == Qt.MouseButton.LeftButton and self.is_capturing:
            self.is_capturing = False
            self.end = event.pos()
            
            # Get selected rectangle
            rect = QRect(self.begin, self.end).normalized()
            
            if rect.width() > 10 and rect.height() > 10:
                # Get device pixel ratio for DPI scaling
                # On Windows with display scaling (125%, 150%, etc.),
                # mouse coordinates are in logical pixels but the screenshot
                # is in physical pixels, so we need to scale the rectangle
                screen = QApplication.primaryScreen()
                dpr = screen.devicePixelRatio()
                
                # Scale rectangle coordinates to match screenshot pixel coordinates
                scaled_rect = QRect(
                    int(rect.x() * dpr),
                    int(rect.y() * dpr),
                    int(rect.width() * dpr),
                    int(rect.height() * dpr)
                )
                
                # Crop screenshot to selected area using scaled coordinates
                self.selected_area = self.screenshot.copy(scaled_rect)
                
            self.hide()
            
    def keyPressEvent(self, event):
        """Cancel selection on ESC"""
        if event.key() == Qt.Key.Key_Escape:
            self.is_capturing = False
            self.selected_area = None
            self.hide()
            
    def get_selected_image(self):
        """Convert selected area to PIL Image"""
        if self.selected_area is None:
            return None
            
        # Convert QPixmap to QImage
        qimage = self.selected_area.toImage()
        
        # Use QBuffer for Qt I/O
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        qimage.save(buffer, "PNG")
        
        # Get data from QBuffer
        image_data = buffer.data().data()
        buffer.close()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        return image
