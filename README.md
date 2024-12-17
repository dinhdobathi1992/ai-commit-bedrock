[![upvote](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=382034&amp;theme=light)](https://www.producthunt.com/posts/ai-commit-2)


[![Preview](./stuff/demo.gif)](https://youtu.be/7cVU3BuNpok)

[View Demo](https://youtu.be/7cVU3BuNpok)


# AI Commit

AI Commit is a Python tool that helps you write better Git commit messages using AI. It uses the Bedrock Claude 3 model through LiteLLM proxy to generate conventional commit messages based on your code changes.

## Features

- 🤖 AI-powered commit message generation
- 📝 Follows conventional commit format
- 🔄 Interactive mode for reviewing and editing messages
- 🚀 Automatic staging, committing, and pushing
- 🏷️ Automatic tag creation
- 🎨 Colorful terminal output

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-commit-bedrock.git
cd ai-commit-bedrock
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
export LITELLM_API_KEY=your_api_key
```

Optional environment variables:
- `AI_COMMIT_MODEL`: Change the AI model (default: bedrock/anthropic.claude-3-sonnet-20240229-v1:0)
- `AI_COMMIT_SYSTEM_PROMPT`: Customize the system prompt for commit message generation

## Usage

Basic usage:
```bash
python main.py
```

Options:
- `-h, --help`: Show help message
- `-a, --auto-commit`: Automatically stage and commit changes
- `-t, --auto-tag`: Automatically create a tag
- `-p, --auto-push`: Automatically push changes

Example with all options:
```bash
python main.py -a -t -p
```

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile main.py --name ai-commit
```

The executable will be created in the `dist` directory. You can then move it to your PATH:
```bash
sudo mv dist/ai-commit /usr/local/bin/
```

## Commit Message Format

The tool generates commit messages following the conventional commit format:
```
<type>(<scope>): <description>
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding or modifying tests
- chore: Maintenance tasks
- perf: Performance improvements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

[![update](./stuff/vhs.gif)](https://twitter.com/duocdev)
