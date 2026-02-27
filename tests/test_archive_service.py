"""Tests for archive service functionality."""
import tempfile
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from archive_service import (
    ArchiveService,
    ArchiveType,
    ArchiveEntry,
    ArchiveInfo
)


class TestArchiveService:
    """Test cases for ArchiveService class."""
    
    def test_service_initialization(self) -> None:
        """Test ArchiveService initialization."""
        service = ArchiveService()
        
        assert service.temp_dir.exists()
        assert service.temp_dir.name == "tui_fm_archives"
        
        # Test with custom temp directory
        custom_temp = Path("/tmp/custom_archive_temp")
        service_custom = ArchiveService(temp_dir=custom_temp)
        assert service_custom.temp_dir == custom_temp
    
    def test_is_archive(self) -> None:
        """Test archive detection."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test supported archive types
            for ext in ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz']:
                archive_file = temp_path / f"test{ext}"
                archive_file.write_text("fake archive content")
                assert service.is_archive(archive_file) is True
            
            # Test unsupported file
            text_file = temp_path / "test.txt"
            text_file.write_text("not an archive")
            assert service.is_archive(text_file) is False
            
            # Test directory
            assert service.is_archive(temp_path) is False
            
            # Test nonexistent file
            assert service.is_archive(Path("/nonexistent/archive.zip")) is False
    
    def test_get_archive_type(self) -> None:
        """Test archive type detection."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test different archive types
            test_cases = [
                ("test.zip", ArchiveType.ZIP),
                ("test.tar", ArchiveType.TAR),
                ("test.tar.gz", ArchiveType.TAR_GZ),
                ("test.tgz", ArchiveType.TAR_GZ),
                ("test.tar.bz2", ArchiveType.TAR_BZ2),
                ("test.tar.xz", ArchiveType.TAR_XZ),
            ]
            
            for filename, expected_type in test_cases:
                archive_file = temp_path / filename
                archive_file.write_text("fake archive content")
                
                detected_type = service.get_archive_type(archive_file)
                assert detected_type == expected_type
            
            # Test unsupported file
            text_file = temp_path / "test.txt"
            text_file.write_text("not an archive")
            assert service.get_archive_type(text_file) is None
    
    def test_list_zip_contents(self) -> None:
        """Test listing ZIP archive contents."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            
            # Create a test ZIP file
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("file1.txt", "Hello World")
                zip_file.writestr("dir/file2.txt", "Hello Directory")
                zip_file.writestr("file3.py", "print('Hello')")
            
            # List contents
            info = service.list_archive_contents(zip_path)
            
            assert isinstance(info, ArchiveInfo)
            assert info.path == zip_path
            assert info.type == ArchiveType.ZIP
            assert info.total_entries == 3
            assert info.total_size > 0
            assert len(info.entries) == 3
            
            # Check entries
            entry_names = [entry.name for entry in info.entries]
            assert "file1.txt" in entry_names
            assert "dir/file2.txt" in entry_names
            assert "file3.py" in entry_names
    
    def test_list_tar_contents(self) -> None:
        """Test listing TAR archive contents."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tar_path = temp_path / "test.tar"
            
            # Create test files
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.txt"
            file1.write_text("Hello World")
            file2.write_text("Hello Tar")
            
            # Create TAR archive
            with tarfile.open(tar_path, 'w') as tar_file:
                tar_file.add(file1)
                tar_file.add(file2)
            
            # List contents
            info = service.list_archive_contents(tar_path)
            
            assert isinstance(info, ArchiveInfo)
            assert info.path == tar_path
            assert info.type == ArchiveType.TAR
            assert info.total_entries == 2
            assert info.total_size > 0
            assert len(info.entries) == 2
    
    def test_list_tar_gz_contents(self) -> None:
        """Test listing TAR.GZ archive contents."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tar_path = temp_path / "test.tar.gz"
            
            # Create test files
            file1 = temp_path / "file1.txt"
            file1.write_text("Hello World")
            
            # Create TAR.GZ archive
            with tarfile.open(tar_path, 'w:gz') as tar_file:
                tar_file.add(file1)
            
            # List contents
            info = service.list_archive_contents(tar_path)
            
            assert info.type == ArchiveType.TAR_GZ
            assert info.total_entries == 1
            assert len(info.entries) == 1
    
    def test_list_unsupported_archive(self) -> None:
        """Test listing unsupported archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_archive = temp_path / "fake.archive"
            fake_archive.write_text("not a real archive")
            
            with pytest.raises(ValueError, match="Unsupported archive"):
                service.list_archive_contents(fake_archive)
    
    def test_extract_file_from_zip(self) -> None:
        """Test extracting a file from ZIP archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            extract_to = temp_path / "extract"
            
            # Create ZIP with test file
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("test.txt", "Extracted Content")
            
            # Extract file
            extracted_path = service.extract_file(zip_path, "test.txt", extract_to)
            
            assert extracted_path.exists()
            assert extracted_path.read_text() == "Extracted Content"
    
    def test_extract_file_from_tar(self) -> None:
        """Test extracting a file from TAR archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tar_path = temp_path / "test.tar"
            extract_to = temp_path / "extract"
            
            # Create TAR with test file
            test_file = temp_path / "test.txt"
            test_file.write_text("Extracted Content")
            
            with tarfile.open(tar_path, 'w') as tar_file:
                tar_file.add(test_file, arcname="test.txt")
            
            # Extract file
            extracted_path = service.extract_file(tar_path, "test.txt", extract_to)
            
            assert extracted_path.exists()
            assert extracted_path.read_text() == "Extracted Content"
    
    def test_extract_nonexistent_file(self) -> None:
        """Test extracting nonexistent file from archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            extract_to = temp_path / "extract"
            
            # Create empty ZIP
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                pass
            
            with pytest.raises(ValueError, match="File not found in archive"):
                service.extract_file(zip_path, "nonexistent.txt", extract_to)
    
    def test_extract_all_from_zip(self) -> None:
        """Test extracting all files from ZIP archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            extract_to = temp_path / "extract"
            
            # Create ZIP with multiple files
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("file1.txt", "Content 1")
                zip_file.writestr("file2.txt", "Content 2")
                zip_file.writestr("subdir/file3.txt", "Content 3")
            
            # Extract all files
            extracted_files = service.extract_all(zip_path, extract_to)
            
            assert len(extracted_files) == 3
            assert (extract_to / "file1.txt").exists()
            assert (extract_to / "file2.txt").exists()
            assert (extract_to / "subdir" / "file3.txt").exists()
    
    def test_extract_all_from_tar(self) -> None:
        """Test extracting all files from TAR archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tar_path = temp_path / "test.tar"
            extract_to = temp_path / "extract"
            
            # Create TAR with multiple files
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.txt"
            subdir = temp_path / "subdir"
            subdir.mkdir()
            file3 = subdir / "file3.txt"
            
            file1.write_text("Content 1")
            file2.write_text("Content 2")
            file3.write_text("Content 3")
            
            with tarfile.open(tar_path, 'w') as tar_file:
                tar_file.add(file1, arcname="file1.txt")
                tar_file.add(file2, arcname="file2.txt")
                tar_file.add(subdir, arcname="subdir", recursive=True)
            
            # Extract all files
            extracted_files = service.extract_all(tar_path, extract_to)
            
            assert len(extracted_files) >= 3
            assert (extract_to / "file1.txt").exists()
            assert (extract_to / "file2.txt").exists()
            assert (extract_to / "subdir" / "file3.txt").exists()
    
    def test_create_zip_archive(self) -> None:
        """Test creating a ZIP archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            file1 = temp_path / "file1.txt"
            file2 = temp_path / "file2.txt"
            file1.write_text("Content 1")
            file2.write_text("Content 2")
            
            archive_path = temp_path / "created.zip"
            
            # Create archive
            created_path = service.create_archive([file1, file2], archive_path, ArchiveType.ZIP)
            
            assert created_path == archive_path
            assert archive_path.exists()
            
            # Verify contents
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                assert "file1.txt" in zip_file.namelist()
                assert "file2.txt" in zip_file.namelist()
                assert zip_file.read("file1.txt").decode() == "Content 1"
    
    def test_create_tar_archive(self) -> None:
        """Test creating a TAR archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_path / "test.txt"
            test_file.write_text("Test Content")
            
            archive_path = temp_path / "created.tar"
            
            # Create archive
            created_path = service.create_archive([test_file], archive_path, ArchiveType.TAR)
            
            assert created_path == archive_path
            assert archive_path.exists()
            
            # Verify contents
            with tarfile.open(archive_path, 'r') as tar_file:
                member = tar_file.getmember("test.txt")
                assert member.name == "test.txt"
                assert member.size > 0
    
    def test_create_tar_gz_archive(self) -> None:
        """Test creating a TAR.GZ archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            test_file = temp_path / "test.txt"
            test_file.write_text("Test Content")
            
            archive_path = temp_path / "created.tar.gz"
            
            # Create archive
            created_path = service.create_archive([test_file], archive_path, ArchiveType.TAR_GZ)
            
            assert created_path == archive_path
            assert archive_path.exists()
            
            # Verify it's a valid gzip archive
            with tarfile.open(archive_path, 'r:gz') as tar_file:
                member = tar_file.getmember("test.txt")
                assert member.name == "test.txt"
    
    def test_preview_file(self) -> None:
        """Test previewing a file from archive."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            
            # Create ZIP with test file
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("preview.txt", "Preview Content")
            
            # Preview file
            content = service.preview_file(zip_path, "preview.txt")
            
            assert content == "Preview Content"
    
    def test_preview_binary_file(self) -> None:
        """Test previewing binary file returns None."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            
            # Create ZIP with binary content
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("binary.bin", b'\x00\x01\x02\x03')
            
            # Preview binary file
            content = service.preview_file(zip_path, "binary.bin")
            
            assert content is None
    
    def test_preview_large_file(self) -> None:
        """Test previewing large file returns None."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            
            # Create ZIP with large content (2MB)
            large_content = "x" * (2 * 1024 * 1024)
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("large.txt", large_content)
            
            # Preview large file
            content = service.preview_file(zip_path, "large.txt", max_size=1024 * 1024)  # 1MB limit
            
            assert content is None
    
    def test_cleanup_temp_files(self) -> None:
        """Test cleaning up temporary files."""
        service = ArchiveService()
        
        # Create some temp files
        temp_file = service.temp_dir / "test.txt"
        temp_file.write_text("test")
        
        assert temp_file.exists()
        
        # Cleanup
        service.cleanup_temp_files()
        
        # Temp directory should still exist but be empty
        assert service.temp_dir.exists()
        assert not temp_file.exists()
    
    def test_get_archive_stats(self) -> None:
        """Test getting archive statistics."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"
            
            # Create ZIP with test files
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                zip_file.writestr("file1.txt", "Content 1")
                zip_file.writestr("file2.txt", "Content 2")
            
            # Get stats
            stats = service.get_archive_stats(zip_path)
            
            assert stats["type"] == "zip"
            assert stats["total_entries"] == 2
            assert stats["file_count"] == 2
            assert stats["dir_count"] == 0
            assert stats["total_size"] > 0
            assert stats["compressed_size"] > 0
            assert "compression_ratio" in stats
            assert "size_reduction" in stats
    
    def test_get_archive_stats_unsupported(self) -> None:
        """Test getting stats for unsupported file."""
        service = ArchiveService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            text_file = temp_path / "test.txt"
            text_file.write_text("not an archive")
            
            stats = service.get_archive_stats(text_file)
            
            assert stats == {}
    
    def test_archive_entry_dataclass(self) -> None:
        """Test ArchiveEntry dataclass."""
        entry = ArchiveEntry(
            name="test.txt",
            path="test.txt",
            size=1024,
            is_dir=False,
            is_file=True,
            mtime=1234567890.0,
            comment="Test comment"
        )
        
        assert entry.name == "test.txt"
        assert entry.path == "test.txt"
        assert entry.size == 1024
        assert entry.is_dir is False
        assert entry.is_file is True
        assert entry.mtime == 1234567890.0
        assert entry.comment == "Test comment"
    
    def test_archive_info_dataclass(self) -> None:
        """Test ArchiveInfo dataclass."""
        path = Path("/test/archive.zip")
        entries = [
            ArchiveEntry("test.txt", "test.txt", 1024, False, True),
            ArchiveEntry("dir", "dir", 0, True, False)
        ]
        
        info = ArchiveInfo(
            path=path,
            type=ArchiveType.ZIP,
            total_entries=2,
            total_size=1024,
            compressed_size=512,
            entries=entries
        )
        
        assert info.path == path
        assert info.type == ArchiveType.ZIP
        assert info.total_entries == 2
        assert info.total_size == 1024
        assert info.compressed_size == 512
        assert len(info.entries) == 2
    
    @patch('zipfile.ZipFile')
    def test_list_zip_contents_error(self, mock_zipfile: Mock) -> None:
        """Test handling ZIP read errors."""
        service = ArchiveService()
        
        mock_zipfile.side_effect = zipfile.BadZipFile("Invalid ZIP")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "bad.zip"
            zip_path.write_text("not a zip")
            
            with pytest.raises(ValueError, match="Failed to read ZIP archive"):
                service.list_archive_contents(zip_path)
    
    @patch('tarfile.open')
    def test_list_tar_contents_error(self, mock_tarfile: Mock) -> None:
        """Test handling TAR read errors."""
        service = ArchiveService()
        
        mock_tarfile.side_effect = tarfile.TarError("Invalid TAR")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            tar_path = Path(temp_dir) / "bad.tar"
            tar_path.write_text("not a tar")
            
            with pytest.raises(ValueError, match="Failed to read TAR archive"):
                service.list_archive_contents(tar_path)
