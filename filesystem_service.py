from pathlib import Path
import shutil


class FileSystemService:
    """Pure filesystem and filtering helpers for the TUI app."""

    @staticmethod
    def apply_name_filter(items, query: str):
        normalized = query.strip().lower()
        if not normalized:
            return list(items)
        return [item for item in items if normalized in item.name.lower()]

    @staticmethod
    def resolve_destination_path(source: Path, target_text: str) -> Path:
        target = Path(target_text.strip()).expanduser()
        if not target.is_absolute():
            target = source.parent / target
        if target.exists() and target.is_dir():
            target = target / source.name
        return target

    @staticmethod
    def copy_path(source: Path, destination: Path) -> Path:
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        if not destination.parent.exists():
            raise FileNotFoundError(f"Destination directory not found: {destination.parent}")

        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return destination

    @staticmethod
    def move_path(source: Path, destination: Path) -> Path:
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        if not destination.parent.exists():
            raise FileNotFoundError(f"Destination directory not found: {destination.parent}")

        moved = shutil.move(str(source), str(destination))
        return Path(moved)

    @staticmethod
    def rename_path(source: Path, new_name: str) -> Path:
        normalized_name = new_name.strip()
        if not normalized_name:
            raise ValueError("New name cannot be empty.")
        if "/" in normalized_name or "\\" in normalized_name:
            raise ValueError("Rename expects a name, not a path.")

        destination = source.parent / normalized_name
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")

        source.rename(destination)
        return destination

    @staticmethod
    def delete_path(target: Path) -> None:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
