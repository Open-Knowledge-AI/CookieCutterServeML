import re
import subprocess

from pathlib import Path
from collections import defaultdict

from rich.panel import Panel
from rich.console import Console

console = Console()

CHANGELOG_FILE = Path("CHANGELOG.md")


def get_last_tag() -> str:
    """Get the latest git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""  # No tags yet


def get_commits_with_branches(tag: str):
    """Get all commits since a tag, including their branches."""
    cmd = ["git", "log", "--pretty=format:%H %s"]
    if tag:
        cmd.append(f"{tag}..HEAD")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = result.stdout.splitlines()

        commits_with_branches = []
        for c in commits:
            sha, message = c.split(" ", 1)
            # get branches containing this commit
            br = subprocess.run(
                ["git", "branch", "--contains", sha],
                capture_output=True,
                text=True,
                check=True,
            )
            branch_list = [b.strip("* ").strip() for b in br.stdout.splitlines()]
            branch_name = branch_list[0] if branch_list else "main"
            commits_with_branches.append((branch_name, message))
        return commits_with_branches
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Failed to get git commits with branches: {e}[/bold red]")
        return []


def categorize_commits(commits):
    """Categorize commits into features, fixes, breaking."""
    features, fixes, breaking = [], [], []
    for c in commits:
        if re.search(r"BREAKING CHANGE|feat!:", c):
            breaking.append(c)
        elif c.startswith("feat:"):
            features.append(c)
        elif c.startswith("fix:"):
            fixes.append(c)
        else:
            # treat other commits as "misc"
            fixes.append(c)
    return features, fixes, breaking


def generate_changelog(new_version: str):
    last_tag = get_last_tag()
    commits_with_branches = get_commits_with_branches(last_tag)
    if not commits_with_branches:
        console.print("[yellow]No commits found since last tag.[/yellow]")
        return

    # group commits by branch
    branch_dict = defaultdict(list)
    for branch, message in commits_with_branches:
        branch_dict[branch].append(message)

    changelog_lines = [f"# Changelog for version {new_version}\n"]

    for branch, messages in branch_dict.items():
        changelog_lines.append(f"### {branch}")

        features, fixes, breaking = categorize_commits(messages)

        if breaking:
            changelog_lines.append("#### ⚠️ Breaking Changes")
            for b in breaking:
                changelog_lines.append(f"- {b}")
        if features:
            changelog_lines.append("#### ✨ Features")
            for f in features:
                changelog_lines.append(f"- {f}")
        if fixes:
            changelog_lines.append("#### 🐛 Fixes")
            for fx in fixes:
                changelog_lines.append(f"- {fx}")

        changelog_lines.append("")  # blank line between branches

    with CHANGELOG_FILE.open("a", encoding="utf-8") as f:
        f.write("\n".join(changelog_lines) + "\n")

    console.print(
        Panel(
            f"CHANGELOG.md updated with version {new_version}",
            title="📄 Changelog Updated",
            border_style="green",
        )
    )


if __name__ == "__main__":
    # Optional: take new_version from command-line argument
    import sys
    if len(sys.argv) > 1:
        new_ver = sys.argv[1]
    else:
        console.print("[bold red]Please provide the new version as an argument[/bold red]")
        sys.exit(1)

    generate_changelog(new_ver)
