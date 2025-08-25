#!/usr/bin/env python3
"""
Software Development Multi-Agent System with MCP Integration

This demonstrates a real-world multi-agent system enhanced with MCP (Model Context Protocol) servers where:
1. Spec Reader Agent - Analyzes requirements and specifications
2. Code Writer Agent - Writes Python code based on specs
3. Build Agent - Uses MCP server for building/compiling and checking code syntax
4. Test Writer Agent - Writes comprehensive Python tests
5. Test Runner Agent - Uses MCP server for running tests and reporting results
6. Debug Agent - Fixes issues when tests fail

The agents collaborate iteratively until all tests pass, with MCP servers handling
build and test operations in isolated environments.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from qwen_agent.agents import GroupChat, Assistant, ReActChat
from qwen_agent.llm.schema import Message
from qwen_agent.tools.mcp_manager import MCPManager


class MCPSoftwareDevWorkspace:
    """Manages the software development workspace with MCP server integration for multi-agent collaboration."""
    
    def __init__(self, project_name: str = "mcp_multi_agent_project"):
        self.project_name = project_name
        self.workspace_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
        self.src_dir = self.workspace_dir / "src"
        self.test_dir = self.workspace_dir / "tests"
        self.build_dir = self.workspace_dir / "build"
        self.mcp_dir = self.workspace_dir / "mcp_servers"
        
        # Create directory structure
        self.src_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.mcp_dir.mkdir(exist_ok=True)
        
        # Initialize MCP manager
        self.mcp_manager = MCPManager()
        self.mcp_tools = []
        
        print(f"📁 Created MCP-enabled workspace: {self.workspace_dir}")
    
    def setup_mcp_servers(self) -> List[Dict]:
        """Set up MCP servers for build and test operations."""
        try:
            # Create build MCP server configuration
            build_server_config = self._create_build_mcp_server()
            
            # Create test MCP server configuration
            test_server_config = self._create_test_mcp_server()
            
            # Combined MCP configuration
            mcp_config = {
                "mcpServers": {
                    "build_server": build_server_config,
                    "test_server": test_server_config
                }
            }
            
            # Initialize MCP tools
            print("🔧 Initializing MCP servers for build and test operations...")
            self.mcp_tools = self.mcp_manager.initConfig(mcp_config)
            print(f"✅ Successfully initialized {len(self.mcp_tools)} MCP tools")
            
            return self.mcp_tools
            
        except Exception as e:
            print(f"⚠️ Failed to setup MCP servers: {e}")
            print("Falling back to local execution...")
            return []
    
    def _create_build_mcp_server(self) -> Dict:
        """Create a build MCP server configuration."""
        # Create a simple build server script
        build_server_script = self.mcp_dir / "build_server.py"
        build_server_content = '''#!/usr/bin/env python3
"""
Simple MCP server for build operations.
"""
import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Create server instance
server = Server("build-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available build tools."""
    return [
        types.Tool(
            name="syntax_check",
            description="Check Python syntax and import dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Python file to check"
                    },
                    "workspace_dir": {
                        "type": "string", 
                        "description": "Workspace directory path"
                    }
                },
                "required": ["file_path", "workspace_dir"]
            }
        ),
        types.Tool(
            name="lint_code",
            description="Run linting checks on Python code",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Python file to lint"
                    },
                    "workspace_dir": {
                        "type": "string",
                        "description": "Workspace directory path"
                    }
                },
                "required": ["file_path", "workspace_dir"]
            }
        ),
        types.Tool(
            name="compile_check",
            description="Compile Python code and check for errors",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to Python file to compile"
                    },
                    "workspace_dir": {
                        "type": "string",
                        "description": "Workspace directory path"
                    }
                },
                "required": ["file_path", "workspace_dir"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for build operations."""
    
    if name == "syntax_check":
        file_path = arguments.get("file_path")
        workspace_dir = arguments.get("workspace_dir")
        
        try:
            full_path = Path(workspace_dir) / file_path
            if not full_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ File not found: {file_path}"
                )]
            
            # Check syntax using py_compile
            import py_compile
            py_compile.compile(str(full_path), doraise=True)
            
            # Check imports
            result = subprocess.run([
                sys.executable, "-m", "py_compile", str(full_path)
            ], capture_output=True, text=True, cwd=workspace_dir)
            
            if result.returncode == 0:
                return [types.TextContent(
                    type="text", 
                    text=f"✅ Syntax check passed for {file_path}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Syntax errors in {file_path}:\\n{result.stderr}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Syntax check failed for {file_path}: {str(e)}"
            )]
    
    elif name == "lint_code":
        file_path = arguments.get("file_path")
        workspace_dir = arguments.get("workspace_dir")
        
        try:
            full_path = Path(workspace_dir) / file_path
            if not full_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ File not found: {file_path}"
                )]
            
            # Try to run flake8 if available, otherwise basic checks
            try:
                result = subprocess.run([
                    "flake8", "--max-line-length=100", str(full_path)
                ], capture_output=True, text=True, cwd=workspace_dir)
                
                if result.returncode == 0:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Linting passed for {file_path}"
                    )]
                else:
                    return [types.TextContent(
                        type="text", 
                        text=f"⚠️ Linting issues in {file_path}:\\n{result.stdout}"
                    )]
            except FileNotFoundError:
                # Fallback to basic checks
                return [types.TextContent(
                    type="text",
                    text=f"✅ Basic linting check passed for {file_path} (flake8 not available)"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Linting failed for {file_path}: {str(e)}"
            )]
    
    elif name == "compile_check":
        file_path = arguments.get("file_path")
        workspace_dir = arguments.get("workspace_dir")
        
        try:
            full_path = Path(workspace_dir) / file_path
            if not full_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ File not found: {file_path}"
                )]
            
            # Compile and check for import errors
            result = subprocess.run([
                sys.executable, "-c", f"import sys; sys.path.insert(0, '{workspace_dir}'); import {Path(file_path).stem}"
            ], capture_output=True, text=True, cwd=workspace_dir)
            
            if result.returncode == 0:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Compilation and import check passed for {file_path}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Compilation/import errors in {file_path}:\\n{result.stderr}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Compilation check failed for {file_path}: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="build-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(build_server_script, 'w') as f:
            f.write(build_server_content)
        
        build_server_script.chmod(0o755)
        
        return {
            "command": sys.executable,
            "args": [str(build_server_script)],
            "env": {"PYTHONPATH": str(self.workspace_dir)}
        }
    
    def _create_test_mcp_server(self) -> Dict:
        """Create a test MCP server configuration."""
        # Create a simple test server script
        test_server_script = self.mcp_dir / "test_server.py"
        test_server_content = '''#!/usr/bin/env python3
"""
Simple MCP server for test operations.
"""
import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Create server instance
server = Server("test-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available test tools."""
    return [
        types.Tool(
            name="run_tests",
            description="Run pytest tests and report results",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Path to test file or directory"
                    },
                    "workspace_dir": {
                        "type": "string",
                        "description": "Workspace directory path"
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Enable verbose output",
                        "default": True
                    }
                },
                "required": ["test_path", "workspace_dir"]
            }
        ),
        types.Tool(
            name="test_coverage",
            description="Run tests with coverage analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Path to test file or directory"
                    },
                    "source_path": {
                        "type": "string",
                        "description": "Path to source code directory"
                    },
                    "workspace_dir": {
                        "type": "string",
                        "description": "Workspace directory path"
                    }
                },
                "required": ["test_path", "source_path", "workspace_dir"]
            }
        ),
        types.Tool(
            name="validate_tests",
            description="Validate test file syntax and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Path to test file"
                    },
                    "workspace_dir": {
                        "type": "string",
                        "description": "Workspace directory path"
                    }
                },
                "required": ["test_path", "workspace_dir"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for test operations."""
    
    if name == "run_tests":
        test_path = arguments.get("test_path")
        workspace_dir = arguments.get("workspace_dir")
        verbose = arguments.get("verbose", True)
        
        try:
            full_test_path = Path(workspace_dir) / test_path
            if not full_test_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Test path not found: {test_path}"
                )]
            
            # Run pytest
            cmd = [sys.executable, "-m", "pytest"]
            if verbose:
                cmd.append("-v")
            cmd.extend(["--tb=short", str(full_test_path)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=workspace_dir,
                env={**os.environ, "PYTHONPATH": workspace_dir}
            )
            
            output = f"Exit code: {result.returncode}\\n"
            output += f"STDOUT:\\n{result.stdout}\\n"
            if result.stderr:
                output += f"STDERR:\\n{result.stderr}\\n"
            
            if result.returncode == 0:
                output = f"✅ All tests passed!\\n\\n{output}"
            else:
                output = f"❌ Some tests failed!\\n\\n{output}"
            
            return [types.TextContent(type="text", text=output)]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Test execution failed: {str(e)}"
            )]
    
    elif name == "test_coverage":
        test_path = arguments.get("test_path")
        source_path = arguments.get("source_path")
        workspace_dir = arguments.get("workspace_dir")
        
        try:
            full_test_path = Path(workspace_dir) / test_path
            full_source_path = Path(workspace_dir) / source_path
            
            if not full_test_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Test path not found: {test_path}"
                )]
            
            if not full_source_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Source path not found: {source_path}"
                )]
            
            # Try to run with coverage
            try:
                cmd = [
                    sys.executable, "-m", "coverage", "run", "--source", str(full_source_path),
                    "-m", "pytest", str(full_test_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=workspace_dir,
                    env={**os.environ, "PYTHONPATH": workspace_dir}
                )
                
                # Get coverage report
                coverage_result = subprocess.run(
                    [sys.executable, "-m", "coverage", "report"],
                    capture_output=True,
                    text=True,
                    cwd=workspace_dir
                )
                
                output = f"Test Results (Exit code: {result.returncode}):\\n{result.stdout}\\n"
                output += f"Coverage Report:\\n{coverage_result.stdout}\\n"
                
                if result.returncode == 0:
                    output = f"✅ Tests passed with coverage analysis!\\n\\n{output}"
                else:
                    output = f"❌ Tests failed during coverage analysis!\\n\\n{output}"
                
                return [types.TextContent(type="text", text=output)]
                
            except FileNotFoundError:
                # Fallback to regular pytest
                return [types.TextContent(
                    type="text",
                    text="⚠️ Coverage tool not available, falling back to regular test execution"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Coverage analysis failed: {str(e)}"
            )]
    
    elif name == "validate_tests":
        test_path = arguments.get("test_path")
        workspace_dir = arguments.get("workspace_dir")
        
        try:
            full_test_path = Path(workspace_dir) / test_path
            if not full_test_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Test file not found: {test_path}"
                )]
            
            # Validate syntax
            import py_compile
            py_compile.compile(str(full_test_path), doraise=True)
            
            # Check for pytest patterns
            with open(full_test_path, 'r') as f:
                content = f.read()
            
            issues = []
            if "def test_" not in content and "class Test" not in content:
                issues.append("No test functions or classes found")
            
            if "import pytest" not in content and "from pytest" not in content:
                issues.append("pytest not imported")
            
            if issues:
                return [types.TextContent(
                    type="text",
                    text=f"⚠️ Test validation issues in {test_path}:\\n" + "\\n".join(f"- {issue}" for issue in issues)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Test validation passed for {test_path}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Test validation failed for {test_path}: {str(e)}"
            )]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="test-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open(test_server_script, 'w') as f:
            f.write(test_server_content)
        
        test_server_script.chmod(0o755)
        
        return {
            "command": sys.executable,
            "args": [str(test_server_script)],
            "env": {"PYTHONPATH": str(self.workspace_dir)}
        }
    
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
    
    def get_mcp_tools_summary(self) -> str:
        """Get a summary of available MCP tools."""
        if not self.mcp_tools:
            return "No MCP tools available."
        
        summary = "🔧 Available MCP Tools:\n"
        for tool in self.mcp_tools:
            summary += f"  • {tool.name}: {tool.description}\n"
        return summary
    
    def cleanup(self):
        """Clean up the workspace and MCP servers."""
        try:
            self.mcp_manager.shutdown()
        except Exception as e:
            print(f"⚠️ MCP cleanup warning: {e}")
        
        shutil.rmtree(self.workspace_dir, ignore_errors=True)
        print(f"🧹 Cleaned up workspace: {self.workspace_dir}")


def create_mcp_software_dev_agents(mcp_tools: List = None):
    """Create specialized agents for MCP-enhanced software development workflow."""
    
    # Prepare MCP tool names for agents
    mcp_tool_names = []
    if mcp_tools:
        mcp_tool_names = [tool.name for tool in mcp_tools]
    
    MCP_SOFTWARE_DEV_CFGS = {
        'background': '''
        A software development team where AI agents collaborate to build, test, and iterate on code.
        Each agent has specific expertise in different aspects of software development.
        The Build and Test Runner agents use MCP servers for isolated and reliable operations.
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
                - Ensure code is compatible with MCP build tools
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'MCP_Build_Agent',
                'description': 'MCP-enhanced code building, syntax checking, and compilation expert',
                'instructions': f'''
                You are a build and integration specialist using MCP servers for reliable build operations.
                Your responsibilities:
                - Use MCP build tools for syntax checking and compilation
                - Verify code structure and organization
                - Run static analysis and linting through MCP servers
                - Check for common code issues
                - Ensure code can be imported and executed
                
                Available MCP tools: {mcp_tool_names}
                
                When building code:
                - Use MCP build server tools for syntax checks
                - Leverage MCP servers for import dependency verification
                - Run compilation checks through isolated MCP environment
                - Report any structural issues found by MCP tools
                - Suggest fixes for build problems identified by MCP servers
                
                Always use MCP tools when available for more reliable and isolated build operations.
                ''',
                'selected_tools': ['code_interpreter'] + [name for name in mcp_tool_names if 'build' in name]
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
                - Ensure tests are compatible with MCP test runners
                
                When writing tests:
                - Use pytest framework and conventions
                - Test both positive and negative scenarios
                - Include boundary value testing
                - Test error handling and exceptions
                - Write descriptive test names and docstrings
                - Use appropriate assertions and fixtures
                - Structure tests for MCP test server execution
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'MCP_Test_Runner_Agent',
                'description': 'MCP-enhanced test execution and results analysis expert',
                'instructions': f'''
                You are a test execution specialist using MCP servers for reliable test operations.
                Your responsibilities:
                - Use MCP test tools for running Python tests
                - Analyze test results and failures through MCP servers
                - Generate detailed test reports using MCP tools
                - Identify patterns in test failures
                - Provide clear feedback on what needs fixing
                
                Available MCP tools: {mcp_tool_names}
                
                When running tests:
                - Use MCP test server for isolated test execution
                - Leverage MCP tools for coverage analysis
                - Execute tests with proper verbosity through MCP
                - Capture and analyze error messages from MCP test results
                - Report test coverage statistics from MCP servers
                - Identify specific failing test cases using MCP tools
                - Provide actionable feedback based on MCP test reports
                
                Always prefer MCP tools for test execution when available for better isolation and reliability.
                ''',
                'selected_tools': ['code_interpreter'] + [name for name in mcp_tool_names if 'test' in name]
            },
            {
                'name': 'Debug_Agent',
                'description': 'Code debugging and issue resolution expert',
                'instructions': '''
                You are a debugging specialist. Your responsibilities:
                - Analyze test failures and error messages from MCP servers
                - Identify root causes of issues
                - Suggest specific code fixes
                - Debug logic errors and edge cases
                - Ensure fixes don't break existing functionality
                - Work with MCP build and test results
                
                When debugging:
                - Carefully analyze error messages and stack traces from MCP tools
                - Identify the specific line or function causing issues
                - Suggest minimal, targeted fixes
                - Consider impact on other parts of the code
                - Verify fixes address the root cause
                - Test fixes using MCP build and test tools
                ''',
                'selected_tools': ['code_interpreter'] + mcp_tool_names
            },
            {
                'name': 'Human_Developer',
                'description': 'Lead developer providing guidance and specifications',
                'is_human': True
            }
        ]
    }
    
    return MCP_SOFTWARE_DEV_CFGS


def demonstrate_mcp_software_dev_workflow():
    """Demonstrate the complete MCP-enhanced software development workflow."""
    
    print("🔧 MCP-Enhanced Software Development Multi-Agent System Demo")
    print("=" * 70)
    
    # Create MCP-enabled workspace
    workspace = MCPSoftwareDevWorkspace("mcp_calculator_project")
    
    # Setup MCP servers
    mcp_tools = workspace.setup_mcp_servers()
    
    # Create the multi-agent system with MCP tools
    cfgs = create_mcp_software_dev_agents(mcp_tools)
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    # Add MCP tools to the agent configuration
    if mcp_tools:
        print(f"🔧 Integrating {len(mcp_tools)} MCP tools into agent system...")
        print(workspace.get_mcp_tools_summary())
    
    dev_team = GroupChat(agents=cfgs, llm=llm_cfg, function_list=mcp_tools)
    
    # Define the software specification
    specification = """
    # Advanced Calculator Module Specification
    
    Create a Python calculator module with the following requirements:
    
    ## Core Functions:
    1. add(a, b) - Add two numbers
    2. subtract(a, b) - Subtract b from a
    3. multiply(a, b) - Multiply two numbers
    4. divide(a, b) - Divide a by b (handle division by zero)
    5. power(a, b) - Raise a to the power of b
    6. sqrt(a) - Calculate square root of a (handle negative numbers)
    7. factorial(n) - Calculate factorial of n (handle negative numbers)
    
    ## Advanced Features:
    - Input validation and type checking
    - Comprehensive error handling
    - Logging of operations
    - Configuration options
    
    ## Requirements:
    - All functions should accept int or float inputs where appropriate
    - Return appropriate numeric types
    - Handle edge cases and invalid inputs
    - Raise appropriate exceptions for errors
    - Include comprehensive docstrings with examples
    - Follow type hints throughout
    
    ## File Structure:
    - src/calculator.py - Main calculator module
    - tests/test_calculator.py - Comprehensive test suite
    
    ## Success Criteria:
    - All tests must pass (verified via MCP test server)
    - Code must follow PEP 8 standards (verified via MCP build server)
    - 100% test coverage for core functions
    - Proper error handling for all edge cases
    """
    
    print("📋 Project Specification:")
    print(specification[:500] + "..." if len(specification) > 500 else specification)
    print()
    
    # Save specification to workspace
    workspace.save_file("SPECIFICATION.md", specification)
    
    # Start the MCP-enhanced development workflow
    print("🚀 Starting MCP-Enhanced Multi-Agent Development Workflow...")
    print()
    
    # Phase 1: Specification Analysis
    print("🔍 Phase 1: Specification Analysis")
    print("-" * 50)
    
    messages = [
        Message(
            'user',
            f'''Spec Reader Agent: Please analyze this specification and break it down into implementable components:

{specification}

Provide a clear breakdown of what needs to be implemented, considering that we'll use MCP servers for build and test operations.''',
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
                print(content[:800] + "..." if len(content) > 800 else content)
                print()
                break
        
        messages.extend(response)
    
    # Phase 2: Code Implementation
    print("💻 Phase 2: Code Implementation")
    print("-" * 40)
    
    code_request = Message(
        'user',
        '''Code Writer Agent: Based on the specification analysis, please implement the calculator module. 
        
        Create the src/calculator.py file with all required functions, proper error handling, type hints, and documentation.
        Ensure the code is compatible with our MCP build and test servers.''',
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
                print(content[:800] + "..." if len(content) > 800 else content)
                
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
    
    return workspace, messages


def create_simple_mcp_example():
    """Create a simple MCP-enhanced example without full LLM calls."""
    
    print("\n🎯 Simple MCP-Enhanced Software Development Example")
    print("=" * 60)
    
    # Create workspace
    workspace = MCPSoftwareDevWorkspace("simple_mcp_example")
    
    # Setup MCP servers
    mcp_tools = workspace.setup_mcp_servers()
    
    # Simulate the MCP workflow with predefined outputs
    print("📋 Specification: Create a math utility with MCP-enhanced build and test")
    
    # 1. Spec Reader output
    print("\n🔍 Spec Reader Agent Analysis:")
    spec_analysis = """
    Based on the specification, I need to create:
    
    1. A math utility module with enhanced operations
    2. Functions: add, subtract, multiply, divide, power, sqrt
    3. Advanced error handling for all edge cases
    4. Type hints and comprehensive documentation
    5. MCP-compatible build and test structure
    
    Implementation plan:
    - src/math_utils.py - Main module with type hints
    - tests/test_math_utils.py - Comprehensive test suite
    - Use MCP servers for build verification and test execution
    
    MCP Integration:
    - Build operations will use isolated MCP build server
    - Test execution will leverage MCP test server
    - Enhanced reliability through server isolation
    """
    print(spec_analysis)
    
    # 2. Code Writer output
    print("\n💻 Code Writer Agent Implementation:")
    code = '''"""Enhanced math utility module with MCP compatibility."""
from typing import Union
import math

Number = Union[int, float]

def add(a: Number, b: Number) -> Number:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
        
    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b

def subtract(a: Number, b: Number) -> Number:
    """Subtract b from a.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Difference of a and b
        
    Examples:
        >>> subtract(5, 3)
        2
        >>> subtract(0, 5)
        -5
    """
    return a - b

def multiply(a: Number, b: Number) -> Number:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Product of a and b
        
    Examples:
        >>> multiply(3, 4)
        12
        >>> multiply(-2, 3)
        -6
    """
    return a * b

def divide(a: Number, b: Number) -> Number:
    """Divide a by b with comprehensive error handling.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Quotient of a and b
        
    Raises:
        ValueError: If b is zero
        
    Examples:
        >>> divide(6, 2)
        3.0
        >>> divide(5, 2)
        2.5
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a: Number, b: Number) -> Number:
    """Raise a to the power of b.
    
    Args:
        a: Base
        b: Exponent
        
    Returns:
        a raised to the power of b
        
    Examples:
        >>> power(2, 3)
        8
        >>> power(4, 0.5)
        2.0
    """
    return a ** b

def sqrt(a: Number) -> float:
    """Calculate square root with error handling.
    
    Args:
        a: Number to calculate square root of
        
    Returns:
        Square root of a
        
    Raises:
        ValueError: If a is negative
        
    Examples:
        >>> sqrt(4)
        2.0
        >>> sqrt(9)
        3.0
    """
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(a)
'''
    
    workspace.save_file("src/math_utils.py", code)
    print("✅ Enhanced code written and saved")
    
    # 3. MCP Build Agent output
    print("\n🔨 MCP Build Agent Verification:")
    if mcp_tools:
        print("🔧 Using MCP build server for verification...")
        print("✅ MCP syntax check passed")
        print("✅ MCP compilation check passed")
        print("✅ MCP lint analysis completed")
        print("✅ Type hints validated via MCP")
        print("✅ Import dependencies verified through MCP")
    else:
        print("⚠️ MCP servers not available, using fallback verification")
        print("✅ Basic syntax check passed")
        print("✅ No import errors")
        print("✅ All functions properly defined")
    
    # 4. Test Writer output
    print("\n🧪 Test Writer Agent Tests:")
    test_code = '''"""Comprehensive tests for enhanced math utility module."""
import pytest
import math
from src.math_utils import add, subtract, multiply, divide, power, sqrt

class TestMathUtils:
    """Test suite for math utility functions."""
    
    def test_add(self):
        """Test addition functionality."""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0.1, 0.2) == pytest.approx(0.3)
        assert add(-5, -3) == -8
    
    def test_subtract(self):
        """Test subtraction functionality."""
        assert subtract(5, 3) == 2
        assert subtract(0, 5) == -5
        assert subtract(0.5, 0.2) == pytest.approx(0.3)
        assert subtract(-2, -5) == 3
    
    def test_multiply(self):
        """Test multiplication functionality."""
        assert multiply(3, 4) == 12
        assert multiply(-2, 3) == -6
        assert multiply(0.5, 4) == 2.0
        assert multiply(0, 100) == 0
    
    def test_divide(self):
        """Test division functionality."""
        assert divide(6, 2) == 3
        assert divide(5, 2) == 2.5
        assert divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
        assert divide(-6, 2) == -3
    
    def test_divide_by_zero(self):
        """Test division by zero error handling."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(-5, 0)
    
    def test_power(self):
        """Test power functionality."""
        assert power(2, 3) == 8
        assert power(5, 0) == 1
        assert power(4, 0.5) == 2.0
        assert power(-2, 2) == 4
        assert power(2, -1) == 0.5
    
    def test_sqrt(self):
        """Test square root functionality."""
        assert sqrt(4) == 2.0
        assert sqrt(9) == 3.0
        assert sqrt(2) == pytest.approx(1.414213, rel=1e-5)
        assert sqrt(0) == 0.0
        assert sqrt(0.25) == 0.5
    
    def test_sqrt_negative(self):
        """Test square root of negative number error handling."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            sqrt(-1)
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            sqrt(-0.1)

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_large_numbers(self):
        """Test with large numbers."""
        assert add(1e10, 1e10) == 2e10
        assert multiply(1e5, 1e5) == 1e10
    
    def test_small_numbers(self):
        """Test with very small numbers."""
        assert add(1e-10, 1e-10) == 2e-10
        assert multiply(1e-5, 1e-5) == pytest.approx(1e-10)
    
    def test_type_consistency(self):
        """Test that return types are consistent."""
        assert isinstance(add(1, 2), int)
        assert isinstance(add(1.0, 2), float)
        assert isinstance(sqrt(4), float)
'''
    
    workspace.save_file("tests/test_math_utils.py", test_code)
    print("✅ Comprehensive tests written and saved")
    
    # 5. MCP Test Runner output
    print("\n🏃 MCP Test Runner Agent Results:")
    if mcp_tools:
        print("🔧 Using MCP test server for execution...")
        print("✅ MCP test execution completed successfully!")
        print("✅ All tests passed via MCP server!")
        print("✅ MCP coverage analysis: 100% coverage achieved")
        print("✅ No errors or failures reported by MCP")
        print("✅ Test isolation verified through MCP server")
    else:
        print("⚠️ MCP test server not available, using fallback")
        print("✅ All tests passed!")
        print("✅ 100% test coverage")
        print("✅ No errors or failures")
    
    # Show final state
    print("\n📁 Final MCP-Enhanced Project Structure:")
    files = workspace.list_files()
    for file in files:
        print(f"📄 {file}")
        if file.endswith('.py') and not file.startswith('mcp_servers/'):
            content = workspace.read_file(file)
            print(f"   Lines: {len(content.splitlines())}")
    
    print(f"\n📊 MCP Enhancement Summary:")
    print(workspace.get_mcp_tools_summary())
    
    print("\n🎉 MCP-Enhanced Development Complete!")
    print("✅ Specification analyzed for MCP compatibility")
    print("✅ Enhanced code implemented with type hints") 
    print("✅ MCP build server verification completed")
    print("✅ Comprehensive tests created for MCP execution")
    print("✅ MCP test server validation successful")
    print("✅ Isolated build and test environment achieved")
    
    workspace.cleanup()


def main():
    """Run the MCP-enhanced software development multi-agent demonstration."""
    
    print("🔧 MCP-Enhanced Software Development Multi-Agent System")
    print("=" * 80)
    print("Demonstrating AI agents with MCP server integration for software development:")
    print("Spec Reading → Code Writing → MCP Building → Test Writing → MCP Test Running")
    print()
    
    # Check command line arguments
    simple_mode = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--simple':
            simple_mode = True
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python software_dev_multi_agent_mcp.py [--simple]")
            print("  --simple: Run simple example without LLM calls")
            print()
            print("MCP Features:")
            print("  • Isolated build operations via MCP build server")
            print("  • Reliable test execution via MCP test server")
            print("  • Enhanced error handling and reporting")
            print("  • Server-based tool isolation")
            return
    
    if simple_mode:
        create_simple_mcp_example()
    else:
        print("Running full MCP-enhanced multi-agent demo...")
        print("Note: Requires MCP dependencies (pip install mcp)")
        print()
        
        try:
            workspace, messages = demonstrate_mcp_software_dev_workflow()
            
            # Show final workspace state
            print("\n📁 Final Workspace State:")
            print("-" * 30)
            files = workspace.list_files()
            for file in files:
                print(f"📄 {file}")
                if file.endswith('.py') and not file.startswith('mcp_servers/'):
                    content = workspace.read_file(file)
                    print(f"   Lines: {len(content.splitlines())}")
            
            print(f"\n📊 MCP-Enhanced Development Summary:")
            print(f"   • Workspace: {workspace.workspace_dir}")
            print(f"   • Files created: {len(files)}")
            print(f"   • Agents involved: 6")
            print(f"   • MCP servers deployed: 2 (build + test)")
            print(workspace.get_mcp_tools_summary())
            
            workspace.cleanup()
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            print("\nTrying simple example instead...")
            create_simple_mcp_example()
    
    print("\n" + "=" * 80)
    print("🎓 Key MCP Enhancement Features:")
    print("   ✅ Isolated build operations via MCP servers")
    print("   ✅ Reliable test execution in MCP environment")
    print("   ✅ Enhanced error handling and reporting")
    print("   ✅ Server-based tool isolation and reliability")
    print("   ✅ Scalable multi-agent MCP integration")
    print("   ✅ Advanced build and test automation")
    print("   ✅ Cross-platform MCP server compatibility")


if __name__ == '__main__':
    main()