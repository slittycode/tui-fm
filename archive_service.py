"""Archive browsing and extraction service."""
import os
import tarfile
import zipfile
from pathlib import Path
from typing import List, Dict, Optional, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
import tempfile
import shutil
import time
import datetime


class ArchiveType(Enum):
    """Supported archive types."""
    ZIP = "zip"
    TAR = "tar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"


@dataclass
class ArchiveEntry:
    """Represents an entry in an archive."""
    name: str
    path: str  # Full path within archive
    size: int
    is_dir: bool
    is_file: bool
    mtime: Optional[float] = None
    comment: Optional[str] = None


@dataclass
class ArchiveInfo:
    """Information about an archive."""
    path: Path
    type: ArchiveType
    total_entries: int
    total_size: int
    compressed_size: int
    entries: List[ArchiveEntry]


class ArchiveService:
    """Service for browsing and extracting archives."""
    
    SUPPORTED_EXTENSIONS = {
        '.zip': ArchiveType.ZIP,
        '.tar': ArchiveType.TAR,
        '.tgz': ArchiveType.TAR_GZ,
        '.tar.gz': ArchiveType.TAR_GZ,
        '.tbz2': ArchiveType.TAR_BZ2,
        '.tar.bz2': ArchiveType.TAR_BZ2,
        '.txz': ArchiveType.TAR_XZ,
        '.tar.xz': ArchiveType.TAR_XZ,
    }
    
    def __init__(self, temp_dir: Optional[Path] = None) -> None:
        """Initialize archive service.
        
        Args:
            temp_dir: Temporary directory for extractions.
        """
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "tui_fm_archives"
        self.temp_dir.mkdir(exist_ok=True)
        
    def is_archive(self, path: Path) -> bool:
        """Check if a file is a supported archive.
        
        Args:
            path: File path to check.
            
        Returns:
            True if file is a supported archive, False otherwise.
        """
        if not path.is_file():
            return False
        
        suffix = path.suffix.lower()
        if suffix in self.SUPPORTED_EXTENSIONS:
            return True
            
        # Check for compound extensions
        name_lower = path.name.lower()
        for ext in ['.tar.gz', '.tar.bz2', '.tar.xz']:
            if name_lower.endswith(ext):
                return True
                
        return False
    
    def get_archive_type(self, path: Path) -> Optional[ArchiveType]:
        """Get the archive type for a file.
        
        Args:
            path: File path to check.
            
        Returns:
            ArchiveType if supported, None otherwise.
        """
        if not self.is_archive(path):
            return None
        
        name_lower = path.name.lower()
        
        # Check compound extensions first
        for ext, archive_type in self.SUPPORTED_EXTENSIONS.items():
            if name_lower.endswith(ext):
                return archive_type
                
        return None
    
    def list_archive_contents(self, archive_path: Path) -> ArchiveInfo:
        """List contents of an archive.
        
        Args:
            archive_path: Path to the archive file.
            
        Returns:
            ArchiveInfo with archive contents.
        """
        if not self.is_archive(archive_path):
            raise ValueError(f"Unsupported archive: {archive_path}")
        
        archive_type = self.get_archive_type(archive_path)
        if archive_type is None:
            raise ValueError(f"Cannot determine archive type: {archive_path}")
        
        if archive_type == ArchiveType.ZIP:
            return self._list_zip_contents(archive_path)
        else:
            return self._list_tar_contents(archive_path, archive_type)
    
    def _list_zip_contents(self, zip_path: Path) -> ArchiveInfo:
        """List contents of a ZIP archive.
        
        Args:
            zip_path: Path to the ZIP file.
            
        Returns:
            ArchiveInfo with ZIP contents.
        """
        entries = []
        total_size = 0
        compressed_size = zip_path.stat().st_size
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                for info in zip_file.infolist():
                    # Skip directory entries that end with /
                    is_dir = info.is_dir()
                    is_file = not is_dir
                    
                    # Convert date_time tuple to timestamp
                    mtime = None
                    if info.date_time:
                        try:
                            dt = datetime.datetime(*info.date_time)
                            mtime = dt.timestamp()
                        except (ValueError, TypeError):
                            mtime = None
                    
                    entry = ArchiveEntry(
                        name=info.filename,
                        path=info.filename,
                        size=info.file_size,
                        is_dir=is_dir,
                        is_file=is_file,
                        mtime=mtime,
                        comment=info.comment.decode('utf-8', errors='ignore') if info.comment else None
                    )
                    entries.append(entry)
                    total_size += info.file_size
                    
        except (zipfile.BadZipFile, OSError) as e:
            raise ValueError(f"Failed to read ZIP archive: {e}")
        
        return ArchiveInfo(
            path=zip_path,
            type=ArchiveType.ZIP,
            total_entries=len(entries),
            total_size=total_size,
            compressed_size=compressed_size,
            entries=entries
        )
    
    def _list_tar_contents(self, tar_path: Path, archive_type: ArchiveType) -> ArchiveInfo:
        """List contents of a TAR archive.
        
        Args:
            tar_path: Path to the TAR file.
            archive_type: Type of TAR archive.
            
        Returns:
            ArchiveInfo with TAR contents.
        """
        entries = []
        total_size = 0
        compressed_size = tar_path.stat().st_size
        
        # Determine the mode based on archive type
        mode_map = {
            ArchiveType.TAR: 'r',
            ArchiveType.TAR_GZ: 'r:gz',
            ArchiveType.TAR_BZ2: 'r:bz2',
            ArchiveType.TAR_XZ: 'r:xz',
        }
        
        mode = mode_map.get(archive_type, 'r')
        
        try:
            with tarfile.open(tar_path, mode) as tar_file:
                for member in tar_file.getmembers():
                    is_dir = member.isdir()
                    is_file = member.isfile()
                    
                    entry = ArchiveEntry(
                        name=member.name,
                        path=member.name,
                        size=member.size,
                        is_dir=is_dir,
                        is_file=is_file,
                        mtime=member.mtime,
                        comment=None
                    )
                    entries.append(entry)
                    total_size += member.size
                    
        except (tarfile.TarError, OSError) as e:
            raise ValueError(f"Failed to read TAR archive: {e}")
        
        return ArchiveInfo(
            path=tar_path,
            type=archive_type,
            total_entries=len(entries),
            total_size=total_size,
            compressed_size=compressed_size,
            entries=entries
        )
    
    def extract_file(self, archive_path: Path, file_path: str, extract_to: Path) -> Path:
        """Extract a single file from an archive.
        
        Args:
            archive_path: Path to the archive file.
            file_path: Path of the file within the archive.
            extract_to: Directory to extract to.
            
        Returns:
            Path to the extracted file.
        """
        if not self.is_archive(archive_path):
            raise ValueError(f"Unsupported archive: {archive_path}")
        
        extract_to.mkdir(parents=True, exist_ok=True)
        archive_type = self.get_archive_type(archive_path)
        
        if archive_type == ArchiveType.ZIP:
            return self._extract_from_zip(archive_path, file_path, extract_to)
        else:
            return self._extract_from_tar(archive_path, file_path, extract_to, archive_type)
    
    def _extract_from_zip(self, zip_path: Path, file_path: str, extract_to: Path) -> Path:
        """Extract a file from a ZIP archive.
        
        Args:
            zip_path: Path to the ZIP file.
            file_path: Path of the file within the ZIP.
            extract_to: Directory to extract to.
            
        Returns:
            Path to the extracted file.
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Ensure the file exists in the archive
                if file_path not in zip_file.namelist():
                    raise ValueError(f"File not found in archive: {file_path}")
                
                # Extract the file
                zip_file.extract(file_path, extract_to)
                
                extracted_path = extract_to / file_path
                if not extracted_path.exists():
                    raise ValueError(f"Failed to extract file: {file_path}")
                
                return extracted_path
                
        except (zipfile.BadZipFile, OSError) as e:
            raise ValueError(f"Failed to extract from ZIP: {e}")
    
    def _extract_from_tar(self, tar_path: Path, file_path: str, extract_to: Path, archive_type: ArchiveType) -> Path:
        """Extract a file from a TAR archive.
        
        Args:
            tar_path: Path to the TAR file.
            file_path: Path of the file within the TAR.
            extract_to: Directory to extract to.
            archive_type: Type of TAR archive.
            
        Returns:
            Path to the extracted file.
        """
        mode_map = {
            ArchiveType.TAR: 'r',
            ArchiveType.TAR_GZ: 'r:gz',
            ArchiveType.TAR_BZ2: 'r:bz2',
            ArchiveType.TAR_XZ: 'r:xz',
        }
        
        mode = mode_map.get(archive_type, 'r')
        
        try:
            with tarfile.open(tar_path, mode) as tar_file:
                try:
                    member = tar_file.getmember(file_path)
                except KeyError:
                    raise ValueError(f"File not found in archive: {file_path}")
                
                # Extract the file
                tar_file.extract(member, extract_to)
                
                extracted_path = extract_to / file_path
                if not extracted_path.exists():
                    raise ValueError(f"Failed to extract file: {file_path}")
                
                return extracted_path
                
        except (tarfile.TarError, OSError) as e:
            raise ValueError(f"Failed to extract from TAR: {e}")
    
    def extract_all(self, archive_path: Path, extract_to: Path) -> List[Path]:
        """Extract all files from an archive.
        
        Args:
            archive_path: Path to the archive file.
            extract_to: Directory to extract to.
            
        Returns:
            List of extracted file paths.
        """
        if not self.is_archive(archive_path):
            raise ValueError(f"Unsupported archive: {archive_path}")
        
        extract_to.mkdir(parents=True, exist_ok=True)
        archive_type = self.get_archive_type(archive_path)
        
        if archive_type == ArchiveType.ZIP:
            return self._extract_all_from_zip(archive_path, extract_to)
        else:
            return self._extract_all_from_tar(archive_path, extract_to, archive_type)
    
    def _extract_all_from_zip(self, zip_path: Path, extract_to: Path) -> List[Path]:
        """Extract all files from a ZIP archive.
        
        Args:
            zip_path: Path to the ZIP file.
            extract_to: Directory to extract to.
            
        Returns:
            List of extracted file paths.
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_to)
                
                # Collect all extracted files
                for root, dirs, files in os.walk(extract_to):
                    for file in files:
                        file_path = Path(root) / file
                        extracted_files.append(file_path)
                        
        except (zipfile.BadZipFile, OSError) as e:
            raise ValueError(f"Failed to extract from ZIP: {e}")
        
        return extracted_files
    
    def _extract_all_from_tar(self, tar_path: Path, extract_to: Path, archive_type: ArchiveType) -> List[Path]:
        """Extract all files from a TAR archive.
        
        Args:
            tar_path: Path to the TAR file.
            extract_to: Directory to extract to.
            archive_type: Type of TAR archive.
            
        Returns:
            List of extracted file paths.
        """
        extracted_files = []
        mode_map = {
            ArchiveType.TAR: 'r',
            ArchiveType.TAR_GZ: 'r:gz',
            ArchiveType.TAR_BZ2: 'r:bz2',
            ArchiveType.TAR_XZ: 'r:xz',
        }
        
        mode = mode_map.get(archive_type, 'r')
        
        try:
            with tarfile.open(tar_path, mode) as tar_file:
                tar_file.extractall(extract_to)
                
                # Collect all extracted files
                for root, dirs, files in os.walk(extract_to):
                    for file in files:
                        file_path = Path(root) / file
                        extracted_files.append(file_path)
                        
        except (tarfile.TarError, OSError) as e:
            raise ValueError(f"Failed to extract from TAR: {e}")
        
        return extracted_files
    
    def create_archive(self, source_paths: List[Path], archive_path: Path, archive_type: ArchiveType) -> Path:
        """Create an archive from files and directories.
        
        Args:
            source_paths: List of files and directories to archive.
            archive_path: Path for the new archive file.
            archive_type: Type of archive to create.
            
        Returns:
            Path to the created archive.
        """
        # Ensure parent directory exists
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        if archive_type == ArchiveType.ZIP:
            return self._create_zip_archive(source_paths, archive_path)
        else:
            return self._create_tar_archive(source_paths, archive_path, archive_type)
    
    def _create_zip_archive(self, source_paths: List[Path], archive_path: Path) -> Path:
        """Create a ZIP archive.
        
        Args:
            source_paths: List of files and directories to archive.
            archive_path: Path for the new ZIP file.
            
        Returns:
            Path to the created ZIP file.
        """
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for source_path in source_paths:
                    if source_path.is_file():
                        # Add single file
                        zip_file.write(source_path, source_path.name)
                    elif source_path.is_dir():
                        # Add directory recursively
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = Path(root) / file
                                arc_name = file_path.relative_to(source_path.parent)
                                zip_file.write(file_path, arc_name)
                                
        except (zipfile.BadZipFile, OSError) as e:
            raise ValueError(f"Failed to create ZIP archive: {e}")
        
        return archive_path
    
    def _create_tar_archive(self, source_paths: List[Path], archive_path: Path, archive_type: ArchiveType) -> Path:
        """Create a TAR archive.
        
        Args:
            source_paths: List of files and directories to archive.
            archive_path: Path for the new TAR file.
            archive_type: Type of TAR archive to create.
            
        Returns:
            Path to the created TAR file.
        """
        mode_map = {
            ArchiveType.TAR: 'w',
            ArchiveType.TAR_GZ: 'w:gz',
            ArchiveType.TAR_BZ2: 'w:bz2',
            ArchiveType.TAR_XZ: 'w:xz',
        }
        
        mode = mode_map.get(archive_type, 'w')
        
        try:
            with tarfile.open(archive_path, mode) as tar_file:
                for source_path in source_paths:
                    if source_path.is_file():
                        # Add single file
                        tar_file.add(source_path, arcname=source_path.name)
                    elif source_path.is_dir():
                        # Add directory recursively
                        tar_file.add(source_path, arcname=source_path.name, recursive=True)
                        
        except (tarfile.TarError, OSError) as e:
            raise ValueError(f"Failed to create TAR archive: {e}")
        
        return archive_path
    
    def preview_file(self, archive_path: Path, file_path: str, max_size: int = 1024 * 1024) -> Optional[str]:
        """Preview a file from an archive without extracting.
        
        Args:
            archive_path: Path to the archive file.
            file_path: Path of the file within the archive.
            max_size: Maximum size to preview (1MB default).
            
        Returns:
            File content as string, or None if too large or binary.
        """
        if not self.is_archive(archive_path):
            return None
        
        # Extract to temporary location
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                extracted_path = self.extract_file(archive_path, file_path, temp_path)
                
                # Check file size
                if extracted_path.stat().st_size > max_size:
                    return None
                
                # Try to read as text
                try:
                    # Check if it's binary by reading a small chunk first
                    with extracted_path.open('rb') as f:
                        chunk = f.read(1024)
                        if b'\x00' in chunk:  # Null bytes indicate binary
                            return None
                    
                    return extracted_path.read_text(encoding='utf-8', errors='ignore')
                except (UnicodeDecodeError, OSError):
                    return None  # Binary file or read error
                    
            except ValueError:
                return None
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary extraction files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
        except OSError:
            pass  # Ignore cleanup errors
    
    def get_archive_stats(self, archive_path: Path) -> Dict[str, Union[int, float, str]]:
        """Get statistics about an archive.
        
        Args:
            archive_path: Path to the archive file.
            
        Returns:
            Dictionary with archive statistics.
        """
        if not self.is_archive(archive_path):
            return {}
        
        try:
            info = self.list_archive_contents(archive_path)
            
            file_count = sum(1 for entry in info.entries if entry.is_file)
            dir_count = sum(1 for entry in info.entries if entry.is_dir)
            
            compression_ratio = (info.compressed_size / info.total_size) if info.total_size > 0 else 1.0
            
            return {
                "type": info.type.value,
                "total_entries": info.total_entries,
                "file_count": file_count,
                "dir_count": dir_count,
                "total_size": info.total_size,
                "compressed_size": info.compressed_size,
                "compression_ratio": compression_ratio,
                "size_reduction": (1.0 - compression_ratio) * 100 if compression_ratio < 1.0 else 0.0
            }
            
        except ValueError:
            return {}
