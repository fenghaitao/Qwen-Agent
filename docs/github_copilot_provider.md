# GitHub Copilot LLM Provider

This module provides integration with GitHub Copilot models through LiteLLM in direct mode for the Qwen-Agent framework.

## Features

- ✅ Direct GitHub Copilot API access via LiteLLM
- ✅ Function calling support
- ✅ Streaming and non-streaming responses
- ✅ Automatic provider detection
- ✅ Full compatibility with Qwen-Agent framework

## Prerequisites

### 1. Install LiteLLM
```bash
pip install litellm
```

### 2. GitHub Token Setup
You need a GitHub token with Copilot access. Get one from [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens).

Set the token either:
- Environment variable: `export GITHUB_TOKEN=your_token_here`
- Configuration parameter: `github_token='your_token_here'`

### 3. GitHub Copilot Access
Ensure you have access to GitHub Copilot (requires subscription or organization access).

## Supported Models

- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-3.5-turbo`
- Other GitHub Copilot supported models

## Usage Examples

### Basic Usage

```python
from qwen_agent.llm import get_chat_model

# Explicit configuration
llm_cfg = {
    'model': 'gpt-4o-mini',
    'model_type': 'github_copilot',
    'github_token': 'your_github_token',  # or set GITHUB_TOKEN env var
    'generate_cfg': {
        'max_tokens': 1000,
        'temperature': 0.7
    }
}

llm = get_chat_model(llm_cfg)
messages = [{'role': 'user', 'content': 'Hello! Write a Python function to sort a list.'}]

for response in llm.chat(messages=messages, stream=True):
    print(response)
```

### Auto-Detection

If `GITHUB_TOKEN` is set and model name contains `gpt-4o` or `copilot`, the provider will be auto-detected:

```python
# Auto-detection when GITHUB_TOKEN is available
llm_cfg = {
    'model': 'gpt-4o-mini',  # Auto-detects github_copilot provider
    'generate_cfg': {
        'max_tokens': 500,
        'temperature': 0.5
    }
}

llm = get_chat_model(llm_cfg)
```

### With Qwen-Agent Assistant

```python
from qwen_agent.agents import Assistant

llm_cfg = {
    'model': 'gpt-4o-mini',
    'model_type': 'github_copilot',
    'generate_cfg': {
        'max_tokens': 1000,
        'temperature': 0.3
    }
}

bot = Assistant(
    llm=llm_cfg,
    function_list=['code_interpreter'],  # Built-in tools
    name='Copilot Assistant',
    description='AI assistant powered by GitHub Copilot'
)

messages = [{'role': 'user', 'content': 'Create a data visualization of sales trends'}]
for response in bot.run(messages=messages):
    print(response)
```

### Function Calling

The provider supports function calling out of the box:

```python
llm_cfg = {
    'model': 'gpt-4o-mini',
    'model_type': 'github_copilot'
}

llm = get_chat_model(llm_cfg)

functions = [{
    'name': 'get_weather',
    'description': 'Get weather information for a location',
    'parameters': {
        'type': 'object',
        'properties': {
            'location': {'type': 'string', 'description': 'City name'}
        },
        'required': ['location']
    }
}]

messages = [{'role': 'user', 'content': 'What is the weather in San Francisco?'}]

for response in llm.chat(messages=messages, functions=functions, stream=True):
    print(response)
```

## Configuration Options

### Core Parameters

- `model`: Model name (default: 'gpt-4o-mini')
- `model_type`: Must be 'github_copilot'
- `github_token`: GitHub token (or use GITHUB_TOKEN env var)

### Generation Parameters

All standard LiteLLM parameters are supported in `generate_cfg`:

- `max_tokens`: Maximum tokens to generate
- `temperature`: Sampling temperature (0.0 to 2.0)
- `top_p`: Nucleus sampling parameter
- `frequency_penalty`: Frequency penalty
- `presence_penalty`: Presence penalty
- `stop`: Stop sequences
- `timeout`: Request timeout in seconds

### Example Full Configuration

```python
llm_cfg = {
    'model': 'gpt-4o-mini',
    'model_type': 'github_copilot',
    'github_token': os.getenv('GITHUB_TOKEN'),
    'verbose': False,  # LiteLLM verbose logging
    'generate_cfg': {
        'max_tokens': 2000,
        'temperature': 0.7,
        'top_p': 0.9,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1,
        'stop': ['\\n\\n'],
        'timeout': 30
    }
}
```

## Error Handling

The provider handles common error scenarios:

### Missing GitHub Token
```
ValueError: GitHub token is required for GitHub Copilot provider. 
Please set 'github_token' in config or 'GITHUB_TOKEN' environment variable.
You can get a GitHub token from: https://github.com/settings/tokens
```

### Missing LiteLLM
```
ImportError: LiteLLM is required for GitHub Copilot provider. 
Please install it with 'pip install litellm'
```

### API Errors
All GitHub Copilot API errors are wrapped in `ModelServiceError` for consistent error handling across Qwen-Agent.

## Troubleshooting

### 1. Authentication Issues
- Verify your GitHub token has Copilot access
- Check token permissions and expiration
- Ensure token is properly set in environment or config

### 2. Model Access Issues
- Verify you have GitHub Copilot subscription
- Check if the model is available in your region
- Try different model names (gpt-4o-mini, gpt-4o, etc.)

### 3. LiteLLM Issues
- Update LiteLLM: `pip install -U litellm`
- Check LiteLLM documentation for GitHub Copilot support
- Enable verbose logging: `verbose=True` in config

## Integration Notes

This provider:
- Inherits from `BaseFnCallModel` for function calling support
- Uses LiteLLM's direct mode (not proxy)
- Supports all Qwen-Agent features (RAG, tools, multi-agent, etc.)
- Maintains compatibility with existing Qwen-Agent applications
- Handles multimodal input preprocessing
- Supports streaming and non-streaming responses

## Example Output

Running the example:

```bash
$ python examples/github_copilot_example.py

✅ LiteLLM is available
🚀 Starting GitHub Copilot LLM Provider Tests

=== Testing Direct LLM Usage ===
LLM Response: [Message(role='assistant', content='I'd be happy to help you write a Python function to calculate factorial! Here's a simple implementation: ...')]

=== Testing GitHub Copilot with Tools ===
Bot Response: [Message(role='assistant', content='I'll help you create a Python script to generate and plot the first 10 Fibonacci numbers. Let me write and execute the code for you.'), Message(role='assistant', function_call=FunctionCall(name='code_interpreter', arguments='{"code": "# Generate first 10 Fibonacci numbers\\ndef fibonacci(n):\\n    fib_sequence = []\\n    a, b = 0, 1\\n    for _ in range(n):\\n        fib_sequence.append(a)\\n        a, b = b, a + b\\n    return fib_sequence\\n\\n# Generate first 10 Fibonacci numbers\\nfib_numbers = fibonacci(10)\\nprint(\\"First 10 Fibonacci numbers:\\", fib_numbers)\\n\\n# Plot them\\nimport matplotlib.pyplot as plt\\n\\nplt.figure(figsize=(10, 6))\\nplt.plot(range(len(fib_numbers)), fib_numbers, 'bo-', linewidth=2, markersize=8)\\nplt.title('First 10 Fibonacci Numbers', fontsize=16)\\nplt.xlabel('Index', fontsize=12)\\nplt.ylabel('Fibonacci Value', fontsize=2)\\nplt.grid(True, alpha=0.3)\\nplt.xticks(range(len(fib_numbers)))\\nplt.show()"}'))]

✅ All tests completed successfully!
```