"""Tests for enhanced Git service functionality."""
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

import pytest

from git_enhanced import (
    EnhancedGitService,
    GitCommit,
    GitBranch,
    GitStash,
    GitDiff,
    GitRepoStatus,
    GitRefType
)


class TestEnhancedGitService:
    """Test cases for EnhancedGitService class."""
    
    def test_service_initialization(self) -> None:
        """Test EnhancedGitService initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            assert service.path == temp_path
            assert service._commit_cache == {}
            assert service._branch_cache is None
    
    def test_get_current_branch(self) -> None:
        """Test getting current branch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="main\n"
                )
                
                branch = service.get_current_branch()
                assert branch == "main"
                mock_run.assert_called_once_with(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
    
    def test_get_current_branch_detached_head(self) -> None:
        """Test getting current branch when in detached HEAD state."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="HEAD\n"
                )
                
                branch = service.get_current_branch()
                assert branch is None
    
    def test_get_current_branch_not_git_repo(self) -> None:
        """Test getting current branch when not in a Git repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="fatal: not a git repository"
                )
                
                branch = service.get_current_branch()
                assert branch is None
    
    def test_get_branches(self) -> None:
        """Test getting branches."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = """* main 1234567890abcdef
  feature 0987654321fedcba
  develop abcdef1234567890"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                branches = service.get_branches(include_remote=False)
                
                assert len(branches) == 3
                assert branches[0].name == "main"
                assert branches[0].is_current is True
                assert branches[0].is_remote is False
                assert branches[0].last_commit == "1234567890abcdef"
                
                assert branches[1].name == "feature"
                assert branches[1].is_current is False
                assert branches[1].last_commit == "0987654321fedcba"
                
                assert branches[2].name == "develop"
                assert branches[2].is_current is False
                assert branches[2].last_commit == "abcdef1234567890"
    
    def test_get_branches_with_remotes(self) -> None:
        """Test getting branches including remotes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            local_output = """* main 1234567890abcdef
  feature 0987654321fedcba"""
            remote_output = """  origin/main 1234567890abcdef
  origin/feature 0987654321fedcba"""
            
            with patch('subprocess.run') as mock_run:
                def mock_subprocess(*args, **kwargs):
                    cmd = args[0]
                    if cmd == ["git", "branch", "-v", "--no-abbrev"]:
                        return Mock(returncode=0, stdout=local_output)
                    elif cmd == ["git", "branch", "-r", "-v", "--no-abbrev"]:
                        return Mock(returncode=0, stdout=remote_output)
                    else:
                        return Mock(returncode=0, stdout="")
                
                mock_run.side_effect = mock_subprocess
                
                branches = service.get_branches(include_remote=True)
                
                assert len(branches) == 4
                local_branches = [b for b in branches if not b.is_remote]
                remote_branches = [b for b in branches if b.is_remote]
                
                assert len(local_branches) == 2
                assert len(remote_branches) == 2
                assert all(b.is_remote for b in remote_branches)
    
    def test_switch_branch_success(self) -> None:
        """Test successful branch switching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Switched to branch 'feature'\n"
                )
                
                success, message = service.switch_branch("feature")
                
                assert success is True
                assert "Switched to branch 'feature'" in message
                mock_run.assert_called_once_with(
                    ["git", "checkout", "feature"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
    
    def test_switch_branch_failure(self) -> None:
        """Test failed branch switching."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stderr="error: pathspec 'feature' did not match any file(s) known to git"
                )
                
                success, message = service.switch_branch("feature")
                
                assert success is False
                assert "pathspec 'feature' did not match" in message
    
    def test_create_branch_success(self) -> None:
        """Test successful branch creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=""
                )
                
                success, message = service.create_branch("new-feature")
                
                assert success is True
                assert "Created branch 'new-feature'" in message
                mock_run.assert_called_once_with(
                    ["git", "branch", "new-feature"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
    
    def test_create_branch_from_base(self) -> None:
        """Test creating branch from a base branch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=""
                )
                
                success, message = service.create_branch("new-feature", "main")
                
                assert success is True
                mock_run.assert_called_once_with(
                    ["git", "branch", "new-feature", "main"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
    
    def test_get_commit_history(self) -> None:
        """Test getting commit history."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = """1234567890abcdef|12345678|John Doe|john@example.com|1640995200|Initial commit
 2 files changed, 50 insertions(+)
 create mode 100644 README.md
 create mode 100644 main.py

0987654321fedcba|09876543|Jane Smith|jane@example.com|1641081600|Add feature
 1 file changed, 10 insertions(+), 2 deletions(-)
"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                commits = service.get_commit_history(limit=2)
                
                assert len(commits) == 2
                
                # Check first commit
                commit1 = commits[0]
                assert commit1.hash == "1234567890abcdef"
                assert commit1.short_hash == "12345678"
                assert commit1.author == "John Doe"
                assert commit1.email == "john@example.com"
                assert commit1.date == datetime.fromtimestamp(1640995200)
                assert commit1.message == "Initial commit"
                assert commit1.files_changed == 2
                assert commit1.insertions == 50
                assert commit1.deletions == 0
                
                # Check second commit
                commit2 = commits[1]
                assert commit2.hash == "0987654321fedcba"
                assert commit2.author == "Jane Smith"
                assert commit2.message == "Add feature"
                assert commit2.files_changed == 1
                assert commit2.insertions == 10
                assert commit2.deletions == 2
    
    def test_get_diff(self) -> None:
        """Test getting diff information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            numstat_output = "5\t3\tsrc/main.py"
            diff_output = """--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,7 @@
 def hello():
-    print("Hello")
+    print("Hello World")
+    print("How are you?")
     return True
"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = [
                    Mock(returncode=0, stdout=numstat_output),  # numstat
                    Mock(returncode=0, stdout=diff_output),   # actual diff
                ]
                
                diffs = service.get_diff()
                
                assert len(diffs) == 1
                diff = diffs[0]
                assert diff.file_path == "src/main.py"
                assert diff.old_file == "src/main.py"
                assert diff.new_file == "src/main.py"
                assert diff.status == "M"
                assert diff.additions == 5
                assert diff.deletions == 3
                assert diff.content == diff_output
    
    def test_get_stashes(self) -> None:
        """Test getting stashes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = """stash@{0}: WIP on main: 1234567 Add new feature
stash@{1}: WIP on feature: 0987656 Work in progress
stash@{2}: On develop: abcdef12 Refactor code"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                stashes = service.get_stashes()
                
                assert len(stashes) == 3
                
                # Check first stash
                stash1 = stashes[0]
                assert stash1.index == "0"
                assert stash1.ref == "stash@{0}"
                assert stash1.message == "WIP on main: 1234567 Add new feature"
                assert stash1.branch == "main"
                
                # Check second stash
                stash2 = stashes[1]
                assert stash2.index == "1"
                assert stash2.branch == "feature"
                
                # Check third stash (different format)
                stash3 = stashes[2]
                assert stash3.index == "2"
                # This stash has "On develop" format
                assert stash3.branch == "develop"
    
    def test_create_stash(self) -> None:
        """Test creating a stash."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="Saved working directory and index state WIP on main: 1234567 Add feature\n"
                )
                
                success, message = service.create_stash("Work in progress")
                
                assert success is True
                assert "Stash created successfully" in message
                mock_run.assert_called_once_with(
                    ["git", "stash", "push", "-m", "Work in progress"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
    
    def test_apply_stash(self) -> None:
        """Test applying a stash."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="On branch main\nChanges not staged for commit:\n..."
                )
                
                success, message = service.apply_stash("0")
                
                assert success is True
                assert "Applied stash 0" in message
                mock_run.assert_called_once_with(
                    ["git", "stash", "apply", "stash@{0}"],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
    
    def test_get_repo_status(self) -> None:
        """Test getting repository status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = """## main...origin/main [ahead 1, behind 2]
 M src/main.py
?? new_file.py
 D deleted_file.py"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                status = service.get_repo_status()
                
                assert isinstance(status, GitRepoStatus)
                assert status.branch == "main"
                assert status.is_clean is False
                assert "src/main.py" in status.modified_files
                assert "new_file.py" in status.untracked_files
                assert "deleted_file.py" in status.deleted_files
                assert status.ahead_by == 1
                assert status.behind_by == 2
    
    def test_get_repo_status_clean(self) -> None:
        """Test getting clean repository status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = "## main"
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                status = service.get_repo_status()
                
                assert status.is_clean is True
                assert len(status.staged_files) == 0
                assert len(status.modified_files) == 0
                assert len(status.untracked_files) == 0
                assert len(status.deleted_files) == 0
    
    def test_get_remote_status(self) -> None:
        """Test getting remote status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            mock_output = """origin	https://github.com/user/repo.git (fetch)
origin	https://github.com/user/repo.git (push)
upstream	https://github.com/original/repo.git (fetch)
upstream	https://github.com/original/repo.git (push)"""
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout=mock_output
                )
                
                remotes = service.get_remote_status()
                
                assert len(remotes) == 2
                assert remotes["origin"] == "https://github.com/user/repo.git"
                assert remotes["upstream"] == "https://github.com/original/repo.git"
    
    def test_clear_cache(self) -> None:
        """Test clearing cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            # Add some data to cache
            service._commit_cache["test"] = "value"
            service._branch_cache = ["test"]
            
            # Clear cache
            service.clear_cache()
            
            assert service._commit_cache == {}
            assert service._branch_cache is None
    
    def test_git_commit_dataclass(self) -> None:
        """Test GitCommit dataclass."""
        commit = GitCommit(
            hash="1234567890abcdef",
            short_hash="12345678",
            author="John Doe",
            email="john@example.com",
            date=datetime.fromtimestamp(1640995200),
            message="Test commit",
            files_changed=5,
            insertions=10,
            deletions=3
        )
        
        assert commit.hash == "1234567890abcdef"
        assert commit.short_hash == "12345678"
        assert commit.author == "John Doe"
        assert commit.email == "john@example.com"
        assert commit.message == "Test commit"
        assert commit.files_changed == 5
        assert commit.insertions == 10
        assert commit.deletions == 3
    
    def test_git_branch_dataclass(self) -> None:
        """Test GitBranch dataclass."""
        branch = GitBranch(
            name="feature",
            is_current=False,
            is_remote=False,
            upstream="origin/feature",
            last_commit="12345678",
            ahead=2,
            behind=1
        )
        
        assert branch.name == "feature"
        assert branch.is_current is False
        assert branch.is_remote is False
        assert branch.upstream == "origin/feature"
        assert branch.last_commit == "12345678"
        assert branch.ahead == 2
        assert branch.behind == 1
    
    def test_git_stash_dataclass(self) -> None:
        """Test GitStash dataclass."""
        stash = GitStash(
            index="0",
            ref="stash@{0}",
            message="WIP on main: Add feature",
            branch="main"
        )
        
        assert stash.index == "0"
        assert stash.ref == "stash@{0}"
        assert stash.message == "WIP on main: Add feature"
        assert stash.branch == "main"
    
    def test_git_diff_dataclass(self) -> None:
        """Test GitDiff dataclass."""
        diff = GitDiff(
            file_path="src/main.py",
            old_file="src/main.py",
            new_file="src/main.py",
            status="M",
            additions=5,
            deletions=2,
            content="+ new line\n- old line"
        )
        
        assert diff.file_path == "src/main.py"
        assert diff.old_file == "src/main.py"
        assert diff.new_file == "src/main.py"
        assert diff.status == "M"
        assert diff.additions == 5
        assert diff.deletions == 2
        assert diff.content == "+ new line\n- old line"
    
    def test_git_repo_status_dataclass(self) -> None:
        """Test GitRepoStatus dataclass."""
        status = GitRepoStatus(
            branch="main",
            is_clean=False,
            staged_files=["file1.py"],
            modified_files=["file2.py"],
            untracked_files=["file3.py"],
            deleted_files=["file4.py"],
            ahead_by=1,
            behind_by=2,
            stashes=3
        )
        
        assert status.branch == "main"
        assert status.is_clean is False
        assert status.staged_files == ["file1.py"]
        assert status.modified_files == ["file2.py"]
        assert status.untracked_files == ["file3.py"]
        assert status.deleted_files == ["file4.py"]
        assert status.ahead_by == 1
        assert status.behind_by == 2
        assert status.stashes == 3
    
    @patch('subprocess.run')
    def test_subprocess_timeout(self, mock_run: Mock) -> None:
        """Test handling of subprocess timeouts."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            # Should handle timeout gracefully
            assert service.get_current_branch() is None
            assert service.get_branches() == []
            assert service.get_commit_history() == []
            assert service.get_stashes() == []
    
    @patch('subprocess.run')
    def test_subprocess_file_not_found(self, mock_run: Mock) -> None:
        """Test handling when git command is not found."""
        mock_run.side_effect = FileNotFoundError("git")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            service = EnhancedGitService(temp_path)
            
            # Should handle missing git gracefully
            assert service.get_current_branch() is None
            assert service.get_branches() == []
