import subprocess
from pathlib import Path

import httpx


def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo. Returns top results."""
    try:
        resp = httpx.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_redirect": "1", "no_html": "1"},
            timeout=10,
        )
        data = resp.json()
        results = []
        for r in data.get("RelatedTopics", [])[:6]:
            if isinstance(r, dict) and r.get("Text"):
                results.append(f"- {r['Text']}")
                if r.get("FirstURL"):
                    results.append(f"  {r['FirstURL']}")
        abstract = data.get("AbstractText", "")
        if abstract:
            results.insert(0, abstract)
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {e}"


def http_request(url: str, method: str = "GET", body: str = "") -> str:
    """Make an HTTP request to a URL. method: GET, POST, PUT, DELETE."""
    try:
        resp = httpx.request(method.upper(), url, content=body.encode(), timeout=15)
        return f"Status: {resp.status_code}\n{resp.text[:2000]}"
    except Exception as e:
        return f"Request error: {e}"


def run_tests(path: str = ".", framework: str = "auto") -> str:
    """Run the test suite. framework: 'pytest', 'jest', or 'auto' to detect."""
    p = Path(path)
    if framework == "auto":
        if (p / "pytest.ini").exists() or (p / "pyproject.toml").exists() or list(p.glob("test_*.py")) or list(p.glob("*_test.py")):
            cmd = "pytest -v"
        else:
            cmd = "npm test -- --watchAll=false"
    elif framework == "pytest":
        cmd = "pytest -v"
    else:
        cmd = "npm test -- --watchAll=false"

    result = subprocess.run(cmd, shell=True, cwd=path, capture_output=True, text=True, timeout=120)
    return (result.stdout + result.stderr).strip() or "(no output)"


def git_status(working_dir: str = ".") -> str:
    """Show git status and recent diff in the working directory."""
    status = subprocess.run("git status", shell=True, cwd=working_dir, capture_output=True, text=True)
    diff = subprocess.run("git diff --stat HEAD", shell=True, cwd=working_dir, capture_output=True, text=True)
    return f"{status.stdout}\n{diff.stdout}".strip()


def git_commit(message: str, working_dir: str = ".") -> str:
    """Stage all changes and create a git commit with the given message."""
    add = subprocess.run("git add -A", shell=True, cwd=working_dir, capture_output=True, text=True)
    commit = subprocess.run(
        f'git commit -m "{message}"',
        shell=True, cwd=working_dir, capture_output=True, text=True,
    )
    return (add.stdout + add.stderr + commit.stdout + commit.stderr).strip()


def run_code(command: str, working_dir: str = ".", expect_errors: bool = False) -> str:
    """Run a code execution command (e.g., python script.py). If expect_errors is False and there's an error, attempt to fix common issues."""
    result = subprocess.run(command, shell=True, cwd=working_dir, capture_output=True, text=True, timeout=120)
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0 and not expect_errors:
        # Attempt simple fixes
        if "ModuleNotFoundError" in output:
            # Suggest pip install
            return f"Error: {output}\nSuggestion: Install missing module with 'pip install <module>'"
        elif "SyntaxError" in output:
            return f"Error: {output}\nSuggestion: Check syntax in the code."
        else:
            return f"Error: {output}\nSuggestion: Review the error and fix accordingly."
    return output or "(no output)"


def make_extended_tools(working_dir: str) -> list:
    """Return extended tools bound to working_dir where applicable."""

    def _run_tests(path: str = ".", framework: str = "auto") -> str:
        """Run the test suite in path. framework: 'pytest', 'jest', or 'auto'."""
        return run_tests(str(Path(working_dir) / path) if not Path(path).is_absolute() else path, framework)

    def _git_status() -> str:
        """Show git status and diff summary for the current project."""
        return git_status(working_dir)

    def _git_commit(message: str) -> str:
        """Stage all changes and commit with the given message."""
        return git_commit(message, working_dir)

    def _run_code(command: str, expect_errors: bool = False) -> str:
        """Run a code execution command. If errors occur and expect_errors=False, provide suggestions."""
        return run_code(command, working_dir, expect_errors)

    def _lint_file(path: str) -> str:
        """Lint a file using flake8 (Python) or eslint (JS/TS)."""
        return lint_file(path, working_dir)

    return [web_search, http_request, _run_tests, _git_status, _git_commit, _run_code, _lint_file]
