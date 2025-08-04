# 🤖 GPT Reviewer - AI-Powered Code Review GitHub Action

An intelligent GitHub Action that automatically reviews pull requests using OpenAI's GPT-4o model based on your custom project rules. It analyzes code changes and posts inline comments directly on your PRs with suggestions, warnings, and best practice recommendations.

## ✨ Features

- 🔍 **Intelligent Code Analysis** - Uses GPT-4o to understand code context and patterns
- 📋 **Custom Rules Engine** - Define your own review criteria in `.project-rules.md`
- 💬 **Inline PR Comments** - Posts suggestions directly on specific lines of code
- 🎯 **Addition-Only Review** - Focuses only on new/changed code, not existing codebase
- 🔒 **Secure** - Uses GitHub tokens and OpenAI API keys securely
- ⚡ **Fast** - Processes only the diff, not entire files

## 🚀 Quick Start

### 1. Create Project Rules

Create a `.project-rules.md` file in your repository root with your coding standards:

```markdown
# Project Rules

## Code Style
- Use descriptive variable names
- Add docstrings to all functions
- Keep functions under 50 lines

## Security
- Never hardcode API keys or secrets
- Validate all user inputs
- Use parameterized queries for database operations
```

### 2. Set up GitHub Action

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
          ai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### 3. Configure Secrets

Add your OpenAI API key to GitHub repository secrets:
- Go to Settings → Secrets and variables → Actions
- Add `OPENAI_API_KEY` with your OpenAI API key

## 📖 How It Works

1. **Trigger** - Action runs when PRs are opened or updated
2. **Diff Analysis** - Fetches unified diff from GitHub API
3. **Rule Loading** - Reads your custom rules from `.project-rules.md`
4. **AI Review** - Sends code changes + rules to GPT-4o for analysis
5. **Comment Posting** - Posts inline comments on specific lines with suggestions

## ⚙️ Configuration

### Action Inputs

| Input | Description | Required |
|-------|-------------|----------|
| `repository` | Repository name (owner/repo) | ✅ |
| `pr_number` | Pull request number | ✅ |
| `commit_id` | Commit SHA to review | ✅ |
| `github_token` | GitHub token for API access | ✅ |
| `ai_api_key` | OpenAI API key | ✅ |

### Environment Variables

The action uses these environment variables internally:
- `GITHUB_TOKEN` - For GitHub API authentication
- `GITHUB_REPOSITORY` - Target repository
- `PR_NUMBER` - Pull request number
- `COMMIT_ID` - Commit SHA
- `OPENAI_API_KEY` - OpenAI API key

## 🔧 Local Development

### Prerequisites
- Python 3.11+
- OpenAI API key
- GitHub personal access token

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/gpt-reviewer.git
cd gpt-reviewer

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_key"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER="123"
export COMMIT_ID="abc123"

# Run locally
python main.py
```
