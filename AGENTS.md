# Agent Guidelines for GPT-Reviewer

## Build/Test/Lint Commands
- Install dependencies: `pip install -r requirements.txt`
- Run the main script: `python main.py`
- Test GitHub Action locally: Use `act` or GitHub Actions workflow
- No specific lint/test commands found - this is a simple Python script

## Code Style Guidelines
- **Language**: Python 3.11+
- **Imports**: Standard library first, then third-party (requests, openai, unidiff)
- **Variables**: Use snake_case (e.g., `github_token`, `pr_number`)
- **Constants**: Use UPPER_CASE for environment variables (e.g., `GITHUB_TOKEN`)
- **Functions**: Use snake_case with descriptive names (e.g., `get_unified_diff`)
- **Error Handling**: Use try/except blocks for JSON parsing and API calls
- **Strings**: Use f-strings for formatting, double quotes preferred
- **Comments**: Use emoji prefixes for print statements (✅, ❌, 👉, ⚠️, 📄)

## Project Structure
- `main.py`: Core logic for PR review automation
- `action.yml`: GitHub Action configuration
- `requirements.txt`: Python dependencies (requests, openai, unidiff)
- `.project-rules.md`: Custom review rules (ignored from processing)

## Key Patterns
- Environment variables for configuration
- GitHub API integration for PR comments
- OpenAI GPT-4o for code review
- Unified diff parsing with unidiff library