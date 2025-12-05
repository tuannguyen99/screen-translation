"""
Test script to verify Manga OCR is working correctly
"""
import sys
from PIL import Image
from ocr_engine import OCREngine

def test_manga_ocr():
    """Test Manga OCR with a sample image or clipboard"""
    print("=" * 50)
    print("Manga OCR Test")
    print("=" * 50)
    
    # Initialize OCR engine
    print("\n1. Initializing Manga OCR (this may take a moment on first run)...")
    ocr = OCREngine(engine='manga')
    
    # Check if available
    if not ocr.is_manga_ocr_available():
        print("ERROR: Manga OCR is not installed!")
        print("Run: pip install manga-ocr")
        return False
    
    # Test with clipboard if available
    try:
        from PIL import ImageGrab
        print("\n2. Attempting to get image from clipboard...")
        img = ImageGrab.grabclipboard()
        
        if img is None:
            print("   No image in clipboard.")
            print("   Copy a manga image to clipboard and run this script again.")
            print("\n   Or use: python test_ocr.py <image_path>")
            return False
        
        print(f"   Image found: {img.size} pixels")
        
    except Exception as e:
        print(f"   Clipboard error: {e}")
        return False
    
    # Run OCR
    print("\n3. Running Manga OCR...")
    result = ocr.extract_text(img)
    
    print("\n" + "=" * 50)
    print("OCR Result:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return True


def test_with_file(image_path):
    """Test with a specific image file"""
    print("=" * 50)
    print(f"Testing with: {image_path}")
    print("=" * 50)
    
    try:
        img = Image.open(image_path)
        print(f"Image size: {img.size}")
    except Exception as e:
        print(f"Error opening image: {e}")
        return False
    
    ocr = OCREngine(engine='manga')
    
    print("\nRunning Manga OCR...")
    result = ocr.extract_text(img)
    
    print("\n" + "=" * 50)
    print("OCR Result:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Test with provided image file
        test_with_file(sys.argv[1])
    else:
        # Test with clipboard
        test_manga_ocr()
