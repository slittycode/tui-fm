"""Image preview service for terminal graphics rendering."""
import io
import os
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image, ImageEnhance
except ImportError:
    Image = None
    ImageEnhance = None


class RenderMode(Enum):
    """Image rendering modes for different terminal capabilities."""
    ASCII = "ascii"
    ANSI = "ansi"
    BLOCK = "block"


class ImagePreviewService:
    """Service for rendering images in terminal environments."""
    
    def __init__(self, max_width: int = 80, max_height: int = 24) -> None:
        """Initialize the image preview service.
        
        Args:
            max_width: Maximum width for rendered output.
            max_height: Maximum height for rendered output.
        """
        self.max_width = max_width
        self.max_height = max_height
        self.render_mode = RenderMode.ASCII
        
        # ASCII characters for different brightness levels
        self.ascii_chars = " .:-=+*#%@"
        
        # Block characters for better rendering
        self.block_chars = " ░▒▓█"
        
        # ANSI color codes for colored rendering
        self.ansi_colors = [
            "\033[38;5;232m",  # Black
            "\033[38;5;233m",  # Dark gray
            "\033[38;5;234m",  # Light gray
            "\033[38;5;235m",  # Medium gray
            "\033[38;5;236m",  # Lighter gray
            "\033[38;5;237m",  # Even lighter gray
            "\033[38;5;238m",  # Almost white
            "\033[38;5;255m",  # White
        ]
    
    def set_render_mode(self, mode: RenderMode) -> None:
        """Set the rendering mode.
        
        Args:
            mode: The rendering mode to use.
        """
        self.render_mode = mode
    
    def can_render_image(self, file_path: Path) -> bool:
        """Check if an image can be rendered.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            True if the image can be rendered, False otherwise.
        """
        if Image is None:
            return False
        
        # Check file extension
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        if file_path.suffix.lower() not in supported_extensions:
            return False
        
        # Check file size (limit to 10MB for performance)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except OSError:
            return False
        
        return True
    
    def render_image(self, file_path: Path) -> Optional[str]:
        """Render an image to terminal-compatible text.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            Rendered image as string, or None if rendering failed.
        """
        if not self.can_render_image(file_path):
            return None
        
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to fit terminal
                img = self._resize_image(img)
                
                # Render based on mode
                if self.render_mode == RenderMode.ASCII:
                    return self._render_ascii(img)
                elif self.render_mode == RenderMode.ANSI:
                    return self._render_ansi(img)
                elif self.render_mode == RenderMode.BLOCK:
                    return self._render_block(img)
                else:
                    return self._render_ascii(img)
                    
        except Exception:
            return None
    
    def _resize_image(self, img: 'Image.Image') -> 'Image.Image':
        """Resize image to fit terminal dimensions.
        
        Args:
            img: PIL Image to resize.
            
        Returns:
            Resized PIL Image.
        """
        # Calculate aspect ratio
        original_width, original_height = img.size
        aspect_ratio = original_width / original_height
        
        # Calculate new dimensions
        new_width = min(self.max_width, original_width)
        new_height = int(new_width / aspect_ratio)
        
        # Ensure height fits
        if new_height > self.max_height:
            new_height = self.max_height
            new_width = int(new_height * aspect_ratio)
        
        # Resize with high quality
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _render_ascii(self, img: 'Image.Image') -> str:
        """Render image using ASCII characters.
        
        Args:
            img: PIL Image to render.
            
        Returns:
            ASCII art representation.
        """
        # Convert to grayscale
        gray_img = img.convert('L')
        
        # Get pixel data
        pixels = list(gray_img.getdata())
        width, height = gray_img.size
        
        # Build ASCII art
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = pixels[y * width + x]
                # Map pixel value to ASCII character
                char_index = int(pixel_value * (len(self.ascii_chars) - 1) / 255)
                line += self.ascii_chars[char_index]
            lines.append(line)
        
        return "\n".join(lines)
    
    def _render_ansi(self, img: 'Image.Image') -> str:
        """Render image using ANSI color codes.
        
        Args:
            img: PIL Image to render.
            
        Returns:
            ANSI-colored representation.
        """
        # Convert to grayscale
        gray_img = img.convert('L')
        
        # Get pixel data
        pixels = list(gray_img.getdata())
        width, height = gray_img.size
        
        # Build ANSI art
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = pixels[y * width + x]
                # Map pixel value to ANSI color
                color_index = int(pixel_value * (len(self.ansi_colors) - 1) / 255)
                line += self.ansi_colors[color_index] + "█"
            line += "\033[0m"  # Reset color
            lines.append(line)
        
        return "\n".join(lines)
    
    def _render_block(self, img: 'Image.Image') -> str:
        """Render image using block characters.
        
        Args:
            img: PIL Image to render.
            
        Returns:
            Block character representation.
        """
        # Convert to grayscale
        gray_img = img.convert('L')
        
        # Get pixel data
        pixels = list(gray_img.getdata())
        width, height = gray_img.size
        
        # Build block art
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel_value = pixels[y * width + x]
                # Map pixel value to block character
                char_index = int(pixel_value * (len(self.block_chars) - 1) / 255)
                line += self.block_chars[char_index]
            lines.append(line)
        
        return "\n".join(lines)
    
    def get_image_info(self, file_path: Path) -> Optional[dict]:
        """Get information about an image file.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            Dictionary with image information, or None if not an image.
        """
        if Image is None or not self.can_render_image(file_path):
            return None
        
        try:
            with Image.open(file_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "file_size": file_path.stat().st_size,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                }
        except Exception:
            return None
    
    def enhance_contrast(self, img: 'Image.Image', factor: float = 1.5) -> 'Image.Image':
        """Enhance image contrast for better rendering.
        
        Args:
            img: PIL Image to enhance.
            factor: Contrast enhancement factor.
            
        Returns:
            Enhanced PIL Image.
        """
        if ImageEnhance is None:
            return img
        
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def detect_render_mode(self) -> RenderMode:
        """Detect the best render mode for the current terminal.
        
        Returns:
            Recommended render mode.
        """
        # Check for common terminal capabilities
        term = os.environ.get('TERM', '').lower()
        colorterm = os.environ.get('COLORTERM', '').lower()
        
        # Check for truecolor support
        if colorterm in ('truecolor', '24bit'):
            return RenderMode.ANSI
        
        # Check for modern terminals
        if any(term_var in term for term_var in ('xterm-256color', 'screen-256color', 'tmux-256color')):
            return RenderMode.ANSI
        
        # Default to ASCII for maximum compatibility
        return RenderMode.ASCII
    
    def auto_configure(self) -> None:
        """Auto-configure the service based on terminal capabilities."""
        # Detect terminal size
        try:
            import shutil
            terminal_size = shutil.get_terminal_size()
            self.max_width = terminal_size.columns - 4  # Leave some padding
            self.max_height = terminal_size.lines - 8   # Leave room for UI
        except Exception:
            # Use defaults if detection fails
            self.max_width = 76
            self.max_height = 16
        
        # Detect render mode
        self.render_mode = self.detect_render_mode()
    
    def __repr__(self) -> str:
        return f"ImagePreviewService(mode={self.render_mode.value}, size={self.max_width}x{self.max_height})"
