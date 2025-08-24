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
import os
from pprint import pformat
from typing import Dict, Iterator, List, Optional

from qwen_agent.llm.base import ModelServiceError, register_llm
from qwen_agent.llm.function_calling import BaseFnCallModel
from qwen_agent.llm.schema import ASSISTANT, FunctionCall, Message
from qwen_agent.log import logger
from qwen_agent.utils.utils import format_as_text_message

# Conditional import for type checking
try:
    import litellm
except ImportError:
    litellm = None  # Will be handled in __init__


@register_llm('github_copilot')
class GitHubCopilotChat(BaseFnCallModel):
    """GitHub Copilot LLM provider using LiteLLM in direct mode
    
    This provider enables access to GitHub Copilot models through LiteLLM.
    
    Supported models:
    - gpt-4o-mini
    - gpt-4o 
    - gpt-3.5-turbo
    - And other GitHub Copilot supported models
    
    Configuration example:
        llm_cfg = {
            'model': 'gpt-4o-mini',
            'model_type': 'github_copilot',
            'github_token': 'your_github_token',  # or set GITHUB_TOKEN env var
            'generate_cfg': {
                'max_tokens': 1000,
                'temperature': 0.7
            }
        }
    
    Requirements:
    - LiteLLM package: pip install litellm
    - GitHub token with Copilot access
    """

    def __init__(self, cfg: Optional[Dict] = None):
        super().__init__(cfg)
        
        # Set default model if not specified
        self.model = self.model or 'gpt-4o-mini'
        cfg = cfg or {}

        # GitHub Copilot token
        github_token = cfg.get('github_token')
        github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError(
                "GitHub token is required for GitHub Copilot provider. "
                "Please set 'github_token' in config or 'GITHUB_TOKEN' environment variable.\n"
                "You can get a GitHub token from: https://github.com/settings/tokens"
            )

        # Import LiteLLM
        try:
            import litellm
            self.litellm = litellm
        except ImportError as e:
            raise ImportError(
                "LiteLLM is required for GitHub Copilot provider. "
                "Please install it with 'pip install litellm'"
            ) from e

        # Set up LiteLLM configuration for GitHub Copilot
        self.litellm.set_verbose = cfg.get('verbose', False)
        
        # Configure GitHub Copilot credentials for LiteLLM
        os.environ['GITHUB_TOKEN'] = github_token
        
        # Store configuration
        self.github_token = github_token
        
        logger.info(f"Initialized GitHub Copilot LLM provider using model: {self.model}")

    def _chat_stream(
        self,
        messages: List[Message],
        delta_stream: bool,
        generate_cfg: dict,
    ) -> Iterator[List[Message]]:
        """Handle streaming chat responses"""
        messages_dict = self.convert_messages_to_dicts(messages)
        logger.debug(f'LLM Input generate_cfg: \n{generate_cfg}')
        
        try:
            # Prepare LiteLLM parameters
            litellm_params = self._prepare_litellm_params(generate_cfg)
            
            # Add tools if present
            if 'tools' in generate_cfg:
                litellm_params['tools'] = generate_cfg['tools']
            
            response = self.litellm.completion(
                model=f"github/{self.model}",
                messages=messages_dict,
                stream=True,
                **litellm_params
            )
            
            if delta_stream:
                for chunk in response:
                    if chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield [Message(role=ASSISTANT, content=delta.content)]
            else:
                full_response = ''
                full_tool_calls = []
                
                for chunk in response:
                    if chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            full_response += delta.content
                        if hasattr(delta, 'tool_calls') and delta.tool_calls:
                            for tc in delta.tool_calls:
                                # Handle tool call accumulation
                                if full_tool_calls and hasattr(tc, 'id') and tc.id:
                                    # Find existing tool call with same ID
                                    existing_call = None
                                    for existing in full_tool_calls:
                                        if existing.extra.get('function_id') == tc.id:
                                            existing_call = existing
                                            break
                                    
                                    if existing_call:
                                        # Append to existing call
                                        if hasattr(tc, 'function') and tc.function:
                                            if hasattr(tc.function, 'name') and tc.function.name:
                                                existing_call.function_call.name += tc.function.name
                                            if hasattr(tc.function, 'arguments') and tc.function.arguments:
                                                existing_call.function_call.arguments += tc.function.arguments
                                    else:
                                        # Create new tool call
                                        if hasattr(tc, 'function') and tc.function:
                                            full_tool_calls.append(
                                                Message(
                                                    role=ASSISTANT,
                                                    content='',
                                                    function_call=FunctionCall(
                                                        name=getattr(tc.function, 'name', '') or '',
                                                        arguments=getattr(tc.function, 'arguments', '') or ''
                                                    ),
                                                    extra={'function_id': tc.id}
                                                )
                                            )
                                else:
                                    # Create new tool call without ID
                                    if hasattr(tc, 'function') and tc.function:
                                        full_tool_calls.append(
                                            Message(
                                                role=ASSISTANT,
                                                content='',
                                                function_call=FunctionCall(
                                                    name=getattr(tc.function, 'name', '') or '',
                                                    arguments=getattr(tc.function, 'arguments', '') or ''
                                                ),
                                                extra={'function_id': getattr(tc, 'id', str(len(full_tool_calls) + 1))}
                                            )
                                        )
                        
                        # Yield current state
                        res = []
                        if full_response:
                            res.append(Message(role=ASSISTANT, content=full_response))
                        if full_tool_calls:
                            res.extend(full_tool_calls)
                        if res:  # Only yield if we have content
                            yield res
                        
        except Exception as ex:
            logger.error(f"GitHub Copilot API error: {ex}")
            raise ModelServiceError(exception=ex)

    def _chat_no_stream(
        self,
        messages: List[Message],
        generate_cfg: dict,
    ) -> List[Message]:
        """Handle non-streaming chat responses"""
        messages_dict = self.convert_messages_to_dicts(messages)
        
        try:
            # Prepare LiteLLM parameters
            litellm_params = self._prepare_litellm_params(generate_cfg)
            
            # Add tools if present
            if 'tools' in generate_cfg:
                litellm_params['tools'] = generate_cfg['tools']
            
            response = self.litellm.completion(
                model=f"github/{self.model}",
                messages=messages_dict,
                stream=False,
                **litellm_params
            )
            
            # Handle function calls in response
            message = response.choices[0].message
            result = []
            
            if hasattr(message, 'content') and message.content:
                result.append(Message(role=ASSISTANT, content=message.content))
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tc in message.tool_calls:
                    if hasattr(tc, 'function') and tc.function:
                        result.append(
                            Message(
                                role=ASSISTANT,
                                content='',
                                function_call=FunctionCall(
                                    name=getattr(tc.function, 'name', '') or '',
                                    arguments=getattr(tc.function, 'arguments', '') or ''
                                ),
                                extra={'function_id': getattr(tc, 'id', '1')}
                            )
                        )
            
            # If no content or tool calls, return default message
            if not result:
                result = [Message(role=ASSISTANT, content=message.content or '')]
                
            return result
            
        except Exception as ex:
            logger.error(f"GitHub Copilot API error: {ex}")
            raise ModelServiceError(exception=ex)

    def _prepare_litellm_params(self, generate_cfg: dict) -> dict:
        """Prepare parameters for LiteLLM completion call"""
        litellm_params = copy.deepcopy(generate_cfg)
        
        # Remove Qwen-Agent specific parameters that LiteLLM doesn't understand
        qwen_agent_params = [
            'lang', 'parallel_function_calls', 'function_choice', 'thought_in_content',
            'max_input_tokens', 'skip_stopword_postproc', 'use_raw_api'
        ]
        for param in qwen_agent_params:
            litellm_params.pop(param, None)
        
        # Map common parameters
        if 'request_timeout' in litellm_params:
            litellm_params['timeout'] = litellm_params.pop('request_timeout')
        
        return litellm_params

    def convert_messages_to_dicts(self, messages: List[Message]) -> List[dict]:
        """Convert Message objects to dictionaries for LiteLLM"""
        formatted_messages = [format_as_text_message(msg, add_upload_info=False) for msg in messages]
        dict_messages = [msg.model_dump() for msg in formatted_messages]
        # Type cast to satisfy the static type checker
        oai_messages = self._conv_qwen_agent_messages_to_oai(dict_messages)  # type: ignore

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f'LLM Input: \n{pformat(oai_messages, indent=2)}')
        return oai_messages

    @property
    def support_multimodal_input(self) -> bool:
        """GitHub Copilot models support multimodal input"""
        return True

    @property
    def support_multimodal_output(self) -> bool:
        """GitHub Copilot models generate text output"""
        return False

    @property
    def support_audio_input(self) -> bool:
        """GitHub Copilot models don't support audio input"""
        return False