"""Enhanced Git service with deep integration capabilities."""
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum

from git_service import GitService, GitStatus


class GitRefType(Enum):
    """Types of Git references."""
    BRANCH = "branch"
    TAG = "tag"
    REMOTE = "remote"


@dataclass
class GitCommit:
    """Represents a Git commit."""
    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int


@dataclass
class GitBranch:
    """Represents a Git branch."""
    name: str
    is_current: bool
    is_remote: bool
    upstream: Optional[str]
    last_commit: Optional[str]
    ahead: Optional[int]
    behind: Optional[int]


@dataclass
class GitStash:
    """Represents a Git stash."""
    index: str
    ref: str
    message: str
    branch: Optional[str]


@dataclass
class GitDiff:
    """Represents a Git diff."""
    file_path: str
    old_file: str
    new_file: str
    status: str  # A, D, M, etc.
    additions: int
    deletions: int
    content: Optional[str]


@dataclass
class GitRepoStatus:
    """Overall repository status."""
    branch: str
    is_clean: bool
    staged_files: List[str]
    modified_files: List[str]
    untracked_files: List[str]
    deleted_files: List[str]
    ahead_by: Optional[int]
    behind_by: Optional[int]
    stashes: int


class EnhancedGitService(GitService):
    """Enhanced Git service with deep integration capabilities."""

    def __init__(self, path: Path) -> None:
        """Initialize enhanced Git service.
        
        Args:
            path: Path to the Git repository.
        """
        super().__init__(path)
        self._commit_cache: Dict[str, GitCommit] = {}
        self._branch_cache: Optional[List[GitBranch]] = None

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name.
        
        Returns:
            Current branch name, or None if not on a branch.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                branch = result.stdout.strip()
                return branch if branch != "HEAD" else None
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        return None

    def get_branches(self, include_remote: bool = True) -> List[GitBranch]:
        """Get all branches with their status.
        
        Args:
            include_remote: Whether to include remote branches.
            
        Returns:
            List of GitBranch objects.
        """
        if self._branch_cache is not None:
            return self._branch_cache

        branches = []
        current_branch = self.get_current_branch()

        try:
            # Get local branches
            result = subprocess.run(
                ["git", "branch", "-v", "--no-abbrev"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        is_current = line.startswith('*')
                        branch_part = line[2:].strip()
                        parts = branch_part.split()
                        if parts:
                            name = parts[0]
                            last_commit = parts[1] if len(parts) > 1 else None
                            
                            branch = GitBranch(
                                name=name,
                                is_current=is_current,
                                is_remote=False,
                                upstream=None,
                                last_commit=last_commit,
                                ahead=None,
                                behind=None
                            )
                            branches.append(branch)

            # Get remote branches if requested
            if include_remote:
                remote_result = subprocess.run(
                    ["git", "branch", "-r", "-v", "--no-abbrev"],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                
                if remote_result.returncode == 0:
                    for line in remote_result.stdout.strip().split('\n'):
                        if line.strip() and not line.strip().startswith('->'):
                            branch_part = line.strip()
                            parts = branch_part.split()
                            if parts:
                                name = parts[0]
                                last_commit = parts[1] if len(parts) > 1 else None
                                
                                branch = GitBranch(
                                    name=name,
                                    is_current=False,
                                    is_remote=True,
                                    upstream=None,
                                    last_commit=last_commit,
                                    ahead=None,
                                    behind=None
                                )
                                branches.append(branch)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        self._branch_cache = branches
        return branches

    def switch_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Switch to a different branch.
        
        Args:
            branch_name: Name of the branch to switch to.
            
        Returns:
            Tuple of (success, message).
        """
        try:
            result = subprocess.run(
                ["git", "checkout", branch_name],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                self._branch_cache = None  # Clear cache
                return True, f"Switched to branch '{branch_name}'"
            else:
                return False, result.stderr.strip() or f"Failed to switch to '{branch_name}'"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Error switching branch: {str(e)}"

    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> Tuple[bool, str]:
        """Create a new branch.
        
        Args:
            branch_name: Name of the new branch.
            from_branch: Base branch to create from (optional).
            
        Returns:
            Tuple of (success, message).
        """
        try:
            cmd = ["git", "branch", branch_name]
            if from_branch:
                cmd.append(from_branch)
                
            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                self._branch_cache = None  # Clear cache
                return True, f"Created branch '{branch_name}'"
            else:
                return False, result.stderr.strip() or f"Failed to create branch '{branch_name}'"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Error creating branch: {str(e)}"

    def get_commit_history(self, limit: int = 20, branch: Optional[str] = None) -> List[GitCommit]:
        """Get commit history.
        
        Args:
            limit: Maximum number of commits to return.
            branch: Branch to get history from (optional).
            
        Returns:
            List of GitCommit objects.
        """
        commits = []
        
        try:
            cmd = [
                "git", "log",
                f"--max-count={limit}",
                "--pretty=format:%H|%h|%an|%ae|%at|%s",
                "--stat=200",  # Limit stat line length
                "--no-abbrev-commit"
            ]
            
            if branch:
                cmd.append(branch)
                
            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    commit_blocks = output.split('\n\n')
                    
                    for block in commit_blocks:
                        lines = block.strip().split('\n')
                        if len(lines) >= 2:
                            # Parse commit header
                            header_parts = lines[0].split('|')
                            if len(header_parts) >= 6:
                                commit_hash = header_parts[0]
                                short_hash = header_parts[1]
                                author = header_parts[2]
                                email = header_parts[3]
                                timestamp = int(header_parts[4])
                                message = header_parts[5]
                                
                                date = datetime.fromtimestamp(timestamp)
                                
                                # Parse stats from remaining lines
                                files_changed = 0
                                insertions = 0
                                deletions = 0
                                
                                for line in lines[1:]:
                                    if 'files changed' in line or 'file changed' in line:
                                        # Parse:  5 files changed, 23 insertions(+), 7 deletions(-)
                                        # or:  1 file changed, 23 insertions(+), 7 deletions(-)
                                        parts = line.strip().split(',')
                                        for part in parts:
                                            if 'files changed' in part or 'file changed' in part:
                                                files_changed = int(part.strip().split()[0])
                                            elif 'insertion' in part:
                                                insertions = int(part.strip().split()[0])
                                            elif 'deletion' in part:
                                                deletions = int(part.strip().split()[0])
                                
                                commit = GitCommit(
                                    hash=commit_hash,
                                    short_hash=short_hash,
                                    author=author,
                                    email=email,
                                    date=date,
                                    message=message,
                                    files_changed=files_changed,
                                    insertions=insertions,
                                    deletions=deletions
                                )
                                
                                commits.append(commit)
                                self._commit_cache[commit_hash] = commit

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError, ValueError):
            pass

        return commits

    def get_diff(self, file_path: Optional[str] = None, commit_hash: Optional[str] = None) -> List[GitDiff]:
        """Get diff information.
        
        Args:
            file_path: Specific file to diff (optional).
            commit_hash: Commit to diff against (optional).
            
        Returns:
            List of GitDiff objects.
        """
        diffs = []
        
        try:
            cmd = ["git", "diff", "--numstat", "--porcelain"]
            
            if commit_hash:
                cmd.append(commit_hash)
            elif file_path:
                cmd.append("--")
                cmd.append(file_path)
                
            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    for line in output.split('\n'):
                        if line.strip():
                            # Parse numstat format: additions deletions filename
                            parts = line.strip().split('\t')
                            if len(parts) >= 3:
                                additions = int(parts[0]) if parts[0] != '-' else 0
                                deletions = int(parts[1]) if parts[1] != '-' else 0
                                file_path = parts[2]
                                
                                # Get the actual diff content
                                diff_cmd = ["git", "diff"]
                                if commit_hash:
                                    diff_cmd.append(commit_hash)
                                diff_cmd.append("--")
                                diff_cmd.append(file_path)
                                
                                diff_result = subprocess.run(
                                    diff_cmd,
                                    cwd=self.path,
                                    capture_output=True,
                                    text=True,
                                    timeout=5,
                                )
                                
                                content = diff_result.stdout if diff_result.returncode == 0 else None
                                
                                diff = GitDiff(
                                    file_path=file_path,
                                    old_file=file_path,
                                    new_file=file_path,
                                    status="M",  # Simplified
                                    additions=additions,
                                    deletions=deletions,
                                    content=content
                                )
                                diffs.append(diff)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return diffs

    def get_stashes(self) -> List[GitStash]:
        """Get list of stashes.
        
        Returns:
            List of GitStash objects.
        """
        stashes = []
        
        try:
            result = subprocess.run(
                ["git", "stash", "list"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    for line in output.split('\n'):
                        if line.strip():
                            # Parse: stash@{0}: WIP on main: 1234567 Commit message
                            parts = line.split(':', 2)
                            if len(parts) >= 3:
                                ref = parts[0].strip()
                                branch_info = parts[1].strip()
                                message = parts[2].strip()
                                
                                # Reconstruct full message
                                full_message = f"{branch_info}: {message}"
                                
                                # Extract branch from branch_info
                                branch = None
                                if " on " in branch_info:
                                    branch = branch_info.split(" on ")[1]
                                elif branch_info.startswith("On "):
                                    branch = branch_info[3:]  # Remove "On "
                                
                                stash = GitStash(
                                    index=ref.split('{')[1].rstrip('}'),
                                    ref=ref,
                                    message=full_message,
                                    branch=branch
                                )
                                stashes.append(stash)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return stashes

    def create_stash(self, message: str = "") -> Tuple[bool, str]:
        """Create a new stash.
        
        Args:
            message: Optional stash message.
            
        Returns:
            Tuple of (success, message).
        """
        try:
            cmd = ["git", "stash", "push"]
            if message:
                cmd.extend(["-m", message])
                
            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                return True, "Stash created successfully"
            else:
                return False, result.stderr.strip() or "Failed to create stash"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Error creating stash: {str(e)}"

    def apply_stash(self, stash_index: str = "0") -> Tuple[bool, str]:
        """Apply a stash.
        
        Args:
            stash_index: Stash index to apply (default "0").
            
        Returns:
            Tuple of (success, message).
        """
        try:
            result = subprocess.run(
                ["git", "stash", "apply", f"stash@{{{stash_index}}}"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                return True, f"Applied stash {stash_index}"
            else:
                return False, result.stderr.strip() or f"Failed to apply stash {stash_index}"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            return False, f"Error applying stash: {str(e)}"

    def get_repo_status(self) -> GitRepoStatus:
        """Get comprehensive repository status.
        
        Returns:
            GitRepoStatus with complete repository information.
        """
        branch = self.get_current_branch() or "HEAD"
        is_clean = True
        staged_files = []
        modified_files = []
        untracked_files = []
        deleted_files = []
        ahead_by = None
        behind_by = None

        try:
            # Get detailed status
            result = subprocess.run(
                ["git", "status", "--porcelain=v1", "-b"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if line.startswith('## '):
                        # Parse branch info: ## main...origin/main [ahead 1, behind 2]
                        branch_info = line[3:]
                        if '...' in branch_info:
                            parts = branch_info.split('...')
                            branch = parts[0]
                            remote_info = parts[1] if len(parts) > 1 else ""
                            
                            if '[' in remote_info:
                                status_part = remote_info.split('[')[1].rstrip(']')
                                for status in status_part.split(','):
                                    status = status.strip()
                                    if status.startswith('ahead '):
                                        ahead_by = int(status.split()[1])
                                    elif status.startswith('behind '):
                                        behind_by = int(status.split()[1])
                    elif line:
                        status_code = line[:2]
                        file_path = line[3:] if len(line) > 3 else ""
                        
                        if status_code[0] in ['A', 'M', 'D', 'R', 'C']:
                            staged_files.append(file_path)
                            is_clean = False
                        if status_code[1] in ['M', 'D']:
                            modified_files.append(file_path)
                            is_clean = False
                        if status_code == '??':
                            untracked_files.append(file_path)
                            is_clean = False
                        if status_code == ' D':
                            deleted_files.append(file_path)
                            is_clean = False

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        stashes = len(self.get_stashes())

        return GitRepoStatus(
            branch=branch,
            is_clean=is_clean,
            staged_files=staged_files,
            modified_files=modified_files,
            untracked_files=untracked_files,
            deleted_files=deleted_files,
            ahead_by=ahead_by,
            behind_by=behind_by,
            stashes=stashes
        )

    def get_remote_status(self) -> Dict[str, str]:
        """Get remote repository status.
        
        Returns:
            Dictionary with remote information.
        """
        remote_info = {}
        
        try:
            # Get remote URLs
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1]
                            remote_info[remote_name] = remote_url

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        return remote_info

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._commit_cache.clear()
        self._branch_cache = None
