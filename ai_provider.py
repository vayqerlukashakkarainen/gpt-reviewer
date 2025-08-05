from abc import abstractmethod
from openai import OpenAI
import anthropic

system_message = "You are a helpful senior software engineer reviewing code diffs. You follow the project rules direct and without stray."
temperature = 0.2

class AIProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        
    @abstractmethod
    def init_client(self):
        pass
    
    @abstractmethod
    def get_review(self, rules, filename, patch):
        pass
        
class OpenAIProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.client = self.init_client()
        
    def init_client(self):
        return OpenAI(api_key=super.api_key)
    
    def get_review(self, rules, filename, patch):
        prompt = build_prompt(rules, filename, patch)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    
class AnthropicAIProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.client = self.init_client()
        
    def init_client(self):
        return anthropic.Anthropic(api_key=super.api_key)
    
    def get_review(self, rules, filename, patch):
        prompt = build_prompt(rules, filename, patch)
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=temperature,
            system=system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
def build_prompt(rules, filename, patch):
    return f"""
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

        Every diff starts with its line number.
        You must only return raw JSON.
        Do not use any markdown formatting.
        Do not explain anything.
        Do not include comments or pre/post text.
        """