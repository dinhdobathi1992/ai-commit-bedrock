#!/usr/bin/env python3
import os
import sys
import subprocess
import random
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from client import LiteLLMClient, Message
from colorama import Fore, Style, init
from config import load_config

# Initialize colorama
init()

def print_success(message: str):
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

def print_error(message: str):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def show_help():
    print("AI Commit - Generate conventional commit messages using AI")
    print("\nUsage:")
    print("\tpython main.py [options]")
    print("\nOptions:")
    print("\t-h, --help\t Show this help message")
    print("\t-a, --auto-commit\t Auto stage all changes and commit")
    print("\t-t, --auto-tag\t Auto create tag")
    print("\t-p, --auto-push\t Auto push changes")
    print("\nEnvironment variables:")
    print("\tLITELLM_API_KEY\t LiteLLM API key")
    print("\tAI_COMMIT_MODEL\t LiteLLM model, default is bedrock/anthropic.claude-3-sonnet-20240229-v1:0")
    print("\tAI_COMMIT_SYSTEM_PROMPT\t Default instruction for the assistant")

def run_git_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a git command and return exit code, stdout, and stderr."""
    process = subprocess.Popen(
        ["git"] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.strip(), stderr.strip()

def is_dirty() -> bool:
    """Check if the git repository has uncommitted changes."""
    code, _, _ = run_git_command(["status", "--porcelain"])
    return code == 0

def git_add() -> bool:
    """Stage all changes."""
    code, _, stderr = run_git_command(["add", "-A"])
    if code != 0:
        print_error(f"Error staging changes: {stderr}")
        return False
    return True

def get_diff() -> Optional[str]:
    """Get the current git diff."""
    code, stdout, stderr = run_git_command(["diff", "--cached"])
    if code != 0:
        print_error(f"Error getting diff: {stderr}")
        return None
    return stdout

def commit(message: str) -> bool:
    """Create a commit with the given message."""
    code, _, stderr = run_git_command(["commit", "-m", message])
    if code != 0:
        print_error(f"Error creating commit: {stderr}")
        return False
    return True

def push() -> bool:
    """Push changes to remote."""
    code, _, stderr = run_git_command(["push"])
    if code != 0:
        print_error(f"Error pushing changes: {stderr}")
        return False
    return True

def get_current_tag() -> Optional[str]:
    """Get the current tag."""
    code, stdout, _ = run_git_command(["describe", "--tags", "--abbrev=0"])
    return stdout if code == 0 else None

def create_tag(tag_name: str) -> bool:
    """Create a new tag."""
    code, _, stderr = run_git_command(["tag", tag_name])
    if code != 0:
        print_error(f"Error creating tag: {stderr}")
        return False
    return True

def read_user_input(prompt: str) -> str:
    """Read user input with a prompt."""
    try:
        return input(f"{prompt} ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)

def truncate_diff(diff: str, max_length: Optional[int] = None) -> str:
    """Truncate the diff to a maximum length while keeping it readable."""
    # Load config if max_length not provided
    if max_length is None:
        config = load_config()
        max_length = config.get('max_diff_length', 6000)

    if len(diff) <= max_length:
        return diff
    
    # Split the diff into lines
    lines = diff.split('\n')
    total_length = 0
    kept_lines = []
    
    for line in lines:
        if total_length + len(line) + 1 > max_length - 100:  # Leave room for truncation message
            break
        kept_lines.append(line)
        total_length += len(line) + 1  # +1 for newline
    
    truncation_message = "\n... [diff truncated due to length] ..."
    return '\n'.join(kept_lines) + truncation_message

def main():
    # Parse command line arguments
    auto_commit = False
    auto_tag = False
    auto_push = False

    for arg in sys.argv[1:]:
        if arg in ["-h", "--help"]:
            show_help()
            sys.exit(0)
        elif arg in ["-a", "--auto-commit"]:
            auto_commit = True
        elif arg in ["-t", "--auto-tag"]:
            auto_tag = True
        elif arg in ["-p", "--auto-push"]:
            auto_push = True

    # Load environment variables
    load_dotenv()

    api_key = os.getenv("LITELLM_API_KEY")
    if not api_key:
        print_error("LITELLM_API_KEY is not set")
        sys.exit(1)

    model = os.getenv("AI_COMMIT_MODEL", "bedrock/anthropic.claude-3-sonnet-20240229-v1:0")
    
    system_prompt = os.getenv("AI_COMMIT_SYSTEM_PROMPT", """You are a Git Commit Assistant specialized in writing conventional commit messages. Follow these rules:
1. Use conventional commit format: <type>(<scope>): <description>
2. Types: feat, fix, docs, style, refactor, test, chore, perf
3. Keep messages under 100 characters
4. Use imperative mood (e.g., "add" not "added")
5. Be specific but concise
6. Focus on the "what" and "why", not the "how"
7. Only respond with the commit message, nothing else
8. If unable to generate a message, respond with empty string

Example good commits:
- feat(auth): add JWT token validation
- fix(api): handle null response from user service
- refactor(db): optimize query performance
- docs(readme): update deployment instructions""")

    # Initialize the LiteLLM client
    client = LiteLLMClient(api_key, model)

    # Main loop
    while True:
        if not is_dirty():
            print("Nothing to commit, working tree clean")
            sys.exit(0)

        diff = get_diff()
        if diff:
            break

        if auto_commit:
            if not git_add():
                sys.exit(1)
            continue

        response = read_user_input("Stage all changes? (y/n):")
        if response != "y":
            sys.exit(0)

        if not git_add():
            sys.exit(1)

    # Generate commit message
    messages = [
        Message("system", system_prompt),
        Message("user", f"Write commit message for the following git diff (some parts might be truncated for length):\n\n```{truncate_diff(diff)}\n\n```")
    ]

    commit_message = client.chat_complete(messages)
    if not commit_message:
        print_error("Failed to generate commit message")
        sys.exit(1)

    print(f"\nProposed commit message: {commit_message}")
    
    if not auto_commit:
        response = read_user_input("Accept this message? (y/n):")
        if response != "y":
            sys.exit(0)

    if not commit(commit_message):
        sys.exit(1)

    success_messages = [
        "🚀 Blast off! Your commit has been launched into cyberspace!",
        "🎉 Woohoo! Your code change just joined the commit party!",
        "🍾 Pop the bubbly! That commit is now part of the code fam!",
        "💫 Magic happened! Your commit is now in the repository!",
        "🌟 Stellar work! Your commit is now among the stars!",
    ]
    print_success(random.choice(success_messages))
    print_success(f"Total tokens used: {client.total_tokens}")

    if auto_push:
        if not push():
            sys.exit(1)
        print_success("Changes pushed to remote!")

if __name__ == "__main__":
    main()
