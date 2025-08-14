import sys
import subprocess

from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.6-3.10


def get_version_from_file(file_path: Path) -> str | None:
    try:
        with file_path.open("rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None


def get_version_from_git(path_in_repo: str, ref: str = "origin/main") -> str | None:
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{path_in_repo}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return get_version_from_string(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to get {path_in_repo} from {ref}: {e}", file=sys.stderr)
        return None


def get_version_from_string(toml_content: str) -> str | None:
    try:
        data = tomllib.loads(toml_content)
        return data["project"]["version"]
    except Exception as e:
        print(f"Error parsing TOML content: {e}", file=sys.stderr)
        return None


def main():
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found in the current directory.", file=sys.stderr)
        sys.exit(1)

    main_version = get_version_from_git("pyproject.toml")
    current_version = get_version_from_file(pyproject_path)

    if not main_version or not current_version:
        print("❌ Could not determine versions. Check pyproject.toml format.", file=sys.stderr)
        sys.exit(1)

    if main_version == current_version:
        print(f"❌ Version has NOT changed! (still {current_version})", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Version changed: {main_version} → {current_version}")


if __name__ == "__main__":
    main()
