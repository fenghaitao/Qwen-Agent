#!/usr/bin/env python3
"""
Example script demonstrating how to use GitHub Copilot with Qwen Agent.

This example shows how to:
1. Configure GitHub Copilot as an LLM provider
2. Use it for basic chat functionality
3. Use it with function calling capabilities

Prerequisites:
- GitHub Copilot subscription
- litellm package installed

Setup:
GitHub Copilot uses OAuth2 authentication through LiteLLM, so no manual token setup is required.
LiteLLM will handle the authentication flow automatically.

Usage:
python examples/github_copilot_example.py
"""

import os
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message


def basic_chat_example():
    """Basic chat example with GitHub Copilot."""
    print("=== Basic Chat Example ===")
    
    # Configure GitHub Copilot
    cfg = {
        'model': 'github_copilot/gpt-4o',  # or 'github_copilot/gpt-4o-mini'
        'model_type': 'github_copilot',
        # No API key needed - LiteLLM handles OAuth2 authentication automatically
        # Required IDE headers (Editor-Version, Copilot-Integration-Id) are included automatically
        'generate_cfg': {
            'max_tokens': 1000,
            'temperature': 0.7,
        }
    }
    
    # Initialize the model
    llm = get_chat_model(cfg)
    
    # Simple chat
    messages = [
        Message(role='user', content='Hello! Can you help me write a Python function to calculate fibonacci numbers?')
    ]
    
    print("User: Hello! Can you help me write a Python function to calculate fibonacci numbers?")
    print("Assistant: ")
    
    # Handle GitHub Copilot's non-delta streaming (takes the last complete response)
    full_response = ""
    for response in llm.chat(messages=messages, stream=True):
        if response and response[0].content:
            # GitHub Copilot sends complete content each time, not deltas
            full_response = response[0].content
    
    # Display the complete response with proper formatting
    print("─" * 60)
    print(full_response)
    print("─" * 60)
    print()


def get_weather(location, unit='celsius'):
    """Mock weather function implementation."""
    # This is a mock implementation - in a real scenario, you would call a weather API
    weather_data = {
        'San Francisco': {'temp_c': 18, 'temp_f': 64, 'condition': 'Foggy'},
        'New York': {'temp_c': 22, 'temp_f': 72, 'condition': 'Sunny'},
        'London': {'temp_c': 15, 'temp_f': 59, 'condition': 'Rainy'},
        'Tokyo': {'temp_c': 25, 'temp_f': 77, 'condition': 'Clear'}
    }
    
    # Extract city name (handle "San Francisco, CA" -> "San Francisco")
    city = location.split(',')[0].strip()
    
    if city in weather_data:
        data = weather_data[city]
        temp = data['temp_c'] if unit == 'celsius' else data['temp_f']
        unit_symbol = '°C' if unit == 'celsius' else '°F'
        return f"The weather in {city} is {data['condition']} with a temperature of {temp}{unit_symbol}."
    else:
        return f"Sorry, I don't have weather information for {city}."


def function_calling_example():
    """Function calling example with GitHub Copilot."""
    print("=== Function Calling Example ===")
    
    # Configure GitHub Copilot with custom IDE headers
    cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot',
        'editor_version': 'vscode/1.90.0',  # Custom VS Code version
        'copilot_integration_id': 'vscode-chat',  # Integration type
        'generate_cfg': {
            'max_tokens': 1000,
            'temperature': 0.1,
        }
    }
    
    # Initialize the model
    llm = get_chat_model(cfg)
    
    # Define a simple function
    functions = [
        {
            'name': 'get_weather',
            'description': 'Get the current weather for a location',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The city and state, e.g. San Francisco, CA'
                    },
                    'unit': {
                        'type': 'string',
                        'enum': ['celsius', 'fahrenheit'],
                        'description': 'The temperature unit'
                    }
                },
                'required': ['location']
            }
        }
    ]
    
    messages = [
        Message(role='user', content='What\'s the weather like in San Francisco in celsius?')
    ]
    
    print("User: What's the weather like in San Francisco in celsius?")
    
    # Chat with function calling (non-streaming mode)
    response = llm.chat(messages=messages, functions=functions, stream=False)
    if response:
        for msg in response:
            if msg.content:
                print(f"Assistant: {msg.content}")
            if hasattr(msg, 'function_call') and msg.function_call:
                import json
                print(f"[Function Call: {msg.function_call.name}({msg.function_call.arguments})]")
                
                # Execute the function call
                if msg.function_call.name == 'get_weather':
                    try:
                        args = json.loads(msg.function_call.arguments)
                        result = get_weather(**args)
                        print(f"[Function Result: {result}]")
                        
                        # Add function result to conversation and get final response
                        messages.append(msg)  # Add assistant's function call
                        messages.append(Message(role='function', content=result, name='get_weather'))
                        
                        final_response = llm.chat(messages=messages, stream=False)
                        if final_response:
                            for final_msg in final_response:
                                if final_msg.content:
                                    print(f"Assistant: {final_msg.content}")
                    except Exception as e:
                        print(f"[Function Error: {e}]")
    
    print()


def simple_usage_example():
    """Simplest usage example."""
    print("=== Simple Usage Example ===")
    
    # Simplest way to use GitHub Copilot
    llm = get_chat_model('github_copilot/gpt-4o')
    
    response = llm.quick_chat("Write a haiku about programming.")
    print("User: Write a haiku about programming.")
    print(f"Assistant: {response}")
    print()


def main():
    """Run all examples."""
    print("GitHub Copilot uses OAuth2 authentication through LiteLLM.")
    print("No manual token setup is required - authentication is handled automatically.")
    print()
    
    try:
        simple_usage_example()
        basic_chat_example()
        function_calling_example()
        
        print("=== All examples completed successfully! ===")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. GitHub Copilot subscription")
        print("2. litellm package installed: pip install litellm")
        print("3. Proper OAuth2 authentication setup (handled by LiteLLM)")


if __name__ == '__main__':
    main()
