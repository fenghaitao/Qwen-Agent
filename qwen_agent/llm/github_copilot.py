# Copyright 2023 The Qwen team, Alibaba Group. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Optional

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    litellm = None
    LITELLM_AVAILABLE = False

from qwen_agent.llm.base import register_llm
from qwen_agent.llm.oai import TextChatAtOAI


@register_llm('github_copilot')
class GitHubCopilotChat(TextChatAtOAI):
    """GitHub Copilot provider using LiteLLM."""

    def __init__(self, cfg: Optional[Dict] = None):
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM is required for GitHub Copilot provider. Please install it with: pip install litellm")
        
        super().__init__(cfg)
        cfg = cfg or {}
        
        # Default model for GitHub Copilot
        self.model = self.model or 'github_copilot/gpt-4o'
        
        # Set up LiteLLM configuration for GitHub Copilot
        litellm.set_verbose = cfg.get('verbose', False)
        
        # Required headers for GitHub Copilot IDE authentication
        editor_version = cfg.get('editor_version', 'vscode/1.85.0')
        copilot_integration_id = cfg.get('copilot_integration_id', 'vscode-chat')
        
        extra_headers = {
            'Editor-Version': editor_version,
            'Copilot-Integration-Id': copilot_integration_id,
        }
        
        # Merge any additional extra headers from config
        if 'extra_headers' in cfg:
            extra_headers.update(cfg['extra_headers'])
        
        # Additional configuration
        litellm_kwargs = {
            'custom_llm_provider': 'github_copilot',
            'extra_headers': extra_headers,
        }
        
        if 'timeout' in cfg:
            litellm_kwargs['timeout'] = cfg['timeout']

        def _chat_complete_create(*args, **kwargs):
            # Merge LiteLLM-specific parameters
            kwargs.update(litellm_kwargs)
            return litellm.completion(*args, **kwargs)

        self._chat_complete_create = _chat_complete_create