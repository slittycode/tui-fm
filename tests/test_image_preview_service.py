"""Tests for image preview service functionality."""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from image_preview_service import ImagePreviewService, RenderMode


class TestImagePreviewService:
    """Test cases for ImagePreviewService class."""
    
    def test_service_initialization(self) -> None:
        """Test ImagePreviewService initialization."""
        service = ImagePreviewService()
        
        assert service.max_width == 80
        assert service.max_height == 24
        assert service.render_mode == RenderMode.ASCII
        assert len(service.ascii_chars) == 10
        assert len(service.block_chars) == 5
        assert len(service.ansi_colors) == 8
    
    def test_service_custom_initialization(self) -> None:
        """Test ImagePreviewService initialization with custom parameters."""
        service = ImagePreviewService(max_width=120, max_height=30)
        
        assert service.max_width == 120
        assert service.max_height == 30
    
    def test_set_render_mode(self) -> None:
        """Test setting render mode."""
        service = ImagePreviewService()
        
        service.set_render_mode(RenderMode.ANSI)
        assert service.render_mode == RenderMode.ANSI
        
        service.set_render_mode(RenderMode.BLOCK)
        assert service.render_mode == RenderMode.BLOCK
    
    @patch('image_preview_service.Image')
    def test_can_render_image_no_pil(self, mock_image: Mock) -> None:
        """Test image rendering capability when PIL is not available."""
        with patch('image_preview_service.Image', None):
            service = ImagePreviewService()
            
            test_file = Path("test.jpg")
            assert not service.can_render_image(test_file)
    
    def test_can_render_image_supported_formats(self) -> None:
        """Test image rendering capability for supported formats."""
        service = ImagePreviewService()
        
        supported_formats = [
            "test.jpg", "test.jpeg", "test.png", "test.gif", 
            "test.bmp", "test.tiff", "test.webp"
        ]
        
        for filename in supported_formats:
            test_file = Path(filename)
            # Mock file size using patch on Path.stat
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024  # Small file
                assert service.can_render_image(test_file)
    
    def test_can_render_image_unsupported_formats(self) -> None:
        """Test image rendering capability for unsupported formats."""
        service = ImagePreviewService()
        
        unsupported_formats = [
            "test.txt", "test.doc", "test.pdf", "test.mp3", "test.mp4"
        ]
        
        for filename in unsupported_formats:
            test_file = Path(filename)
            assert not service.can_render_image(test_file)
    
    def test_can_render_image_file_too_large(self) -> None:
        """Test image rendering capability for large files."""
        service = ImagePreviewService()
        
        test_file = Path("test.jpg")
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 15 * 1024 * 1024  # 15MB
            assert not service.can_render_image(test_file)
    
    def test_can_render_image_file_error(self) -> None:
        """Test image rendering capability when file access fails."""
        service = ImagePreviewService()
        
        test_file = Path("test.jpg")
        with patch('pathlib.Path.stat', side_effect=OSError("Permission denied")):
            assert not service.can_render_image(test_file)
    
    @patch('image_preview_service.Image')
    def test_render_image_success(self, mock_image: Mock) -> None:
        """Test successful image rendering."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.size = (100, 50)
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        mock_image.open.return_value.__enter__.return_value = mock_img
        
        service = ImagePreviewService()
        test_file = Path("test.jpg")
        
        # Mock can_render_image to return True
        with patch.object(service, 'can_render_image', return_value=True):
            with patch.object(service, '_render_ascii', return_value="ascii art"):
                result = service.render_image(test_file)
                assert result == "ascii art"
    
    @patch('image_preview_service.Image')
    def test_render_image_failure(self, mock_image: Mock) -> None:
        """Test image rendering failure."""
        mock_image.open.side_effect = Exception("Cannot open image")
        
        service = ImagePreviewService()
        test_file = Path("test.jpg")
        
        # Mock can_render_image to return True
        with patch.object(service, 'can_render_image', return_value=True):
            result = service.render_image(test_file)
            assert result is None
    
    def test_render_image_cannot_render(self) -> None:
        """Test rendering when image cannot be rendered."""
        service = ImagePreviewService()
        test_file = Path("test.txt")
        
        result = service.render_image(test_file)
        assert result is None
    
    @patch('image_preview_service.Image')
    def test_resize_image(self, mock_image: Mock) -> None:
        """Test image resizing."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (200, 100)
        mock_img.mode = 'RGB'
        
        service = ImagePreviewService(max_width=80, max_height=24)
        
        result = service._resize_image(mock_img)
        
        # Should call resize with calculated dimensions
        mock_img.resize.assert_called_once()
        resize_args = mock_img.resize.call_args[0]
        assert isinstance(resize_args[0], tuple)
        assert len(resize_args[0]) == 2
        assert resize_args[0][0] <= 80
        assert resize_args[0][1] <= 24
    
    @patch('image_preview_service.Image')
    def test_render_ascii(self, mock_image_class: Mock) -> None:
        """Test ASCII rendering."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.configure_mock(size=(4, 3))
        mock_gray_img = Mock()
        mock_img.convert.return_value = mock_gray_img
        mock_gray_img.configure_mock(size=(4, 3))
        mock_gray_img.getdata.return_value = [0, 128, 255, 128, 0, 255, 128, 255, 0, 128, 255, 0]
        
        service = ImagePreviewService()
        
        result = service._render_ascii(mock_img)
        
        assert isinstance(result, str)
        assert len(result.split('\n')) == 3  # 3 lines for height 3
        assert all(len(line) == 4 for line in result.split('\n'))  # 4 chars for width 4
    
    @patch('image_preview_service.Image')
    def test_render_ansi(self, mock_image: Mock) -> None:
        """Test ANSI rendering."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.configure_mock(size=(2, 2))
        mock_gray_img = Mock()
        mock_img.convert.return_value = mock_gray_img
        mock_gray_img.configure_mock(size=(2, 2))
        mock_gray_img.getdata.return_value = [0, 255, 128, 255]
        
        service = ImagePreviewService()
        
        result = service._render_ansi(mock_img)
        
        assert isinstance(result, str)
        assert '\033[' in result  # Should contain ANSI codes
        assert len(result.split('\n')) == 2  # 2 lines for height 2
    
    @patch('image_preview_service.Image')
    def test_render_block(self, mock_image: Mock) -> None:
        """Test block rendering."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.configure_mock(size=(3, 2))
        mock_gray_img = Mock()
        mock_img.convert.return_value = mock_gray_img
        mock_gray_img.configure_mock(size=(3, 2))
        mock_gray_img.getdata.return_value = [0, 128, 255, 64, 192, 255]
        
        service = ImagePreviewService()
        
        result = service._render_block(mock_img)
        
        assert isinstance(result, str)
        assert len(result.split('\n')) == 2  # 2 lines for height 2
        assert all(len(line) == 3 for line in result.split('\n'))  # 3 chars for width 3
    
    @patch('image_preview_service.Image')
    def test_get_image_info(self, mock_image: Mock) -> None:
        """Test getting image information."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.configure_mock(
            format='JPEG',
            mode='RGB',
            size=(800, 600),
            width=800,
            height=600,
            info={}
        )
        mock_image.open.return_value.__enter__.return_value = mock_img
        
        service = ImagePreviewService()
        test_file = Path("test.jpg")
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024
            with patch.object(service, 'can_render_image', return_value=True):
                result = service.get_image_info(test_file)
                
                assert result is not None
                assert result["format"] == 'JPEG'
                assert result["mode"] == 'RGB'
                assert result["size"] == (800, 600)
                assert result["width"] == 800
                assert result["height"] == 600
                assert result["file_size"] == 1024
                assert result["has_transparency"] is False
    
    def test_get_image_info_no_pil(self) -> None:
        """Test getting image info when PIL is not available."""
        with patch('image_preview_service.Image', None):
            service = ImagePreviewService()
            test_file = Path("test.jpg")
            
            result = service.get_image_info(test_file)
            assert result is None
    
    def test_get_image_info_cannot_render(self) -> None:
        """Test getting image info for non-renderable file."""
        service = ImagePreviewService()
        test_file = Path("test.txt")
        
        result = service.get_image_info(test_file)
        assert result is None
    
    @patch('image_preview_service.ImageEnhance')
    @patch('image_preview_service.Image')
    def test_enhance_contrast(self, mock_image_class: Mock, mock_enhance: Mock) -> None:
        """Test contrast enhancement."""
        # Mock PIL Image and Enhancer
        mock_img = Mock()
        mock_enhancer = Mock()
        mock_enhance.enhance.return_value = mock_img
        mock_enhance.Contrast.return_value = mock_enhancer
        
        service = ImagePreviewService()
        
        result = service.enhance_contrast(mock_img, 2.0)
        
        mock_enhance.Contrast.assert_called_once_with(mock_img)
        mock_enhancer.enhance.assert_called_once_with(2.0)
        # The result should be the enhanced image, not the original
        assert result is not None
    
    def test_enhance_contrast_no_enhance(self) -> None:
        """Test contrast enhancement when ImageEnhance is not available."""
        with patch('image_preview_service.ImageEnhance', None):
            service = ImagePreviewService()
            mock_img = Mock()
            
            result = service.enhance_contrast(mock_img)
            assert result == mock_img
    
    def test_detect_render_mode_truecolor(self) -> None:
        """Test render mode detection for truecolor terminals."""
        service = ImagePreviewService()
        
        with patch.dict(os.environ, {'COLORTERM': 'truecolor'}):
            mode = service.detect_render_mode()
            assert mode == RenderMode.ANSI
        
        with patch.dict(os.environ, {'COLORTERM': '24bit'}):
            mode = service.detect_render_mode()
            assert mode == RenderMode.ANSI
    
    def test_detect_render_mode_256color(self) -> None:
        """Test render mode detection for 256-color terminals."""
        service = ImagePreviewService()
        
        with patch.dict(os.environ, {'TERM': 'xterm-256color'}):
            mode = service.detect_render_mode()
            assert mode == RenderMode.ANSI
        
        with patch.dict(os.environ, {'TERM': 'screen-256color'}):
            mode = service.detect_render_mode()
            assert mode == RenderMode.ANSI
    
    def test_detect_render_mode_basic(self) -> None:
        """Test render mode detection for basic terminals."""
        service = ImagePreviewService()
        
        with patch.dict(os.environ, {'TERM': 'vt100'}, clear=True):
            mode = service.detect_render_mode()
            assert mode == RenderMode.ASCII
    
    def test_auto_configure(self) -> None:
        """Test auto-configuration based on terminal capabilities."""
        service = ImagePreviewService()
        
        # Mock terminal size detection
        with patch('shutil.get_terminal_size') as mock_size:
            mock_size.return_value.columns = 100
            mock_size.return_value.lines = 30
            
            # Mock render mode detection
            with patch.object(service, 'detect_render_mode', return_value=RenderMode.ANSI):
                service.auto_configure()
                
                assert service.max_width == 96  # 100 - 4 padding
                assert service.max_height == 22  # 30 - 8 padding
                assert service.render_mode == RenderMode.ANSI
    
    def test_auto_configure_fallback(self) -> None:
        """Test auto-configuration fallback when detection fails."""
        service = ImagePreviewService()
        
        # Mock terminal size detection failure
        with patch('shutil.get_terminal_size', side_effect=Exception("Detection failed")):
            # Mock render mode detection
            with patch.object(service, 'detect_render_mode', return_value=RenderMode.ASCII):
                service.auto_configure()
                
                assert service.max_width == 76  # Default
                assert service.max_height == 16  # Default
                assert service.render_mode == RenderMode.ASCII
    
    def test_repr(self) -> None:
        """Test string representation."""
        service = ImagePreviewService(max_width=120, max_height=30)
        service.set_render_mode(RenderMode.ANSI)
        
        repr_str = repr(service)
        assert "ImagePreviewService" in repr_str
        assert "ansi" in repr_str
        assert "120x30" in repr_str
    
    def test_render_mode_enum(self) -> None:
        """Test RenderMode enum values."""
        assert RenderMode.ASCII.value == "ascii"
        assert RenderMode.ANSI.value == "ansi"
        assert RenderMode.BLOCK.value == "block"
    
    @patch('image_preview_service.Image')
    def test_render_image_different_modes(self, mock_image_class: Mock) -> None:
        """Test image rendering with different modes."""
        # Mock PIL Image
        mock_img = Mock()
        mock_img.mode = 'RGB'
        mock_img.size = (10, 5)
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        mock_image_class.open.return_value.__enter__.return_value = mock_img
        
        service = ImagePreviewService()
        test_file = Path("test.jpg")
        
        with patch.object(service, 'can_render_image', return_value=True):
            # Test ASCII mode
            service.set_render_mode(RenderMode.ASCII)
            with patch.object(service, '_render_ascii', return_value="ascii"):
                result = service.render_image(test_file)
                assert result == "ascii"
            
            # Test ANSI mode
            service.set_render_mode(RenderMode.ANSI)
            with patch.object(service, '_render_ansi', return_value="ansi"):
                result = service.render_image(test_file)
                assert result == "ansi"
            
            # Test BLOCK mode
            service.set_render_mode(RenderMode.BLOCK)
            with patch.object(service, '_render_block', return_value="block"):
                result = service.render_image(test_file)
                assert result == "block"
