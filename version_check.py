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
    branch = get_current_branch()
    current_version = get_version_from_pyproject(Path("pyproject.toml"))
    if not current_version:
        sys.exit(1)

    main_version = get_main_version()
    if not main_version:
        sys.exit(1)

    # Determine pre-release type
    if branch.startswith("feature/"):
        pre_release = "alpha"
    elif branch.startswith("beta/"):
        pre_release = "beta"
    elif branch.startswith("rc/"):
        pre_release = "rc"
    else:
        pre_release = None

    # Compute suggested version
    # Handle pre-release branches
    if pre_release:
        if f"{pre_release}" not in current_version:
            suggested = suggest_next_version(main_version, pre_release)
            print_version_warning(branch, current_version, suggested)
            update_pyproject_version(Path("pyproject.toml"), suggested)

            # Update changelog automatically for pre-release
            subprocess.run(["python", "changelog_generator.py", suggested], check=True)

            warning_table = Table(show_header=False, box=None)
            warning_table.add_row("Branch:", branch)
            warning_table.add_row("Old version:", current_version)
            warning_table.add_row("New version:", suggested)
            warning_table.add_row("", "This pre-release version was auto-bumped!")

            console.print(
                Panel(
                    warning_table,
                    title="🚨 PRE-RELEASE VERSION AUTO-BUMPED 🚨",
                    border_style="bold yellow",
                    style="bold black on yellow",
                    expand=True,
                )
            )
        else:
            console.print(f"[green]✅ Pre-release version {current_version} looks good.[/green]")
    else:
        # Standard release branch check
        if current_version == main_version:
            # Auto-suggest next patch version
            suggested = suggest_next_version(current_version)
            print_version_warning(branch, current_version, suggested)

            response = input(f"Do you want to auto-bump to {suggested}? [y/N]: ")
            if response.lower() == "y":
                update_pyproject_version(Path("pyproject.toml"), suggested)
                console.print(f"[green]✅ Version bumped to {suggested}[/green]")
                # Optional: update changelog automatically
                subprocess.run(["python", "changelog_generator.py", suggested], check=True)
            else:
                console.print("[yellow]Version not changed.[/yellow]")
                sys.exit(1)
        else:
            console.print(f"[green]✅ Version bumped: {main_version} → {current_version}[/green]")


if __name__ == "__main__":
    main()
