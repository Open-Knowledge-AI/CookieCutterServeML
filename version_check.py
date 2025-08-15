import re
import sys
import yaml
import fnmatch
import subprocess

from pathlib import Path
from packaging.version import Version, InvalidVersion

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.6-3.10

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def load_versioning_config(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_version_from_pyproject(file_path: Path):
    try:
        with file_path.open("rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception as e:
        console.print(f"[bold red]Error reading {file_path}: {e}[/bold red]")
        return None


def update_pyproject_version(file_path: Path, new_version: str):
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()
        content_new = re.sub(
            r'version\s*=\s*"[0-9A-Za-z\.\-]+"',
            f'version = "{new_version}"',
            content
        )
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content_new)
        console.print(f"[bold green]Updated pyproject.toml to version {new_version}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to update pyproject.toml: {e}[/bold red]")
        sys.exit(1)


def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Failed to get current branch: {e}[/bold red]")
        sys.exit(1)


def get_main_version(default_branch="main"):
    try:
        result = subprocess.run(
            ["git", "show", f"origin/{default_branch}:pyproject.toml"],
            capture_output=True,
            text=True,
            check=True,
        )
        import io
        data = tomllib.load(io.BytesIO(result.stdout.encode()))
        return data["project"]["version"]
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Failed to get main branch version: {e}[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Failed to parse main branch pyproject.toml: {e}[/bold red]")
        sys.exit(1)


def get_commits_since_main(default_branch="main"):
    try:
        result = subprocess.run(
            ["git", "log", f"origin/{default_branch}..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Failed to get commits: {e}[/bold red]")
        return []


def suggest_semver_bump(current_version: str, commits: list[str]) -> str:
    try:
        ver = Version(current_version)
    except InvalidVersion:
        console.print(f"[bold red]Invalid current version: {current_version}[/bold red]")
        sys.exit(1)

    major, minor, patch = ver.major, ver.minor, ver.micro

    bump_major = any("BREAKING CHANGE" in c or c.startswith("feat!") for c in commits)
    bump_minor = any(c.startswith("feat:") for c in commits)
    bump_patch = any(c.startswith("fix:") for c in commits)

    if bump_major:
        return f"{major + 1}.0.0"
    elif bump_minor:
        return f"{major}.{minor + 1}.0"
    elif bump_patch:
        return f"{major}.{minor}.{patch + 1}"
    else:
        return current_version


def suggest_next_version(current_version: str, pre_release: str | None = None):
    try:
        ver = Version(current_version)
    except InvalidVersion:
        console.print(f"[bold red]Invalid current version: {current_version}[/bold red]")
        sys.exit(1)

    if pre_release:
        if ver.pre and ver.pre[0] == pre_release:
            new_pre = (pre_release, ver.pre[1] + 1)
        else:
            new_pre = (pre_release, 1)
        new_version = f"{ver.major}.{ver.minor}.{ver.micro}-{new_pre[0]}.{new_pre[1]}"
    else:
        new_version = f"{ver.major}.{ver.minor}.{ver.micro + 1}"
    return new_version


def get_pre_release_for_branch(branch: str, branch_mappings: dict) -> str | None:
    for pattern, pre in branch_mappings.items():
        if fnmatch.fnmatch(branch, pattern):
            return pre
    return None


def print_version_warning(branch, current_version, suggested_version):
    table = Table(show_header=False, box=None)
    table.add_row("Branch:", branch)
    table.add_row("Current version:", current_version)
    table.add_row("Suggested version:", suggested_version)
    table.add_row("", "Please update pyproject.toml before pushing!")

    console.print(
        Panel(
            table,
            title="⚠️  VERSION NOT BUMPED ⚠️",
            border_style="bold red",
            style="bold white on red",
            expand=False,
        )
    )


def print_auto_bump_panel(branch, old_version, new_version):
    table = Table(show_header=False, box=None)
    table.add_row("Branch:", branch)
    table.add_row("Old version:", old_version)
    table.add_row("New version:", new_version)
    table.add_row("", "This version was auto-bumped based on commits!")

    console.print(
        Panel(
            table,
            title="🚨 VERSION AUTO-BUMPED 🚨",
            border_style="bold yellow",
            style="bold black on yellow",
            expand=True,
        )
    )


def main():
    config = load_versioning_config(Path("versioning.yaml"))
    default_branch = config.get("default_branch", "main")
    branch_mappings = config.get("pre_release_branches", {})

    branch = get_current_branch()
    current_version = get_version_from_pyproject(Path("pyproject.toml"))
    if not current_version:
        sys.exit(1)

    main_version = get_main_version(default_branch)
    if not main_version:
        sys.exit(1)

    commits = get_commits_since_main(default_branch)
    suggested_semver = suggest_semver_bump(main_version, commits)

    pre_release = get_pre_release_for_branch(branch, branch_mappings)

    if pre_release:
        if pre_release not in current_version:
            suggested = suggest_next_version(suggested_semver, pre_release)
            print_version_warning(branch, current_version, suggested)
            update_pyproject_version(Path("pyproject.toml"), suggested)
            try:
                subprocess.run(["python", "changelog_generator.py", suggested], check=True)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Failed to update CHANGELOG.md: {e}[/bold red]")
            print_auto_bump_panel(branch, current_version, suggested)
        else:
            console.print(f"[green]✅ Pre-release version {current_version} looks good.[/green]")
    else:
        if current_version == main_version:
            suggested = suggested_semver
            print_version_warning(branch, current_version, suggested)

            # Prompt user to auto-bump
            response = input(f"Do you want to auto-bump to {suggested}? [y/N]: ").strip().lower()
            if response == "y":
                update_pyproject_version(Path("pyproject.toml"), suggested)
                subprocess.run(["python", "changelog_generator.py", suggested], check=True)
                console.print(f"[bold green]Version bumped and CHANGELOG.md updated![/bold green]")
            else:
                sys.exit(1)
        else:
            subprocess.run(["python", "changelog_generator.py", current_version], check=True)
            console.print(f"[bold green]CHANGELOG.md updated for version {current_version}[/bold green]")
            console.print(f"[green]✅ Version bumped: {main_version} → {current_version}[/green]")


if __name__ == "__main__":
    main()
