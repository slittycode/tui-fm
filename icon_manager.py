"""Icon management system for file type icons using Nerd Fonts."""
import subprocess
from pathlib import Path
from typing import Dict, Optional

from rich.text import Text


class IconManager:
    """Manage file type icons using Nerd Fonts."""
    
    # Comprehensive file type icon mappings
    ICON_MAPPINGS: Dict[str, str] = {
        # Programming Languages
        '.py': '🐍',
        '.pyw': '🐍',
        '.pyi': '🐍',
        '.js': '📜',
        '.jsx': '📜',
        '.ts': '📘',
        '.tsx': '📘',
        '.java': '☕',
        '.class': '☕',
        '.jar': '☕',
        '.cpp': '⚙️',
        '.cxx': '⚙️',
        '.cc': '⚙️',
        '.c': '⚙️',
        '.h': '⚙️',
        '.hpp': '⚙️',
        '.rs': '🦀',
        '.go': '🐹',
        '.php': '🐘',
        '.rb': '💎',
        '.swift': '🍎',
        '.kt': '🎯',
        '.scala': '🔷',
        '.cs': '🔷',
        '.vb': '🔷',
        '.dart': '🎯',
        '.lua': '🌙',
        '.r': '📊',
        '.m': '🍎',
        '.sh': '📜',
        '.bash': '📜',
        '.zsh': '📜',
        '.fish': '🐠',
        '.ps1': '📜',
        '.bat': '📜',
        '.cmd': '📜',
        '.sql': '🗃️',
        '.pl': '🐪',
        '.pm': '🐪',
        '.tcl': '🐪',
        '.tk': '🐪',
        
        # Web Technologies
        '.html': '🌐',
        '.htm': '🌐',
        '.css': '🎨',
        '.scss': '🎨',
        '.sass': '🎨',
        '.less': '🎨',
        '.vue': '💚',
        '.svelte': '🔥',
        
        # Configuration Files
        '.json': '📋',
        '.yaml': '📄',
        '.yml': '📄',
        '.toml': '📝',
        '.ini': '⚙️',
        '.cfg': '⚙️',
        '.conf': '⚙️',
        '.xml': '📰',
        '.xaml': '📰',
        '.plist': '📰',
        '.env': '🔐',
        '.dockerfile': '🐳',
        'dockerfile': '🐳',
        '.gitignore': '📝',
        '.gitattributes': '📝',
        '.gitmodules': '📝',
        
        # Documents
        '.pdf': '📕',
        '.doc': '📘',
        '.docx': '📘',
        '.odt': '📘',
        '.rtf': '📘',
        '.txt': '📄',
        '.md': '📝',
        '.markdown': '📝',
        '.rst': '📝',
        '.tex': '📜',
        '.latex': '📜',
        
        # Spreadsheets
        '.xls': '📗',
        '.xlsx': '📗',
        '.ods': '📗',
        '.csv': '📊',
        
        # Presentations
        '.ppt': '📙',
        '.pptx': '📙',
        '.odp': '📙',
        
        # Images
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.gif': '🖼️',
        '.bmp': '🖼️',
        '.tiff': '🖼️',
        '.tif': '🖼️',
        '.webp': '🖼️',
        '.svg': '🎨',
        '.ico': '🖼️',
        '.psd': '🎨',
        '.ai': '🎨',
        '.eps': '🎨',
        
        # Audio Files
        '.mp3': '🎵',
        '.wav': '🎵',
        '.flac': '🎵',
        '.aac': '🎵',
        '.ogg': '🎵',
        '.wma': '🎵',
        '.m4a': '🎵',
        '.opus': '🎵',
        
        # Video Files
        '.mp4': '🎬',
        '.avi': '🎬',
        '.mkv': '🎬',
        '.mov': '🎬',
        '.wmv': '🎬',
        '.flv': '🎬',
        '.webm': '🎬',
        '.m4v': '🎬',
        '.3gp': '🎬',
        
        # Archives
        '.zip': '📦',
        '.tar': '📦',
        '.gz': '📦',
        '.tgz': '📦',
        '.bz2': '📦',
        '.tbz2': '📦',
        '.xz': '📦',
        '.txz': '📦',
        '.7z': '📦',
        '.rar': '📦',
        '.deb': '📦',
        '.rpm': '📦',
        '.dmg': '📦',
        '.pkg': '📦',
        '.msi': '📦',
        '.iso': '💿',
        
        # System Files
        '.exe': '⚙️',
        '.msi': '⚙️',
        '.dll': '🔧',
        '.so': '🔧',
        '.dylib': '🔧',
        '.a': '🔧',
        '.lib': '🔧',
        '.obj': '🔧',
        '.o': '🔧',
        
        # Development Files
        '.lock': '🔒',
        '.log': '📋',
        '.tmp': '📄',
        '.temp': '📄',
        '.bak': '📄',
        '.backup': '📄',
        '.old': '📄',
        '.orig': '📄',
        '.swp': '📄',
        '.swo': '📄',
        
        # Certificate Files
        '.pem': '🔐',
        '.crt': '🔐',
        '.key': '🔑',
        '.p12': '🔐',
        '.pfx': '🔐',
        
        # Database Files
        '.db': '🗃️',
        '.sqlite': '🗃️',
        '.sqlite3': '🗃️',
        '.mdb': '🗃️',
        
        # Font Files
        '.ttf': '🔤',
        '.otf': '🔤',
        '.woff': '🔤',
        '.woff2': '🔤',
        '.eot': '🔤',
        
        # E-book Files
        '.epub': '📚',
        '.mobi': '📚',
        '.azw': '📚',
        '.azw3': '📚',
        
        # Virtual Machine Files
        '.vmdk': '💻',
        '.vdi': '💻',
        '.vhd': '💻',
        '.ova': '💻',
        '.ovf': '💻',
        
        # Network Files
        '.pcap': '🌐',
        '.cap': '🌐',
        
        # 3D Files
        '.obj': '🎮',
        '.stl': '🎮',
        '.ply': '🎮',
        '.blend': '🎮',
        
        # Other Files
        '.torrent': '🔽',
        '.key': '🔑',
        '.pages': '📄',
        '.numbers': '📊',
        '.notebook': '📓',
    }
    
    # Directory icons
    DIRECTORY_ICONS = {
        'default': '📁',
        'git': '📂',
        'node_modules': '📦',
        '.git': '📂',
        '.vscode': '📝',
        '.idea': '📝',
        'venv': '🐍',
        'env': '🐍',
        '.venv': '🐍',
        '__pycache__': '🐍',
        'target': '🎯',
        'build': '🔨',
        'dist': '📦',
        'cmake-build': '🔨',
        'src': '📂',
        'lib': '📚',
        'docs': '📚',
        'test': '🧪',
        'tests': '🧪',
        'spec': '🧪',
        'config': '⚙️',
        'configs': '⚙️',
        'scripts': '📜',
        'bin': '⚙️',
        'sbin': '⚙️',
        'etc': '⚙️',
        'usr': '📂',
        'var': '📂',
        'opt': '📂',
        'tmp': '📄',
        'home': '🏠',
        'desktop': '🖥️',
        'documents': '📚',
        'downloads': '📥',
        'music': '🎵',
        'videos': '🎬',
        'pictures': '🖼️',
        'photos': '🖼️',
        'public': '🌐',
        'templates': '📋',
        '.local': '📂',
        '.config': '⚙️',
        '.cache': '📄',
    }
    
    def __init__(self) -> None:
        """Initialize the icon manager."""
        self.nerd_font_available = self._check_nerd_font()
        self.icon_cache: Dict[str, str] = {}
        self.fallback_enabled = True
    
    def _check_nerd_font(self) -> bool:
        """Check if Nerd Fonts are available on the system."""
        try:
            # Try to find Nerd Fonts in system font directories
            font_dirs = [
                Path.home() / "Library" / "Fonts",
                Path("/usr/local/share/fonts"),
                Path("/usr/share/fonts"),
                Path.home() / ".local" / "share" / "fonts",
                Path.home() / ".fonts",
            ]
            
            for font_dir in font_dirs:
                if font_dir.exists():
                    for font_file in font_dir.rglob("*Nerd*"):
                        if font_file.suffix.lower() in ['.ttf', '.otf']:
                            return True
            
            # Check if fc-list is available and can find Nerd Fonts
            try:
                result = subprocess.run(
                    ["fc-list", ":family=Nerd Font"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return False
        except Exception:
            return False
    
    def get_file_icon(self, file_path: Path) -> str:
        """Get icon for a file based on extension and type.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Icon character as string.
        """
        # Check cache first
        cache_key = str(file_path)
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        icon = self._get_file_icon_internal(file_path)
        
        # Cache the result
        self.icon_cache[cache_key] = icon
        
        return icon
    
    def _get_file_icon_internal(self, file_path: Path) -> str:
        """Internal method to get file icon without caching."""
        if not self.nerd_font_available and not self.fallback_enabled:
            return ""
        
        # Check if it's a hidden file
        if file_path.name.startswith('.'):
            if file_path.name in ['.git', '.gitignore', '.gitattributes', '.gitmodules']:
                return self.ICON_MAPPINGS.get('.git', '📝')
            elif file_path.name == '.env':
                return self.ICON_MAPPINGS.get('.env', '🔐')
            elif file_path.name in ['.venv', 'venv', 'env']:
                return '🐍'
            elif file_path.name in ['node_modules']:
                return '📦'
            elif file_path.name.startswith('.vscode') or file_path.name.startswith('.idea'):
                return '📝'
            else:
                return '👁️'  # Generic hidden file icon
        
        # Get file extension
        extension = file_path.suffix.lower()
        
        # Check exact extension match
        if extension in self.ICON_MAPPINGS:
            return self.ICON_MAPPINGS[extension]
        
        # Check special filename patterns
        filename_lower = file_path.name.lower()
        if filename_lower in ['dockerfile', 'makefile', 'readme', 'license', 'changelog']:
            if filename_lower == 'dockerfile':
                return '🐳'
            elif filename_lower == 'makefile':
                return '🔨'
            elif filename_lower in ['readme', 'license', 'changelog']:
                return '📄'
        
        # Check for common patterns
        if any(pattern in filename_lower for pattern in ['readme', 'license', 'changelog', 'install']):
            return '📄'
        
        # Default file icon
        return '📄'
    
    def get_directory_icon(self, dir_path: Path, is_git_repo: bool = False) -> str:
        """Get icon for a directory.
        
        Args:
            dir_path: Path to the directory.
            is_git_repo: Whether the directory is a Git repository.
            
        Returns:
            Icon character as string.
        """
        if not self.nerd_font_available and not self.fallback_enabled:
            return ""
        
        # Check cache first
        cache_key = f"dir:{str(dir_path)}:{is_git_repo}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        icon = self._get_directory_icon_internal(dir_path, is_git_repo)
        
        # Cache the result
        self.icon_cache[cache_key] = icon
        
        return icon
    
    def _get_directory_icon_internal(self, dir_path: Path, is_git_repo: bool) -> str:
        """Internal method to get directory icon without caching."""
        dirname = dir_path.name.lower()
        
        # Check for special directory names
        if dirname in self.DIRECTORY_ICONS:
            return self.DIRECTORY_ICONS[dirname]
        
        # Check for Git repository
        if is_git_repo or dirname == '.git':
            return '📂'
        
        # Check for common patterns
        if any(pattern in dirname for pattern in ['test', 'spec', 'tests']):
            return '🧪'
        elif any(pattern in dirname for pattern in ['doc', 'readme']):
            return '📚'
        elif any(pattern in dirname for pattern in ['src', 'source']):
            return '📂'
        elif any(pattern in dirname for pattern in ['config', 'conf']):
            return '⚙️'
        elif any(pattern in dirname for pattern in ['script', 'bin']):
            return '📜'
        elif any(pattern in dirname for pattern in ['build', 'dist', 'out']):
            return '📦'
        
        # Default directory icon
        return '📁'
    
    def get_icon_with_fallback(self, file_path: Path, default_icon: str = "📄") -> str:
        """Get icon with fallback for systems without Nerd Fonts.
        
        Args:
            file_path: Path to the file.
            default_icon: Default icon to use if Nerd Fonts are not available.
            
        Returns:
            Icon character as string.
        """
        if not self.nerd_font_available:
            return default_icon
        
        return self.get_file_icon(file_path)
    
    def get_directory_icon_with_fallback(self, dir_path: Path, is_git_repo: bool = False, default_icon: str = "📁") -> str:
        """Get directory icon with fallback for systems without Nerd Fonts.
        
        Args:
            dir_path: Path to the directory.
            is_git_repo: Whether the directory is a Git repository.
            default_icon: Default icon to use if Nerd Fonts are not available.
            
        Returns:
            Icon character as string.
        """
        if not self.nerd_font_available:
            return default_icon
        
        return self.get_directory_icon(dir_path, is_git_repo)
    
    def clear_cache(self) -> None:
        """Clear the icon cache."""
        self.icon_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        return {
            "cache_size": len(self.icon_cache),
            "nerd_font_available": self.nerd_font_available,
            "fallback_enabled": self.fallback_enabled,
        }
    
    def create_icon_text(self, icon: str, text: str, style: str = "") -> Text:
        """Create a Text object with icon and text.
        
        Args:
            icon: Icon character.
            text: Text to display.
            style: Rich text style.
            
        Returns:
            Text object with icon and text.
        """
        result = Text()
        
        if icon:
            result.append(f"{icon} ", style=style)
        
        result.append(text, style=style)
        
        return result
    
    def create_icon_text_string(self, icon: str, text: str, style: str = "") -> str:
        """Create a string with icon and text.
        
        Args:
            icon: Icon character.
            text: Text to display.
            style: Rich text style (ignored for string output).
            
        Returns:
            String with icon and text.
        """
        if icon:
            return f"{icon} {text}"
        return text
    
    def is_available(self) -> bool:
        """Check if icons are available.
        
        Returns:
            True if Nerd Fonts are available, False otherwise.
        """
        return self.nerd_font_available
    
    def enable_fallback(self, enabled: bool) -> None:
        """Enable or disable fallback icons.
        
        Args:
            enabled: Whether to enable fallback icons.
        """
        self.fallback_enabled = enabled
    
    def __repr__(self) -> str:
        return f"IconManager(nerd_font={self.nerd_font_available}, cache_size={len(self.icon_cache)})"
