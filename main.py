import os
import json
import requests
import fnmatch
from unidiff import PatchSet
from ai_provider import AnthropicAIProvider, OpenAIProvider

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]
COMMIT_ID = os.environ["COMMIT_ID"]
AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai").lower()
AI_API_KEY = os.environ["AI_API_KEY"]

ignored_files = [".project-rules.md"]

def load_ignore_patterns():
    ignore_patterns = []
    ignore_file_path = ".ignore"
    
    if os.path.exists(ignore_file_path):
        try:
            with open(ignore_file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith("#"):
                        ignore_patterns.append(line)
            print(f"✅ Loaded {len(ignore_patterns)} ignore patterns from ignore file")
        except Exception as e:
            print(f"⚠️ Error reading ignore file: {e}")
    
    return ignore_patterns

def get_unified_diff():
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text

def load_rules():
    with open(".project-rules.md", "r") as f:
        return f.read()

def get_ai_review(rules, filename, patch, ai_provider):
    match ai_provider:
        case "openai":
            provider = OpenAIProvider(AI_API_KEY)
            return provider.get_review(rules, filename, patch)
        case "antrophic":
            provider = AnthropicAIProvider(AI_API_KEY)
            return provider.get_review(rules, filename, patch)
        case _:
            raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")

def post_inline_comment(comment, path, line):
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "body": comment,
        "commit_id": COMMIT_ID,
        "path": path,
        "line": line
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 201:
        print(f"✅ Comment posted on {path} @ {line}")
    else:
        print(f"❌ Error: {res.status_code} - {res.text}")
        
def get_pr_additions_only(diff):
    additions_by_file =  []
    patchset = PatchSet.from_string(diff)
    
    for patched_file in patchset:
        print(f"\n📄 File: {patched_file.path}")
        additions = [] 
     
        for hunk in patched_file:
            for line in hunk:
                if line.is_added:
                    additions.append(f"+ Line {line.target_line_no}: {line.value.strip()}")
        
        add_str = "".join(additions)
        
        if additions:
            additions_by_file.append({
                "patch": add_str,
                "filename": patched_file.path
            })

    return additions_by_file
    
def ignore_file(file_path, ignore_patterns):
    filename = os.path.basename(file_path)
    
    # Check hardcoded ignored files
    if filename in ignored_files:
        return True
    
    # Check against ignore patterns
    for pattern in ignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            if "/" in file_path and fnmatch.fnmatch(os.path.dirname(file_path), dir_pattern):
                return True
            if fnmatch.fnmatch(filename, dir_pattern):
                return True
        # Handle negation patterns (starting with !)
        elif pattern.startswith("!"):
            # Negation patterns override previous matches - not implemented for simplicity
            continue
        # Handle full path patterns
        elif "/" in pattern:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        # Handle filename patterns
        else:
            if fnmatch.fnmatch(filename, pattern):
                return True
    
    return False

def main():
    rules = load_rules()
    ignore_patterns = load_ignore_patterns()
    diff = get_unified_diff()
    file_additions = get_pr_additions_only(diff)

    for additions in file_additions:
        file_path = additions["filename"]
        
        if ignore_file(file_path, ignore_patterns):
            print(f"⏭️ Skipping ignored file: {file_path}")
            continue
        
        patch = additions["patch"]

        ai_output = get_ai_review(rules, file_path, patch, AI_PROVIDER)
        clean_ai_output = ai_output.replace("```json", "").replace("```", "").strip()

        try:
            suggestions = json.loads(clean_ai_output)
            for suggestion in suggestions:
                print(f"👉 Posting suggestion {suggestion}")
                post_inline_comment(suggestion["comment"], file_path, suggestion["line"])
        except Exception as e:
            print(f"⚠️ Could not parse suggestions for {file_path}: {e}\nAI Output:\n{ai_output}")
            print(f"⚠️ Cleaned:\n{clean_ai_output}")

if __name__ == "__main__":
    main()
