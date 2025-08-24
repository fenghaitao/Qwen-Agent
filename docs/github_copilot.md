# GitHub Copilot Provider for Qwen Agent

This document explains how to use GitHub Copilot as an LLM provider in Qwen Agent through the LiteLLM library.

## Overview

The GitHub Copilot provider allows you to use GitHub Copilot's language models within the Qwen Agent framework. This integration uses LiteLLM in direct mode to communicate with GitHub Copilot's API.

## Prerequisites

1. **GitHub Copilot Subscription**: You need an active GitHub Copilot subscription
2. **LiteLLM**: The `litellm` package (automatically installed with qwen-agent)

## Setup

### 1. Authentication

GitHub Copilot uses OAuth2 authentication through LiteLLM. No manual token setup is required - LiteLLM handles the authentication flow automatically when you first use the service.

### 2. Installation

The GitHub Copilot provider is included with qwen-agent. LiteLLM is automatically installed as a dependency.

```bash
pip install qwen-agent
```

## Usage

### Basic Configuration

```python
from qwen_agent.llm import get_chat_model

# Method 1: Using model string (simplest)
llm = get_chat_model('github_copilot/gpt-4o')

# Method 2: Using configuration dictionary
cfg = {
    'model': 'github_copilot/gpt-4o',
    'model_type': 'github_copilot',
    # No API key needed - OAuth2 authentication handled automatically
    'generate_cfg': {
        'max_tokens': 1000,
        'temperature': 0.7,
    }
}
llm = get_chat_model(cfg)
```

### Available Models

GitHub Copilot supports several models through LiteLLM:

- `github_copilot/gpt-4o` - GPT-4o model
- `github_copilot/gpt-4.1` - GPT-4.1 model
- `github_copilot/gpt-5` - GPT-5 model
- `github_copilot/gpt-5-mini` - GPT-5 mini model

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model` | The model name (e.g., 'github_copilot/gpt-4o') | 'github_copilot/gpt-4o' |
| `api_key` | Optional API key (OAuth2 used by default) | None |
| `editor_version` | Editor version for IDE authentication | 'vscode/1.85.0' |
| `copilot_integration_id` | Copilot integration identifier | 'vscode-chat' |
| `extra_headers` | Additional headers to include in requests | None |
| `base_url` | Custom API base URL (optional) | None |
| `timeout` | Request timeout in seconds | None |
| `verbose` | Enable verbose logging | False |

### IDE Authentication Headers

GitHub Copilot requires specific headers to identify the IDE/editor making the request. The provider automatically includes the required headers with sensible defaults:

```python
# Default headers (automatically included)
headers = {
    'Editor-Version': 'vscode/1.85.0',
    'Copilot-Integration-Id': 'vscode-chat'
}

# Custom IDE configuration
cfg = {
    'model': 'github_copilot/gpt-4o',
    'model_type': 'github_copilot',
    'editor_version': 'vscode/1.90.0',  # Custom VS Code version
    'copilot_integration_id': 'vscode-chat',  # Integration type
    'extra_headers': {
        'Custom-Header': 'custom-value'  # Additional headers if needed
    }
}
```

### Generation Configuration

You can control the model's behavior using the `generate_cfg` parameter:

```python
cfg = {
    'model': 'github_copilot/gpt-4o',
    'model_type': 'github_copilot',
    'generate_cfg': {
        'max_tokens': 2000,
        'temperature': 0.3,
        'top_p': 0.9,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'stop': ['###', 'END'],
    }
}
```

## Examples

### 1. Simple Chat

```python
from qwen_agent.llm import get_chat_model

llm = get_chat_model('github_copilot/gpt-4o')
response = llm.quick_chat("Write a Python function to sort a list.")
print(response)
```

### 2. Streaming Chat

```python
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message

llm = get_chat_model('github_copilot/gpt-4o')
messages = [Message(role='user', content='Explain quantum computing.')]

for response in llm.chat(messages=messages, stream=True):
    if response and response[0].content:
        print(response[0].content, end='', flush=True)
```

### 3. Function Calling

```python
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message

# Define functions
functions = [
    {
        'name': 'calculate',
        'description': 'Perform mathematical calculations',
        'parameters': {
            'type': 'object',
            'properties': {
                'expression': {
                    'type': 'string',
                    'description': 'Mathematical expression to evaluate'
                }
            },
            'required': ['expression']
        }
    }
]

llm = get_chat_model('github_copilot/gpt-4o')
messages = [Message(role='user', content='What is 15 * 23?')]

for response in llm.chat(messages=messages, functions=functions, stream=True):
    for msg in response:
        if msg.content:
            print(msg.content)
        if hasattr(msg, 'function_call') and msg.function_call:
            print(f"Function call: {msg.function_call.name}({msg.function_call.arguments})")
```

### 4. Multi-turn Conversation

```python
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message

llm = get_chat_model('github_copilot/gpt-4o')

messages = [
    Message(role='user', content='Hello, I need help with Python.'),
    Message(role='assistant', content='Hello! I\'d be happy to help you with Python. What specific topic or problem would you like assistance with?'),
    Message(role='user', content='How do I read a CSV file?')
]

for response in llm.chat(messages=messages, stream=True):
    if response and response[0].content:
        print(response[0].content, end='', flush=True)
```

## Error Handling

The provider includes comprehensive error handling:

```python
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.base import ModelServiceError

try:
    llm = get_chat_model('github_copilot/gpt-4o')
    response = llm.quick_chat("Hello!")
    print(response)
except ModelServiceError as e:
    print(f"Model service error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Authentication**: OAuth2 is handled automatically by LiteLLM - no manual token management needed
2. **Rate Limiting**: Be aware of GitHub Copilot's rate limits and implement appropriate retry logic
3. **Model Selection**: Choose the appropriate model based on your use case:
   - `gpt-4o` for complex reasoning tasks
   - `gpt-4o-mini` for faster, simpler tasks
4. **Temperature Settings**: Use lower temperatures (0.1-0.3) for code generation, higher (0.7-0.9) for creative tasks
5. **Error Handling**: Always implement proper error handling for production use

## Troubleshooting

### Common Issues

1. **Authentication Error**: OAuth2 authentication is handled by LiteLLM automatically. Ensure you have a valid GitHub Copilot subscription
2. **Missing Editor-Version Header**: If you get "missing Editor-Version header" error, the provider automatically includes required headers. Check your LiteLLM version
3. **Model Not Found**: Verify the model name format (e.g., 'github_copilot/gpt-4o')
4. **Rate Limiting**: Implement exponential backoff for rate limit errors
5. **Import Error**: Ensure LiteLLM is installed: `pip install litellm`
6. **OAuth2 Flow**: On first use, LiteLLM may prompt for authentication - follow the OAuth2 flow in your browser
7. **IDE Headers**: The provider automatically includes `Editor-Version` and `Copilot-Integration-Id` headers. You can customize these if needed

### Debug Mode

Enable verbose logging to debug issues:

```python
cfg = {
    'model': 'github_copilot/gpt-4o',
    'model_type': 'github_copilot',
    'verbose': True,
}
```

## Integration with Qwen Agent Features

The GitHub Copilot provider is fully compatible with all Qwen Agent features:

- **Agents**: Use with any Qwen Agent (Assistant, ReactChat, etc.)
- **Tools**: Full function calling support
- **RAG**: Compatible with retrieval-augmented generation
- **Multi-agent**: Works in multi-agent scenarios
- **Streaming**: Full streaming support
- **Memory**: Compatible with conversation memory

Example with Assistant agent:

```python
from qwen_agent.agents import Assistant

# Create assistant with GitHub Copilot
assistant = Assistant(
    llm={
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot',
    }
)

response = assistant.run("Help me write a web scraper in Python.")
print(response)
```

## Limitations

1. **Model Availability**: Limited to models supported by GitHub Copilot
2. **Rate Limits**: Subject to GitHub Copilot's rate limiting
3. **Subscription Required**: Requires active GitHub Copilot subscription
4. **Network Dependency**: Requires internet connection for API calls

## Support

For issues specific to the GitHub Copilot provider, please check:

1. [Qwen Agent GitHub Issues](https://github.com/QwenLM/Qwen-Agent/issues)
2. [LiteLLM Documentation](https://docs.litellm.ai/)
3. [GitHub Copilot Documentation](https://docs.github.com/en/copilot)