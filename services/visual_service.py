import os
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)

class VisualService:
    """
    Generates branded social media cards for AI news.
    """
    def __init__(self):
        self.width = 1080
        self.height = 1080
        self.bg_color = (15, 15, 15)  # Dark theme
        self.accent_color = (0, 87, 255)  # Brand Blue
        self.text_color = (255, 255, 255)
        self.secondary_text_color = (180, 180, 180)
        
        # Font paths - common Windows paths
        self.font_bold = self._find_font(["arialbd.ttf", "segoeuib.ttf", "Roboto-Bold.ttf"])
        self.font_regular = self._find_font(["arial.ttf", "segoeui.ttf", "Roboto-Regular.ttf"])

    def _find_font(self, font_names: list) -> str:
        """Attempts to find a system font from a list of possibilities."""
        search_paths = [
            "C:\\Windows\\Fonts\\",
            "/usr/share/fonts/truetype/",
            "/usr/share/fonts/truetype/dejavu/",
            "/usr/share/fonts/truetype/liberation/",
            "assets/fonts/"
        ]
        # Common Linux font alternatives
        linux_alternatives = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Ubuntu-B.ttf"]
        
        for path in search_paths:
            if not os.path.exists(path): continue
            for name in font_names + linux_alternatives:
                full_path = os.path.join(path, name)
                if os.path.exists(full_path):
                    return full_path
        return None 

    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wraps text to fit within a specified width."""
        lines = []
        words = text.split()
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            # Get length of the test line
            w = font.getlength(test_line)
            if w <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def generate_news_card(self, headline: str, brand_name: str = "AI News Daily") -> str:
        """
        Creates a high-impact square news card with dynamic font scaling.
        """
        import random
        
        THEMES = [
            {"bg": (10, 10, 15), "accent": (0, 120, 255), "glow": (0, 50, 150), "name": "Cyber Blue"},
            {"bg": (15, 10, 20), "accent": (160, 60, 255), "glow": (70, 30, 120), "name": "Neon Purple"},
            {"bg": (10, 18, 15), "accent": (0, 220, 140), "glow": (0, 100, 60), "name": "Matrix Green"},
            {"bg": (20, 15, 10), "accent": (255, 110, 0), "glow": (140, 50, 0), "name": "Amber Tech"}
        ]
        
        theme = random.choice(THEMES)
        bg_color = theme["bg"]
        accent_color = theme["accent"]
        glow_color = theme["glow"]

        try:
            # Create base image
            img = Image.new('RGB', (self.width, self.height), color=bg_color)
            draw = ImageDraw.Draw(img)

            # --- Background Glow ---
            glow = Image.new('RGB', (self.width, self.height), (0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_draw.ellipse([self.width//4, -self.height//4, self.width*1.2, self.height//1.8], fill=glow_color)
            glow = glow.filter(ImageFilter.GaussianBlur(radius=150))
            img = Image.blend(img, glow, 0.5)
            draw = ImageDraw.Draw(img)

            margin = 80
            
            # --- Dynamic Font Selection ---
            font_size = 90 if len(headline) < 60 else 70
            if len(headline) > 100: font_size = 55
            
            try:
                headline_font = ImageFont.truetype(self.font_bold, font_size) if self.font_bold else ImageFont.load_default()
            except:
                headline_font = ImageFont.load_default()

            # Wrap text
            max_text_width = self.width - (margin * 2)
            wrapped_lines = self._wrap_text(headline.upper(), headline_font, max_text_width)
            
            # Center vertically
            line_spacing = 20
            # Get height per line (fallback for default font)
            h = font_size if self.font_bold else 20
            total_height = len(wrapped_lines) * (h + line_spacing)
            y_start = (self.height // 2) - (total_height // 2)

            # --- Header Tag ---
            try:
                tag_font = ImageFont.truetype(self.font_bold, 30) if self.font_bold else ImageFont.load_default()
            except: tag_font = ImageFont.load_default()
            draw.text((margin, margin), "⚡ LATEST AI NEWS", font=tag_font, fill=accent_color)

            # --- Headline ---
            for i, line in enumerate(wrapped_lines):
                y = y_start + i * (h + line_spacing)
                # Drop shadow
                draw.text((margin + 3, y + 3), line, font=headline_font, fill=(0, 0, 0))
                draw.text((margin, y), line, font=headline_font, fill=(255, 255, 255))

            # --- Footer ---
            try:
                footer_font = ImageFont.truetype(self.font_regular, 36) if self.font_regular else ImageFont.load_default()
            except: footer_font = ImageFont.load_default()
            
            draw.rectangle([margin, self.height - margin - 80, margin + 150, self.height - margin - 72], fill=accent_color)
            draw.text((margin, self.height - margin - 55), brand_name.upper(), font=footer_font, fill=(180, 180, 180))

            # --- Save ---
            os.makedirs(config.MEDIA_DIR, exist_ok=True)
            filename = f"news_card_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join(config.MEDIA_DIR, filename)
            img.save(file_path, quality=95)
            
            logger.info(f"VisualService: Premium card generated at {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"VisualService: Error generating news card - {e}")
            return None
    def is_square(self, image_path: str, tolerance: float = 0.05) -> bool:
        """
        Checks if an image is roughly square (1:1 aspect ratio).
        """
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            ratio = width / height
            return (1.0 - tolerance) <= ratio <= (1.0 + tolerance)
        except Exception as e:
            logger.error(f"VisualService: Failed to check image ratio: {e}")
            return False

    def square_image(self, image_path: str, output_path: str = None) -> str:
        """
        Takes an image of any aspect ratio and places it on a 1:1 (square) 
        white canvas. This ensures Instagram compatibility.
        """
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            width, height = img.size
            new_size = max(width, height)
            
            # Create white background
            new_img = Image.new("RGB", (new_size, new_size), (255, 255, 255))
            offset = ((new_size - width) // 2, (new_size - height) // 2)
            new_img.paste(img, offset)
            
            final_path = output_path or image_path.replace(".", "_squared.")
            new_img.save(final_path, quality=95)
            logger.info(f"VisualService: Squared image saved to {final_path}")
            return final_path
        except Exception as e:
            logger.error(f"VisualService: Failed to square image: {e}")
            return image_path
