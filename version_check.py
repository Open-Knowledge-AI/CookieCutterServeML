import sys
import os
import subprocess

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python 3.6-3.10


def get_version_from_pyproject(file_path):
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None


def main():
    # Pre-push hook receives local and remote refs on stdin
    lines = sys.stdin.readlines()
    if not lines:
        print("Not a pre-push hook context. Exiting.")
        sys.exit(0)

    for line in lines:
        local_ref, local_sha, remote_ref, remote_sha = line.split()

        if remote_ref == "refs/heads/main":
            print("🔍 Pushing to main. Checking for version bump...")

            # Get the version from main branch
            try:
                result = subprocess.run(
                    ["git", "show", f"origin/main:pyproject.toml"],
                    capture_output=True,
                    check=True,
                    text=True,
                )
                main_version = get_version_from_pyproject(os.path.join(os.getcwd(), 'pyproject.toml'))

                # Get the version from the current branch's pyproject.toml
                current_version = get_version_from_pyproject("pyproject.toml")

                if main_version and current_version and main_version == current_version:
                    print(f"❌ Version has NOT changed! (still {current_version})", file=sys.stderr)
                    sys.exit(1)
                elif main_version and current_version:
                    print(f"✅ Version changed: {main_version} → {current_version}")
                else:
                    print("❌ Could not determine versions. Check file path and format.", file=sys.stderr)
                    sys.exit(1)

            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to get main branch version: {e}", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
