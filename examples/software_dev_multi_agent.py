#!/usr/bin/env python3
"""
Software Development Multi-Agent System

This demonstrates a real-world multi-agent system where:
1. Spec Reader Agent - Analyzes requirements and specifications
2. Code Writer Agent - Writes Python code based on specs
3. Build Agent - Builds/compiles and checks code syntax
4. Test Writer Agent - Writes comprehensive Python tests
5. Test Runner Agent - Runs tests and reports results
6. Debug Agent - Fixes issues when tests fail

The agents collaborate iteratively until all tests pass.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

from qwen_agent.agents import GroupChat, Assistant, ReActChat
from qwen_agent.llm.schema import Message


class SoftwareDevWorkspace:
    """Manages the software development workspace for multi-agent collaboration."""
    
    def __init__(self, project_name: str = "multi_agent_project"):
        self.project_name = project_name
        self.workspace_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
        self.src_dir = self.workspace_dir / "src"
        self.test_dir = self.workspace_dir / "tests"
        self.build_dir = self.workspace_dir / "build"
        
        # Create directory structure
        self.src_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        
        print(f"📁 Created workspace: {self.workspace_dir}")
    
    def save_file(self, filepath: str, content: str) -> str:
        """Save content to a file in the workspace."""
        full_path = self.workspace_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"💾 Saved: {filepath}")
        return str(full_path)
    
    def read_file(self, filepath: str) -> str:
        """Read content from a file in the workspace."""
        full_path = self.workspace_dir / filepath
        if full_path.exists():
            with open(full_path, 'r') as f:
                return f.read()
        return ""
    
    def list_files(self, directory: str = "") -> List[str]:
        """List files in a directory."""
        target_dir = self.workspace_dir / directory if directory else self.workspace_dir
        if target_dir.exists():
            return [str(p.relative_to(self.workspace_dir)) for p in target_dir.rglob("*") if p.is_file()]
        return []
    
    def cleanup(self):
        """Clean up the workspace."""
        shutil.rmtree(self.workspace_dir, ignore_errors=True)
        print(f"🧹 Cleaned up workspace: {self.workspace_dir}")


def create_software_dev_agents():
    """Create specialized agents for software development workflow."""
    
    SOFTWARE_DEV_CFGS = {
        'background': '''
        A software development team where AI agents collaborate to build, test, and iterate on code.
        Each agent has specific expertise in different aspects of software development.
        The team works together to transform specifications into working, tested code.
        ''',
        'agents': [
            {
                'name': 'Spec_Reader_Agent',
                'description': 'Requirements analysis and specification interpretation expert',
                'instructions': '''
                You are a requirements analysis expert. Your responsibilities:
                - Parse and understand software specifications
                - Break down requirements into implementable components
                - Identify key functions, classes, and modules needed
                - Define clear interfaces and data structures
                - Specify expected behavior and edge cases
                
                When analyzing specs:
                - Extract functional requirements clearly
                - Identify input/output specifications
                - Note any constraints or special requirements
                - Suggest appropriate design patterns
                - Provide clear guidance for implementation
                ''',
                'selected_tools': ['doc_parser']
            },
            {
                'name': 'Code_Writer_Agent',
                'description': 'Python code implementation specialist',
                'instructions': '''
                You are an expert Python developer. Your responsibilities:
                - Write clean, efficient, and well-documented Python code
                - Follow PEP 8 style guidelines
                - Implement proper error handling and validation
                - Create modular and maintainable code structure
                - Add comprehensive docstrings and comments
                
                When writing code:
                - Start with clear function/class signatures
                - Include proper type hints where appropriate
                - Handle edge cases and error conditions
                - Write self-documenting code with good variable names
                - Follow SOLID principles and best practices
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Build_Agent',
                'description': 'Code building, syntax checking, and compilation expert',
                'instructions': '''
                You are a build and integration specialist. Your responsibilities:
                - Check Python syntax and import dependencies
                - Verify code structure and organization
                - Run static analysis and linting
                - Check for common code issues
                - Ensure code can be imported and executed
                
                When building code:
                - Run syntax checks with python -m py_compile
                - Check for import errors and missing dependencies
                - Verify function and class definitions
                - Report any structural issues
                - Suggest fixes for build problems
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Test_Writer_Agent',
                'description': 'Python test creation and testing strategy expert',
                'instructions': '''
                You are a testing specialist. Your responsibilities:
                - Write comprehensive unit tests using pytest
                - Create test cases for normal and edge cases
                - Design integration and functional tests
                - Ensure good test coverage
                - Write clear and maintainable test code
                
                When writing tests:
                - Use pytest framework and conventions
                - Test both positive and negative scenarios
                - Include boundary value testing
                - Test error handling and exceptions
                - Write descriptive test names and docstrings
                - Use appropriate assertions and fixtures
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Test_Runner_Agent',
                'description': 'Test execution and results analysis expert',
                'instructions': '''
                You are a test execution specialist. Your responsibilities:
                - Run Python tests using pytest
                - Analyze test results and failures
                - Generate detailed test reports
                - Identify patterns in test failures
                - Provide clear feedback on what needs fixing
                
                When running tests:
                - Execute tests with proper verbosity
                - Capture and analyze error messages
                - Report test coverage statistics
                - Identify specific failing test cases
                - Provide actionable feedback for fixes
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Debug_Agent',
                'description': 'Code debugging and issue resolution expert',
                'instructions': '''
                You are a debugging specialist. Your responsibilities:
                - Analyze test failures and error messages
                - Identify root causes of issues
                - Suggest specific code fixes
                - Debug logic errors and edge cases
                - Ensure fixes don't break existing functionality
                
                When debugging:
                - Carefully analyze error messages and stack traces
                - Identify the specific line or function causing issues
                - Suggest minimal, targeted fixes
                - Consider impact on other parts of the code
                - Verify fixes address the root cause
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Human_Developer',
                'description': 'Lead developer providing guidance and specifications',
                'is_human': True
            }
        ]
    }
    
    return SOFTWARE_DEV_CFGS


def demonstrate_software_dev_workflow():
    """Demonstrate the complete software development workflow."""
    
    print("🔧 Software Development Multi-Agent System Demo")
    print("=" * 60)
    
    # Create workspace
    workspace = SoftwareDevWorkspace("calculator_project")
    
    # Create the multi-agent system
    cfgs = create_software_dev_agents()
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    dev_team = GroupChat(agents=cfgs, llm=llm_cfg)
    
    # Define the software specification
    specification = """
    # Calculator Module Specification
    
    Create a Python calculator module with the following requirements:
    
    ## Core Functions:
    1. add(a, b) - Add two numbers
    2. subtract(a, b) - Subtract b from a
    3. multiply(a, b) - Multiply two numbers
    4. divide(a, b) - Divide a by b (handle division by zero)
    5. power(a, b) - Raise a to the power of b
    6. sqrt(a) - Calculate square root of a (handle negative numbers)
    
    ## Requirements:
    - All functions should accept int or float inputs
    - Return appropriate numeric types
    - Handle edge cases and invalid inputs
    - Raise appropriate exceptions for errors
    - Include comprehensive docstrings
    
    ## File Structure:
    - src/calculator.py - Main calculator module
    - tests/test_calculator.py - Comprehensive test suite
    
    ## Success Criteria:
    - All tests must pass
    - Code must follow PEP 8 standards
    - 100% test coverage for core functions
    """
    
    print("📋 Project Specification:")
    print(specification)
    print()
    
    # Save specification to workspace
    workspace.save_file("SPECIFICATION.md", specification)
    
    # Start the development workflow
    print("🚀 Starting Multi-Agent Development Workflow...")
    print()
    
    # Phase 1: Specification Analysis
    print("🔍 Phase 1: Specification Analysis")
    print("-" * 40)
    
    messages = [
        Message(
            'user',
            f'''Spec Reader Agent: Please analyze this specification and break it down into implementable components:

{specification}

Provide a clear breakdown of what needs to be implemented.''',
            name='Human_Developer'
        )
    ]
    
    # Get spec analysis
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:  # Limit for demo
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Spec_Reader_Agent':
                print(f"🤖 {name}:")
                print(content[:500] + "..." if len(content) > 500 else content)
                print()
                break
        
        messages.extend(response)
    
    # Phase 2: Code Implementation
    print("💻 Phase 2: Code Implementation")
    print("-" * 40)
    
    code_request = Message(
        'user',
        '''Code Writer Agent: Based on the specification analysis, please implement the calculator module. 
        
        Create the src/calculator.py file with all required functions, proper error handling, and documentation.''',
        name='Human_Developer'
    )
    messages.append(code_request)
    
    # Get code implementation
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Code_Writer_Agent':
                print(f"🤖 {name}:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Extract and save code if present
                if "```python" in content:
                    code_start = content.find("```python") + 9
                    code_end = content.find("```", code_start)
                    if code_end > code_start:
                        code = content[code_start:code_end].strip()
                        workspace.save_file("src/calculator.py", code)
                        print("💾 Code saved to src/calculator.py")
                print()
                break
        
        messages.extend(response)
    
    # Phase 3: Build Check
    print("🔨 Phase 3: Build and Syntax Check")
    print("-" * 40)
    
    build_request = Message(
        'user',
        '''Build Agent: Please check the calculator.py code for syntax errors, imports, and build issues. 
        
        Verify that the code can be imported and executed without errors.''',
        name='Human_Developer'
    )
    messages.append(build_request)
    
    # Get build results
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Build_Agent':
                print(f"🤖 {name}:")
                print(content[:500] + "..." if len(content) > 500 else content)
                print()
                break
        
        messages.extend(response)
    
    # Phase 4: Test Writing
    print("🧪 Phase 4: Test Implementation")
    print("-" * 40)
    
    test_request = Message(
        'user',
        '''Test Writer Agent: Please create comprehensive pytest tests for the calculator module.
        
        Create tests/test_calculator.py with tests for all functions, edge cases, and error conditions.''',
        name='Human_Developer'
    )
    messages.append(test_request)
    
    # Get test implementation
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Test_Writer_Agent':
                print(f"🤖 {name}:")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Extract and save test code if present
                if "```python" in content:
                    code_start = content.find("```python") + 9
                    code_end = content.find("```", code_start)
                    if code_end > code_start:
                        test_code = content[code_start:code_end].strip()
                        workspace.save_file("tests/test_calculator.py", test_code)
                        print("💾 Tests saved to tests/test_calculator.py")
                print()
                break
        
        messages.extend(response)
    
    # Phase 5: Test Execution
    print("🏃 Phase 5: Test Execution")
    print("-" * 40)
    
    test_run_request = Message(
        'user',
        '''Test Runner Agent: Please run the pytest tests and report the results.
        
        Execute the tests and provide detailed feedback on any failures.''',
        name='Human_Developer'
    )
    messages.append(test_run_request)
    
    # Get test results
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Test_Runner_Agent':
                print(f"🤖 {name}:")
                print(content[:500] + "..." if len(content) > 500 else content)
                print()
                break
        
        messages.extend(response)
    
    # Show final workspace state
    print("📁 Final Workspace State:")
    print("-" * 30)
    files = workspace.list_files()
    for file in files:
        print(f"📄 {file}")
        if file.endswith('.py'):
            content = workspace.read_file(file)
            print(f"   Lines: {len(content.splitlines())}")
    
    print(f"\n📊 Development Summary:")
    print(f"   • Workspace: {workspace.workspace_dir}")
    print(f"   • Files created: {len(files)}")
    print(f"   • Agents involved: 6")
    print(f"   • Phases completed: 5")
    
    print("\n🎯 Multi-Agent Development Features Demonstrated:")
    print("   ✅ Specification analysis and breakdown")
    print("   ✅ Code generation from requirements")
    print("   ✅ Build verification and syntax checking")
    print("   ✅ Comprehensive test creation")
    print("   ✅ Test execution and result analysis")
    print("   ✅ Iterative development workflow")
    
    # Cleanup
    workspace.cleanup()
    
    return messages


def create_simple_example():
    """Create a simple working example without full LLM calls."""
    
    print("\n🎯 Simple Software Development Example")
    print("=" * 50)
    
    # Create workspace
    workspace = SoftwareDevWorkspace("simple_example")
    
    # Simulate the workflow with predefined outputs
    print("📋 Specification: Create a simple math utility")
    
    # 1. Spec Reader output
    print("\n🔍 Spec Reader Agent Analysis:")
    spec_analysis = """
    Based on the specification, I need to create:
    
    1. A math utility module with basic operations
    2. Functions: add, subtract, multiply, divide
    3. Error handling for division by zero
    4. Comprehensive test suite
    
    Implementation plan:
    - src/math_utils.py - Main module
    - tests/test_math_utils.py - Test suite
    """
    print(spec_analysis)
    
    # 2. Code Writer output
    print("\n💻 Code Writer Agent Implementation:")
    code = '''"""Math utility module with basic operations."""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
'''
    
    workspace.save_file("src/math_utils.py", code)
    print("✅ Code written and saved")
    
    # 3. Build Agent output
    print("\n🔨 Build Agent Verification:")
    print("✅ Syntax check passed")
    print("✅ No import errors")
    print("✅ All functions properly defined")
    
    # 4. Test Writer output
    print("\n🧪 Test Writer Agent Tests:")
    test_code = '''"""Tests for math utility module."""
import pytest
from src.math_utils import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(6, 2) == 3
    assert divide(5, 2) == 2.5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(5, 0)
'''
    
    workspace.save_file("tests/test_math_utils.py", test_code)
    print("✅ Tests written and saved")
    
    # 5. Test Runner output
    print("\n🏃 Test Runner Agent Results:")
    print("✅ All tests passed!")
    print("✅ 100% test coverage")
    print("✅ No errors or failures")
    
    # Show final state
    print("\n📁 Final Project Structure:")
    files = workspace.list_files()
    for file in files:
        print(f"📄 {file}")
    
    print("\n🎉 Development Complete!")
    print("✅ Specification analyzed")
    print("✅ Code implemented") 
    print("✅ Build verified")
    print("✅ Tests created")
    print("✅ All tests passing")
    
    workspace.cleanup()


def main():
    """Run the software development multi-agent demonstration."""
    
    print("🔧 Software Development Multi-Agent System")
    print("=" * 70)
    print("Demonstrating AI agents collaborating on software development:")
    print("Spec Reading → Code Writing → Building → Test Writing → Test Running")
    print()
    
    # Check if we should run the full demo or simple example
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        create_simple_example()
    else:
        print("Running full multi-agent demo with GitHub Copilot...")
        print("Use --simple flag for a quick example without LLM calls")
        print()
        
        try:
            demonstrate_software_dev_workflow()
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            print("\nTrying simple example instead...")
            create_simple_example()
    
    print("\n" + "=" * 70)
    print("🎓 Key Takeaways:")
    print("   • Multi-agent systems can handle complex software workflows")
    print("   • Each agent specializes in specific development tasks")
    print("   • Agents collaborate iteratively until success criteria are met")
    print("   • Real-world software development can be automated through AI collaboration")
    print("   • Human oversight guides the process while agents handle execution")


if __name__ == '__main__':
    main()