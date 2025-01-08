import anthropic
import re
import readline
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import sys

client = anthropic.Anthropic()
console = Console()
prompts = {
    'hello': 'Hello, Claude',
    'proofread': 'Act as an editor. Please proofread and provide suggestions for my queries',
    'pair': 'Act as a developer. Pair program with me',
    'summarize': 'Summarize the content I provide you'
}

def choose_prompt():
    table = Table(title="Prompts")
    table.add_column("Name")
    table.add_column("Description")
    for key, prompt in prompts.items():
        table.add_row(key, prompt)
    console.print(table)
    choice = Prompt.ask("🎬")
    if choice in prompts.keys():
        return prompts[choice]
    else:
        return prompts['hello']

def stream_messages(system, messages):
    return client.messages.stream(
        model="claude-3-opus-20240229",
        system=system,
        max_tokens=1024,
        messages=messages
    )

# TODO: prompt, web, add, commit, clear, run, undo

commands = [
    '/help',
    '/exit',
    '/quit'
]

def print_help():
    print("""
    /help   Display this help menu
    /exit   Quit the application
    /quit   Quit the application
    """)

def dispatch(command):
    match command:
        case '/exit'|'/quit':
            sys.exit()
        case '/help':
            print_help()
        case _:
            print('No such command!')

class Conversation:
    def __init__(self, prompt):
        self.system = prompt
        self.messages = []

    def start(self):
        while True:
            query = Prompt.ask("💬")
            if query in commands:
                dispatch(query)
            else:
                self.say(query)
                try:
                    answer = self.listen()
                    self.remember(answer)
                except anthropic.APIStatusError as err:
                    console.print("❌ API Error:", style="red")
                    console.print(err.body['error']['message'], style="red")
                    sys.exit()

    def say(self, query):
        self.messages.append({"role": "user", "content": query})

    def listen(self):
        answer = ''
        console.print("🤖:", end="")
        with stream_messages(self.system, self.messages) as stream:
            for text in stream.text_stream:
                answer += text
                console.print(text, style="blue", end="")
            console.print()
        return answer

    def remember(self, answer):
        self.messages.append({"role": "assistant", "content": answer})
        if len(self.messages) >= 7:
            self.messages = self.messages[2:]

if __name__ == "__main__":
    try:
        prompt = choose_prompt()
        choice = Text(prompt)
        console.print(Panel(choice, title="Prompt"))
        conv = Conversation(prompt)
        conv.start()
    except KeyboardInterrupt:
        console.print("❌ KeyboardInterrupt: Exiting", style="red")
        sys.exit()
