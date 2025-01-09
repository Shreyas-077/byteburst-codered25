import PyPDF2
import io
from PIL import Image
import fitz  # PyMuPDF
import os
from typing import Dict, List, Optional, Tuple
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFEditor:
    def __init__(self):
        self.current_pdf = None
        self.edited_pages = {}
        self.annotations = {}
    
    def load_pdf(self, file_path: str) -> bool:
        """Load a PDF file for editing."""
        try:
            self.current_pdf = fitz.open(file_path)
            return True
        except Exception as e:
            print(f"Error loading PDF: {str(e)}")
            return False
    
    def get_page_count(self) -> int:
        """Get the total number of pages in the PDF."""
        if self.current_pdf:
            return len(self.current_pdf)
        return 0
    
    def get_page_text(self, page_num: int) -> str:
        """Get text content of a specific page."""
        if self.current_pdf and 0 <= page_num < len(self.current_pdf):
            return self.current_pdf[page_num].get_text()
        return ""
    
    def get_page_image(self, page_num: int) -> str:
        """Get page as an image in base64 format."""
        if not self.current_pdf or page_num >= len(self.current_pdf):
            return ""
        
        try:
            page = self.current_pdf[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            return base64.b64encode(img_data).decode()
        except Exception as e:
            print(f"Error converting page to image: {str(e)}")
            return ""
    
    def add_text(self, page_num: int, text: str, position: Tuple[float, float], 
                 font_size: int = 12, color: Tuple[float, float, float] = (0, 0, 0)) -> bool:
        """Add text to a specific position on a page."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                page = self.current_pdf[page_num]
                page.insert_text(
                    point=position,
                    text=text,
                    fontsize=font_size,
                    color=color
                )
                return True
        except Exception as e:
            print(f"Error adding text: {str(e)}")
        return False
    
    def add_highlight(self, page_num: int, rect: Tuple[float, float, float, float], 
                     color: Tuple[float, float, float] = (1, 1, 0)) -> bool:
        """Add a highlight to a specific area on a page."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                page = self.current_pdf[page_num]
                page.add_highlight_annot(rect)
                return True
        except Exception as e:
            print(f"Error adding highlight: {str(e)}")
        return False
    
    def add_image(self, page_num: int, image_path: str, position: Tuple[float, float], 
                 size: Tuple[float, float]) -> bool:
        """Add an image to a specific position on a page."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                page = self.current_pdf[page_num]
                img = open(image_path, "rb").read()
                page.insert_image(rect=(position[0], position[1], 
                                      position[0] + size[0], position[1] + size[1]), 
                                stream=img)
                return True
        except Exception as e:
            print(f"Error adding image: {str(e)}")
        return False
    
    def delete_page(self, page_num: int) -> bool:
        """Delete a specific page from the PDF."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                self.current_pdf.delete_page(page_num)
                return True
        except Exception as e:
            print(f"Error deleting page: {str(e)}")
        return False
    
    def rotate_page(self, page_num: int, angle: int) -> bool:
        """Rotate a specific page by the given angle."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                page = self.current_pdf[page_num]
                page.set_rotation(angle)
                return True
        except Exception as e:
            print(f"Error rotating page: {str(e)}")
        return False
    
    def add_annotation(self, page_num: int, text: str, position: Tuple[float, float], 
                      type: str = "text") -> bool:
        """Add an annotation to a specific position on a page."""
        try:
            if self.current_pdf and 0 <= page_num < len(self.current_pdf):
                page = self.current_pdf[page_num]
                if type == "text":
                    annot = page.add_text_annot(position, text)
                elif type == "sticky-note":
                    annot = page.add_sticky_note_annot(position, text)
                return True
        except Exception as e:
            print(f"Error adding annotation: {str(e)}")
        return False
    
    def save_pdf(self, output_path: str) -> bool:
        """Save the edited PDF to a file."""
        try:
            if self.current_pdf:
                self.current_pdf.save(output_path)
                return True
        except Exception as e:
            print(f"Error saving PDF: {str(e)}")
        return False
    
    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """Get the dimensions of a specific page."""
        if self.current_pdf and 0 <= page_num < len(self.current_pdf):
            page = self.current_pdf[page_num]
            return page.rect.width, page.rect.height
        return (0, 0)
    
    def extract_images(self, page_num: int) -> List[bytes]:
        """Extract all images from a specific page."""
        images = []
        if self.current_pdf and 0 <= page_num < len(self.current_pdf):
            page = self.current_pdf[page_num]
            image_list = page.get_images()
            for img in image_list:
                try:
                    xref = img[0]
                    base_image = self.current_pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    images.append(image_bytes)
                except Exception as e:
                    print(f"Error extracting image: {str(e)}")
        return images
    
    def close(self):
        """Close the PDF file."""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None
