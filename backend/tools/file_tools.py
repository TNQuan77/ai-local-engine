import os
import subprocess
import glob as glob_module
import platform
from pathlib import Path


def _resolve(working_dir: str, path: str) -> str:
    if os.path.isabs(path):
        return path
    return str(Path(working_dir) / path)


def _is_windows() -> bool:
    return platform.system() == "Windows"


def make_file_tools(working_dir: str) -> list:
    """Return file system tools bound to working_dir."""

    def read_file(path: str) -> str:
        """Read the contents of a file. path can be relative or absolute."""
        full = _resolve(working_dir, path)
        with open(full, encoding="utf-8") as f:
            return f.read()

    def write_file(path: str, content: str) -> str:
        """Create or overwrite a file with new content."""
        full = _resolve(working_dir, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        # Verification
        if os.path.exists(full):
            return f"Successfully created/updated {full}"
        else:
            return f"ERROR: Failed to create {full}"

    def create_file(path: str | None = None, content: str = "") -> str:
        """Create a file with optional content."""
        if not path:
            return "ERROR: create_file requires a 'path' argument."
        full = _resolve(working_dir, path)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        # Verification
        if os.path.exists(full) and os.path.isfile(full):
            return f"Successfully created {full}"
        else:
            return f"ERROR: Failed to create {full}"

    def create_directory(path: str) -> str:
        """Create a directory and all parent directories if needed."""
        full = _resolve(working_dir, path)
        os.makedirs(full, exist_ok=True)
        # Verification
        if os.path.exists(full) and os.path.isdir(full):
            return f"Successfully created directory {full}"
        else:
            return f"ERROR: Failed to create directory {full}"

    def edit_file(path: str, old_string: str, new_string: str) -> str:
        """Replace exactly one occurrence of old_string with new_string in a file."""
        full = _resolve(working_dir, path)
        content = open(full, encoding="utf-8").read()
        if old_string not in content:
            return f"ERROR: old_string not found in {path}"
        with open(full, "w", encoding="utf-8") as f:
            f.write(content.replace(old_string, new_string, 1))
        return f"Edited {full}"

    def run_bash(command: str) -> str:
        """Run a shell command in the working directory. Returns stdout + stderr."""
        # OS-aware shell
        shell_cmd = "cmd" if _is_windows() else "/bin/bash"
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=60,
            executable=shell_cmd if not _is_windows() else None,
        )
        output = (result.stdout + result.stderr).strip()
        return output or "(no output)"

    def list_files(pattern: str = "**/*") -> str:
        """Find files matching a glob pattern in the project. Example: '**/*.py'"""
        matches = glob_module.glob(pattern, root_dir=working_dir, recursive=True)
        files = [m for m in matches if os.path.isfile(_resolve(working_dir, m))]
        return "\n".join(files) if files else "(no files found)"

    def search_in_files(text: str, file_pattern: str = "**/*") -> str:
        """Search for text in files matching a pattern. Returns file:line:content matches."""
        results = []
        for filepath in glob_module.glob(file_pattern, root_dir=working_dir, recursive=True):
            full = _resolve(working_dir, filepath)
            if not os.path.isfile(full):
                continue
            try:
                for i, line in enumerate(open(full, encoding="utf-8"), 1):
                    if text in line:
                        results.append(f"{filepath}:{i}: {line.rstrip()}")
            except (UnicodeDecodeError, PermissionError):
                pass
        return "\n".join(results) if results else "(not found)"

    return [read_file, write_file, create_file, create_directory, edit_file, run_bash, list_files, search_in_files]
