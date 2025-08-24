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

import copy
import logging
from pprint import pformat
from typing import Dict, Iterator, List, Optional

try:
    import litellm
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    litellm = None
    completion = None
    LITELLM_AVAILABLE = False

from qwen_agent.utils.utils import format_as_text_message
from qwen_agent.llm.base import ModelServiceError, register_llm
from qwen_agent.llm.function_calling import BaseFnCallModel
from qwen_agent.llm.schema import ASSISTANT, FunctionCall, Message
from qwen_agent.log import logger


@register_llm('github_copilot')
class GitHubCopilotChat(BaseFnCallModel):
    """GitHub Copilot provider using LiteLLM in direct mode."""

    def __init__(self, cfg: Optional[Dict] = None):
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM is required for GitHub Copilot provider. Please install it with: pip install litellm")
        
        super().__init__(cfg)
        cfg = cfg or {}
        
        # Default model for GitHub Copilot
        self.model = self.model or 'github_copilot/gpt-4.1'
        
        # Set up LiteLLM configuration for GitHub Copilot
        litellm.set_verbose = cfg.get('verbose', False)
        
        # Configure GitHub Copilot specific settings
        # GitHub Copilot uses OAuth2 authentication through LiteLLM
        self.copilot_config = {
            'custom_llm_provider': 'github_copilot',
        }
        
        # Required headers for GitHub Copilot IDE authentication
        editor_version = cfg.get('editor_version', 'vscode/1.85.0')
        copilot_integration_id = cfg.get('copilot_integration_id', 'vscode-chat')
        
        self.copilot_config['extra_headers'] = {
            'Editor-Version': editor_version,
            'Copilot-Integration-Id': copilot_integration_id,
        }
        
        # Additional configuration from cfg
        if 'timeout' in cfg:
            self.copilot_config['timeout'] = cfg['timeout']
        
        # Merge any additional extra headers from config
        if 'extra_headers' in cfg:
            self.copilot_config['extra_headers'].update(cfg['extra_headers'])

    def _chat_stream(
        self,
        messages: List[Message],
        delta_stream: bool,
        generate_cfg: dict,
    ) -> Iterator[List[Message]]:
        messages = self.convert_messages_to_dicts(messages)
        logger.debug(f'LLM Input generate_cfg: \n{generate_cfg}')
        
        # Prepare LiteLLM parameters
        litellm_params = {
            'model': self.model,
            'messages': messages,
            'stream': True,
            **self.copilot_config,
            **generate_cfg
        }
        
        try:
            response = completion(**litellm_params)
            
            if delta_stream:
                for chunk in response:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            yield [
                                Message(role=ASSISTANT,
                                       content='',
                                       reasoning_content=delta.reasoning_content)
                            ]
                        if hasattr(delta, 'content') and delta.content:
                            yield [Message(role=ASSISTANT, content=delta.content)]
            else:
                full_response = ''
                full_reasoning_content = ''
                full_tool_calls = []
                
                for chunk in response:
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            full_reasoning_content += delta.reasoning_content
                        if hasattr(delta, 'content') and delta.content:
                            full_response += delta.content
                        if hasattr(delta, 'tool_calls') and delta.tool_calls:
                            for tc in delta.tool_calls:
                                if full_tool_calls and (not tc.id or 
                                                       tc.id == full_tool_calls[-1]['extra']['function_id']):
                                    if tc.function.name:
                                        full_tool_calls[-1].function_call['name'] += tc.function.name
                                    if tc.function.arguments:
                                        full_tool_calls[-1].function_call['arguments'] += tc.function.arguments
                                else:
                                    full_tool_calls.append(
                                        Message(role=ASSISTANT,
                                               content='',
                                               function_call=FunctionCall(name=tc.function.name,
                                                                         arguments=tc.function.arguments),
                                               extra={'function_id': tc.id}))

                        res = []
                        if full_reasoning_content:
                            res.append(Message(role=ASSISTANT, content='', reasoning_content=full_reasoning_content))
                        if full_response:
                            res.append(Message(role=ASSISTANT, content=full_response))
                        if full_tool_calls:
                            res += full_tool_calls
                        yield res
                        
        except Exception as ex:
            raise ModelServiceError(exception=ex)

    def _chat_no_stream(
        self,
        messages: List[Message],
        generate_cfg: dict,
    ) -> List[Message]:
        messages = self.convert_messages_to_dicts(messages)
        
        # Prepare LiteLLM parameters
        litellm_params = {
            'model': self.model,
            'messages': messages,
            'stream': False,
            **self.copilot_config,
            **generate_cfg
        }
        
        try:
            response = completion(**litellm_params)
            message = response.choices[0].message
            
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                return [
                    Message(role=ASSISTANT,
                           content=message.content or '',
                           reasoning_content=message.reasoning_content)
                ]
            else:
                return [Message(role=ASSISTANT, content=message.content or '')]
                
        except Exception as ex:
            raise ModelServiceError(exception=ex)

    def convert_messages_to_dicts(self, messages: List[Message]) -> List[dict]:
        """Convert Qwen Agent messages to OpenAI format for LiteLLM."""
        messages = [format_as_text_message(msg, add_upload_info=False) for msg in messages]
        messages = [msg.model_dump() for msg in messages]
        messages = self._conv_qwen_agent_messages_to_oai(messages)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'LLM Input: \n{pformat(messages, indent=2)}')
        return messages