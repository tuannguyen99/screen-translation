# Japanese Screen Translator

A Windows desktop app that captures text from any area of your screen using OCR and translates it to English. **Optimized for Japanese text** - perfect for reading manga, newspapers, websites, and games.

![Screenshot](https://img.shields.io/badge/Platform-Windows-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green)

## ✨ Features

- **📷 Screen Capture**: Select any area on your screen to capture text
- **🔍 Multiple OCR Engines**:
  - **Windows OCR** - Best for UI text, documents, newspapers
  - **Manga OCR** - Optimized for manga speech bubbles
  - **Tesseract** - Fallback for other languages
- **🌐 Translation**: Google Translate or Ollama (offline)
- **⌨️ Keyboard Shortcut**: `Ctrl+Shift+C` for quick capture
- **🎨 Modern Dark UI**: Clean interface with image preview

## 📋 Requirements

- Windows 10/11
- Python 3.10+
- Japanese OCR Language Pack (see installation)

## 🚀 Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Windows Japanese OCR (Required)

Open **PowerShell as Administrator** and run:

```powershell
Add-WindowsCapability -Online -Name "Language.OCR~~~ja-JP~0.0.1.0"
```

### 3. (Optional) Install Tesseract OCR

For fallback OCR support:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install Japanese language packs: `jpn.traineddata`, `jpn_vert.traineddata`
- Save to: `C:\Program Files\Tesseract-OCR\tessdata`

### 4. (Optional) Install Ollama for Offline Translation

- Download from: https://ollama.ai
- Pull a model: `ollama pull gemma`

## 📖 Usage

### Quick Start

```bash
python main.py
```

1. Click **📷 Start Capture** (or press `Ctrl+Shift+C`)
2. Drag to select a screen area with Japanese text
3. Wait for OCR and translation
4. View results - original Japanese + English translation
5. Click **📋 Copy** to copy text

### Settings

Access the **Settings** tab to configure:

| Setting | Description |
|---------|-------------|
| OCR Engine | `auto` (recommended), `windows`, `manga`, or `tesseract` |
| Target Language | English, Spanish, Chinese, etc. |
| Translation Backend | `google` (online) or `ollama` (offline) |

### OCR Engine Guide

| Engine | Best For | Notes |
|--------|----------|-------|
| **Windows OCR** | Websites, documents, newspapers, UI | Requires Japanese language pack |
| **Manga OCR** | Manga speech bubbles, stylized fonts | ~400MB model download on first use |
| **Tesseract** | General fallback | Requires separate installation |

## 🎯 Tips for Best Results

1. **Capture one text block at a time** for best accuracy
2. **Use Windows OCR** for standard fonts (websites, documents)
3. **Use Manga OCR** only for actual manga with stylized text
4. **High contrast text** works better than low contrast
5. For very small text, capture a larger area

## 🔧 Troubleshooting

### "Windows OCR: Language.OCR~~~ja-JP not found"

Install the Japanese OCR language pack (requires admin):
```powershell
Add-WindowsCapability -Online -Name "Language.OCR~~~ja-JP~0.0.1.0"
```

### First Manga OCR is slow

The Manga OCR model (~400MB) downloads on first use. Subsequent uses are instant.

### DPI Scaling Issues

The app automatically handles Windows display scaling (125%, 150%, etc.).

## 📁 Project Structure

```
screen-translation/
├── main.py              # Main application with UI
├── ocr_engine.py        # OCR engines (Windows/Manga/Tesseract)
├── translation_engine.py # Translation (Google/Ollama)
├── screen_capture.py    # Screen capture with DPI scaling
├── settings_ui.py       # Settings panel
├── config_manager.py    # Configuration management
└── requirements.txt     # Python dependencies
```

## 📄 License

MIT
