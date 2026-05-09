"""
Skill definitions for slash commands.

Each skill maps to a system prompt template injected into the agent
when the user triggers it with /skill_name [args].
"""

SKILLS: dict[str, dict] = {
    "review": {
        "description": "Review code changes for bugs, security, and quality",
        "prompt_template": (
            "Perform a thorough code review of the project at: {working_dir}\n"
            "Steps:\n"
            "1. Run `git diff HEAD` or `git diff --staged` to see recent changes\n"
            "2. Read the changed files\n"
            "3. Check for: bugs, security vulnerabilities, code quality issues, performance problems\n"
            "4. Provide a structured review with: Summary, Issues Found, Suggestions\n"
            "{args}"
        ),
    },
    "refactor": {
        "description": "Refactor a file for better quality",
        "prompt_template": (
            "Refactor the following file for better readability, performance, and maintainability: {args}\n"
            "Steps:\n"
            "1. Read the file\n"
            "2. Identify areas to improve (naming, structure, duplication, complexity)\n"
            "3. Apply changes using edit_file or write_file\n"
            "4. Confirm the refactored version is complete and correct"
        ),
    },
    "test": {
        "description": "Generate unit tests for a file",
        "prompt_template": (
            "Generate comprehensive unit tests for: {args}\n"
            "Steps:\n"
            "1. Read the target file to understand all functions/classes\n"
            "2. Create a test file with tests covering: normal cases, edge cases, error cases\n"
            "3. Run the tests to verify they pass\n"
            "4. Fix any test failures"
        ),
    },
    "explain": {
        "description": "Explain a file or function in detail",
        "prompt_template": (
            "Explain the following in detail: {args}\n"
            "Read the relevant file(s) and provide:\n"
            "- Purpose and overview\n"
            "- How it works (step by step)\n"
            "- Key functions/classes and their roles\n"
            "- Dependencies and interactions with other parts"
        ),
    },
    "fix": {
        "description": "Find and fix bugs in the project",
        "prompt_template": (
            "Find and fix bugs in the project at: {working_dir}\n"
            "{args}\n"
            "Steps:\n"
            "1. Read the relevant files\n"
            "2. Identify the bug(s)\n"
            "3. Explain what is wrong and why\n"
            "4. Apply the fix using edit_file\n"
            "5. Verify the fix makes sense"
        ),
    },
    "docs": {
        "description": "Generate documentation for a file",
        "prompt_template": (
            "Generate documentation for: {args}\n"
            "Steps:\n"
            "1. Read the file\n"
            "2. Add/update docstrings for all public functions and classes\n"
            "3. If a README section is relevant, generate it too\n"
            "4. Save changes using edit_file or write_file"
        ),
    },
    "commit": {
        "description": "Create a git commit with an appropriate message",
        "prompt_template": (
            "Create a git commit for the current changes in: {working_dir}\n"
            "Steps:\n"
            "1. Run `git diff --staged` and `git diff` to review changes\n"
            "2. Run `git status` to see all modified files\n"
            "3. Write a concise, meaningful commit message (imperative mood, under 72 chars)\n"
            "4. Run `git add -A && git commit -m '<message>'`\n"
            "{args}"
        ),
    },
    "lint": {
        "description": "Lint and auto-fix code style issues",
        "prompt_template": (
            "Lint and fix code style issues in: {args or working_dir}\n"
            "Steps:\n"
            "1. List relevant source files\n"
            "2. Run linter (flake8 for Python, eslint for JS/TS)\n"
            "3. Fix auto-fixable issues using edit_file\n"
            "4. Report any remaining issues that need manual attention"
        ).replace("or working_dir", ""),
    },
}
