import os
import requests
from openai import OpenAI

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
PR_NUMBER = os.environ["PR_NUMBER"]
COMMIT_ID = os.environ["COMMIT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)


ignored_files = [".project-rules.md"]

def get_pr_files():
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}/files"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def load_rules():
    with open(".project-rules.md", "r") as f:
        return f.read()

def get_ai_review(rules, filename, patch):
    prompt = f"""
        You are a strict code reviewer. Below are the project rules:

        {rules}

        Here is a code diff for the file `{filename}`:

        ```
        {patch}
        ```

        Identify any rule violations based on the provided rules. For each one, return only a JSON like:
        [
        {{
            "line": <line number in the diff>,
            "comment": "<suggestion or warning>"
        }},
        ...
        ]

        You must only return raw JSON.
        Do not use any markdown formatting.
        Do not explain anything.
        Do not include comments or pre/post text.
        """
        
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

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
        
def get_pr_additions_only(files):
    additions_by_file = {}

    for file in files:
        if file.get("patch") is None:
            continue
        
        patch = file["patch"]
        filename = file["filename"]
        
        additions = [
            line for line in patch.splitlines(True)
            if line.startswith("+")
        ]
        
        add_str = "".join(additions)
        
        if additions:
            additions_by_file[filename] = add_str

    return additions_by_file

def ignore_file(file_name):
    return file_name in ignored_files

def main():
    rules = load_rules()
    files = get_pr_files()
    additions = get_pr_additions_only(files)

    for file in files:
        if file.get("patch") is None:
            continue

        file_path = file["filename"]
        filename = os.path.basename(file_path)
        
        if ignore_file(filename):
            continue
        
        patch = additions[file_path]

        ai_output = get_ai_review(rules, file_path, patch)
        clean_ai_output = ai_output.replace("```json", "").replace("```", "").strip()

        try:
            import json
            suggestions = json.loads(clean_ai_output)
            for suggestion in suggestions:
                print(f"👉 Posting suggestion {suggestion}")
                post_inline_comment(suggestion["comment"], file_path, suggestion["line"])
        except Exception as e:
            print(f"⚠️ Could not parse suggestions for {file_path}: {e}\nAI Output:\n{ai_output}")
            print(f"⚠️ Cleaned:\n{clean_ai_output}")

if __name__ == "__main__":
    main()
