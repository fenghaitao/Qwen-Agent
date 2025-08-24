# GitHub Copilot Integration with Qwen Server

This guide explains how to use GitHub Copilot as the LLM provider for qwen_server using LiteLLM direct mode.

## Prerequisites

1. **GitHub Copilot Subscription**: You need an active GitHub Copilot subscription
2. **LiteLLM Package**: Automatically installed with qwen-agent
3. **Authentication**: GitHub Copilot uses OAuth2 authentication through LiteLLM (no manual token setup required)

## Quick Start

### Basic Usage

To run qwen_server with GitHub Copilot using default settings:

```bash
python run_server.py --model_server github_copilot --llm github_copilot/gpt-4o
```

### Advanced Configuration

For custom GitHub Copilot settings:

```bash
python run_server.py \
    --model_server github_copilot \
    --llm github_copilot/gpt-4o \
    --copilot_integration_id vscode-chat \
    --editor_version vscode/1.90.0 \
    --max_ref_token 5000
```

## Available Models

GitHub Copilot supports the following models through LiteLLM:

- `github_copilot/gpt-4o` - GPT-4o model (recommended)
- `github_copilot/gpt-4o-mini` - GPT-4o mini model
- `github_copilot/gpt-4` - GPT-4 model
- `github_copilot/gpt-3.5-turbo` - GPT-3.5 Turbo model

## Command Line Arguments

### GitHub Copilot Specific Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--model_server` | Set to `github_copilot` to use GitHub Copilot | `dashscope` | Yes |
| `--llm` | GitHub Copilot model name | `qwen-plus` | Yes |
| `--copilot_integration_id` | Copilot integration identifier | `vscode-chat` | No |
| `--editor_version` | Editor version for authentication | `vscode/1.85.0` | No |

### General Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--api_key` | Not required for GitHub Copilot (OAuth2) | `""` | No |
| `--server_host` | Server host address | `127.0.0.1` | No |
| `--max_ref_token` | Tokens for RAG reference materials | `4000` | No |
| `--workstation_port` | Creative writing workstation port | `7864` | No |

## Configuration Examples

### Example 1: Basic GitHub Copilot Setup

```bash
python run_server.py \
    --model_server github_copilot \
    --llm github_copilot/gpt-4o
```

This will start the qwen_server with:
- GitHub Copilot as the LLM provider
- GPT-4o model
- Default integration settings
- OAuth2 authentication (handled automatically)

### Example 2: Custom Integration Settings

```bash
python run_server.py \
    --model_server github_copilot \
    --llm github_copilot/gpt-4o-mini \
    --copilot_integration_id vscode-chat \
    --editor_version vscode/1.92.0 \
    --max_ref_token 6000 \
    --server_host 0.0.0.0
```

This configuration:
- Uses the smaller GPT-4o-mini model
- Sets custom editor version
- Increases RAG token limit
- Allows external access to the server

### Example 3: Development Setup

```bash
python run_server.py \
    --model_server github_copilot \
    --llm github_copilot/gpt-4 \
    --workstation_port 8864 \
    --max_ref_token 8000
```

## Server Components

When using GitHub Copilot, all three qwen_server components will use the GitHub Copilot configuration:

1. **Assistant Server** (Port 7863): Chat interface with GitHub Copilot
2. **Database Server** (Port 7866): Content caching and management
3. **Workstation Server** (Port 7864): Document management interface

## Authentication

GitHub Copilot uses OAuth2 authentication through LiteLLM:

- **No manual token setup required**
- **Authentication is handled automatically** by LiteLLM
- **First-time usage** may prompt for GitHub authentication
- **Subsequent runs** will use cached authentication

## Configuration File

The server configuration is automatically updated in `qwen_server/server_config.json`:

```json
{
    "path": {
        "work_space_root": "workspace/",
        "download_root": "workspace/download/",
        "code_interpreter_ws": "workspace/tools/code_interpreter/"
    },
    "server": {
        "server_host": "127.0.0.1",
        "fast_api_port": 7866,
        "app_in_browser_port": 7863,
        "workstation_port": 7864,
        "model_server": "github_copilot",
        "api_key": "",
        "llm": "github_copilot/gpt-4o",
        "max_ref_token": 4000,
        "max_days": 7,
        "copilot_integration_id": "vscode-chat",
        "editor_version": "vscode/1.85.0"
    }
}
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   Error: GitHub Copilot authentication failed
   ```
   **Solution**: Ensure you have an active GitHub Copilot subscription and run the command again to trigger OAuth2 flow.

2. **LiteLLM Import Error**
   ```
   ImportError: LiteLLM is required for GitHub Copilot provider
   ```
   **Solution**: LiteLLM should be automatically installed with qwen-agent. If not, install manually:
   ```bash
   pip install litellm
   ```

3. **Model Not Found**
   ```
   Error: Model 'github_copilot/gpt-4o' not found
   ```
   **Solution**: Verify the model name format and ensure you have access to the specified model.

4. **Connection Issues**
   ```
   Error: Failed to connect to GitHub Copilot service
   ```
   **Solution**: Check your internet connection and GitHub Copilot service status.

### Debug Mode

To enable verbose logging for troubleshooting:

```bash
export LITELLM_LOG=DEBUG
python run_server.py --model_server github_copilot --llm github_copilot/gpt-4o
```

## Integration with Browser Extension

The GitHub Copilot integration works seamlessly with the qwen_server browser extension:

1. **Install the browser extension** from `browser_qwen/`
2. **Start the server** with GitHub Copilot configuration
3. **Browse web pages** and add them to your reading list
4. **Chat with GitHub Copilot** about the web content through the assistant interface

## Performance Considerations

- **Model Selection**: `gpt-4o-mini` is faster and more cost-effective for simple tasks
- **Token Limits**: Adjust `--max_ref_token` based on your document sizes and needs
- **Concurrent Users**: GitHub Copilot has rate limits; consider this for multi-user setups

## Migration from Other Providers

To switch from DashScope or OpenAI to GitHub Copilot:

1. **Stop the current server** (Ctrl+C)
2. **Restart with GitHub Copilot configuration**:
   ```bash
   python run_server.py --model_server github_copilot --llm github_copilot/gpt-4o
   ```
3. **Your workspace and history** will be preserved

## Related Documentation

- [GitHub Copilot with Qwen Agent](github_copilot.md)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Qwen Server Overview](../README.md)

## Support

For issues specific to GitHub Copilot integration:

1. Check the [troubleshooting section](#troubleshooting) above
2. Verify your GitHub Copilot subscription status
3. Review the LiteLLM documentation for advanced configuration options
4. Open an issue in the qwen-agent repository with detailed error logs