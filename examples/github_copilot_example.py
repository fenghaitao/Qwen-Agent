#!/usr/bin/env python3
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

"""
Example of using GitHub Copilot LLM provider with Qwen-Agent

Before running this example:
1. Install LiteLLM: pip install litellm
2. Set your GitHub token: export GITHUB_TOKEN=your_github_token_here
3. Make sure you have access to GitHub Copilot

Usage:
    python examples/github_copilot_example.py
"""

import os
from qwen_agent.agents import Assistant
from qwen_agent.llm import get_chat_model


def test_github_copilot_basic():
    """Test basic GitHub Copilot functionality"""
    
    # Configure GitHub Copilot LLM
    llm_cfg = {
        'model': 'gpt-4o-mini',  # or other GitHub Copilot supported models
        'model_type': 'github_copilot',
        'github_token': os.getenv('GITHUB_TOKEN'),  # Can also be set via environment variable
        'generate_cfg': {
            'max_tokens': 1000,
            'temperature': 0.7,
        }
    }
    
    # Test direct LLM usage
    print("=== Testing Direct LLM Usage ===")
    llm = get_chat_model(llm_cfg)
    
    messages = [
        {'role': 'user', 'content': 'Hello! Can you help me write a simple Python function to calculate factorial?'}
    ]
    
    for response in llm.chat(messages=messages, stream=True):
        print("LLM Response:", response)
        break  # Just show the first response for demo


def test_github_copilot_with_tools():
    """Test GitHub Copilot with function calling"""
    
    llm_cfg = {
        'model': 'gpt-4o-mini',
        'model_type': 'github_copilot',
        'github_token': os.getenv('GITHUB_TOKEN'),
        'generate_cfg': {
            'max_tokens': 1000,
            'temperature': 0.3,
        }
    }
    
    # Create an assistant with tools
    bot = Assistant(
        llm=llm_cfg,
        function_list=['code_interpreter'],  # Built-in code interpreter tool
        name='GitHub Copilot Assistant',
        description='AI coding assistant powered by GitHub Copilot'
    )
    
    print("\\n=== Testing GitHub Copilot with Tools ===")
    messages = [
        {
            'role': 'user', 
            'content': 'Please write and execute a Python script that generates the first 10 Fibonacci numbers and plots them.'
        }
    ]
    
    response_text = ''
    for response in bot.run(messages=messages):
        if response:
            print("Bot Response:", response)
            break  # Just show the first response for demo


def test_auto_detection():
    """Test automatic GitHub Copilot provider detection"""
    
    print("\\n=== Testing Auto Detection ===")
    
    # When GITHUB_TOKEN is set and model is gpt-4o*, it should auto-detect github_copilot
    if os.getenv('GITHUB_TOKEN'):
        llm_cfg = {
            'model': 'gpt-4o-mini',  # Should auto-detect as github_copilot
            'generate_cfg': {
                'max_tokens': 500,
                'temperature': 0.5,
            }
        }
        
        llm = get_chat_model(llm_cfg)
        print(f"Auto-detected model type: {llm.model_type}")
        
        messages = [{'role': 'user', 'content': 'What programming languages do you support?'}]
        
        for response in llm.chat(messages=messages, stream=True):
            print("Auto-detected LLM Response:", response)
            break
    else:
        print("GITHUB_TOKEN not set, skipping auto-detection test")


if __name__ == '__main__':
    # Check if GitHub token is available
    if not os.getenv('GITHUB_TOKEN'):
        print("❌ GITHUB_TOKEN environment variable not set!")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token_here")
        print("You can get a GitHub token from: https://github.com/settings/tokens")
        exit(1)
    
    try:
        import litellm
        print("✅ LiteLLM is available")
    except ImportError:
        print("❌ LiteLLM not installed!")
        print("Please install it: pip install litellm")
        exit(1)
    
    print("🚀 Starting GitHub Copilot LLM Provider Tests\\n")
    
    try:
        test_github_copilot_basic()
        test_github_copilot_with_tools()
        test_auto_detection()
        
        print("\\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()