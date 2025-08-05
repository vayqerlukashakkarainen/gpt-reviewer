# GPT Reviewer

AI-powered GitHub Action that automatically reviews pull requests using OpenAI GPT-4o or Anthropic Claude based on custom project rules.

## Setup

### 1. Create Project Rules

Create `.project-rules.md` in your repository root:

```markdown
# Project Rules

## Code Style
- Use descriptive variable names
- Add docstrings to all functions
- Keep functions under 50 lines

## Security
- Never hardcode API keys or secrets
- Validate all user inputs
```

### 2. Add GitHub Action

Create `.github/workflows/pr-review.yml`:

```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AI PR Review
        uses: your-username/gpt-reviewer@v1
        with:
          repository: ${{ github.repository }}
          pr_number: ${{ github.event.pull_request.number }}
          commit_id: ${{ github.event.pull_request.head.sha }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          ai_provider: "openai"  # or "anthropic"
          ai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### 3. Configure Secrets

Add your AI provider API key to GitHub repository secrets:
- `OPENAI_API_KEY` for OpenAI
- `ANTHROPIC_API_KEY` for Anthropic

## Configuration

| Input | Description | Required |
|-------|-------------|----------|
| `repository` | Repository name (owner/repo) | Yes |
| `pr_number` | Pull request number | Yes |
| `commit_id` | Commit SHA to review | Yes |
| `github_token` | GitHub token for API access | Yes |
| `ai_provider` | AI provider (`openai` or `anthropic`) | No (default: `openai`) |
| `ai_api_key` | API key for selected AI provider | Yes |
