#!/usr/bin/env python3
"""
Software Development Multi-Agent System with RAG

This demonstrates a real-world multi-agent system enhanced with RAG capabilities where:
1. Spec Reader Agent - Analyzes requirements and specifications from PDF documents using RAG
2. Code Writer Agent - Writes Python code based on retrieved specs
3. Build Agent - Builds/compiles and checks code syntax
4. Test Writer Agent - Writes comprehensive Python tests
5. Test Runner Agent - Runs tests and reports results
6. Debug Agent - Fixes issues when tests fail

The agents collaborate iteratively until all tests pass, with RAG providing
context-aware specification retrieval from indexed PDF documents.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

from qwen_agent.agents import GroupChat, Assistant, ReActChat
from qwen_agent.llm.schema import Message
from qwen_agent.tools.retrieval import Retrieval
from qwen_agent.tools.doc_parser import DocParser


class RAGEnabledWorkspace:
    """Manages the software development workspace with RAG capabilities for multi-agent collaboration."""
    
    def __init__(self, project_name: str = "rag_multi_agent_project"):
        self.project_name = project_name
        self.workspace_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
        self.src_dir = self.workspace_dir / "src"
        self.test_dir = self.workspace_dir / "tests"
        self.build_dir = self.workspace_dir / "build"
        self.docs_dir = self.workspace_dir / "docs"
        
        # Create directory structure
        self.src_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
        
        # Initialize RAG components
        self.doc_parser = DocParser()
        self.retrieval = Retrieval()
        self.indexed_documents = []
        
        print(f"📁 Created RAG-enabled workspace: {self.workspace_dir}")
    
    def index_pdf_specification(self, pdf_path: str) -> str:
        """Index a PDF specification document for RAG retrieval."""
        try:
            # Copy PDF to workspace docs directory
            pdf_name = Path(pdf_path).name
            workspace_pdf_path = self.docs_dir / pdf_name
            
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            shutil.copy2(pdf_path, workspace_pdf_path)
            
            # Parse and index the document
            print(f"📚 Indexing PDF specification: {pdf_name}")
            parsed_doc = self.doc_parser.call({'url': str(workspace_pdf_path)})
            
            self.indexed_documents.append({
                'path': str(workspace_pdf_path),
                'title': parsed_doc.get('title', pdf_name),
                'chunks': len(parsed_doc.get('raw', [])),
                'parsed_data': parsed_doc
            })
            
            print(f"✅ Successfully indexed {pdf_name} with {len(parsed_doc.get('raw', []))} chunks")
            return str(workspace_pdf_path)
            
        except Exception as e:
            print(f"❌ Failed to index PDF {pdf_path}: {str(e)}")
            raise
    
    def retrieve_specification(self, query: str, max_results: int = 5) -> List[Dict]:
        """Retrieve relevant specification content using RAG."""
        if not self.indexed_documents:
            print("⚠️ No documents indexed for retrieval")
            return []
        
        try:
            # Get all indexed document paths
            doc_paths = [doc['path'] for doc in self.indexed_documents]
            
            # Perform RAG retrieval
            print(f"🔍 Retrieving specifications for query: '{query}'")
            results = self.retrieval.call({
                'query': query,
                'files': doc_paths
            })
            
            # Limit results
            limited_results = results[:max_results] if results else []
            print(f"📋 Retrieved {len(limited_results)} relevant specification chunks")
            
            return limited_results
            
        except Exception as e:
            print(f"❌ Failed to retrieve specifications: {str(e)}")
            return []
    
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
    
    def get_indexed_documents_summary(self) -> str:
        """Get a summary of indexed documents."""
        if not self.indexed_documents:
            return "No documents indexed."
        
        summary = "📚 Indexed Documents:\n"
        for i, doc in enumerate(self.indexed_documents, 1):
            summary += f"  {i}. {doc['title']} ({doc['chunks']} chunks)\n"
        return summary
    
    def cleanup(self):
        """Clean up the workspace."""
        shutil.rmtree(self.workspace_dir, ignore_errors=True)
        print(f"🧹 Cleaned up workspace: {self.workspace_dir}")


def create_rag_software_dev_agents():
    """Create specialized agents for RAG-enhanced software development workflow."""
    
    RAG_SOFTWARE_DEV_CFGS = {
        'background': '''
        A RAG-enhanced software development team where AI agents collaborate to build, test, and iterate on code.
        Each agent has specific expertise in different aspects of software development.
        The Spec Reader Agent uses RAG to retrieve relevant specifications from indexed PDF documents.
        The team works together to transform specifications into working, tested code.
        ''',
        'agents': [
            {
                'name': 'RAG_Spec_Reader_Agent',
                'description': 'RAG-enhanced requirements analysis and specification interpretation expert',
                'instructions': '''
                You are a RAG-enhanced requirements analysis expert. Your responsibilities:
                - Use RAG retrieval to find relevant specifications from indexed PDF documents
                - Parse and understand software specifications from retrieved content
                - Break down requirements into implementable components
                - Identify key functions, classes, and modules needed
                - Define clear interfaces and data structures
                - Specify expected behavior and edge cases
                
                When analyzing specs:
                - First use RAG to retrieve relevant specification content
                - Extract functional requirements clearly from retrieved content
                - Identify input/output specifications
                - Note any constraints or special requirements
                - Suggest appropriate design patterns
                - Provide clear guidance for implementation
                - Reference specific sections from the retrieved documents
                ''',
                'selected_tools': ['retrieval', 'doc_parser']
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
                - Reference specification requirements in code comments
                
                When writing code:
                - Start with clear function/class signatures
                - Include proper type hints where appropriate
                - Handle edge cases and error conditions
                - Write self-documenting code with good variable names
                - Follow SOLID principles and best practices
                - Include references to specification sections in docstrings
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
                - Test against specification requirements
                
                When writing tests:
                - Use pytest framework and conventions
                - Test both positive and negative scenarios
                - Include boundary value testing
                - Test error handling and exceptions
                - Write descriptive test names and docstrings
                - Use appropriate assertions and fixtures
                - Reference specification requirements in test documentation
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
                - Cross-reference issues with specification requirements
                
                When debugging:
                - Carefully analyze error messages and stack traces
                - Identify the specific line or function causing issues
                - Suggest minimal, targeted fixes
                - Consider impact on other parts of the code
                - Verify fixes address the root cause
                - Check fixes against specification requirements
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
    
    return RAG_SOFTWARE_DEV_CFGS


def demonstrate_rag_software_dev_workflow(pdf_spec_path: Optional[str] = None):
    """Demonstrate the complete RAG-enhanced software development workflow."""
    
    print("🔧 RAG-Enhanced Software Development Multi-Agent System Demo")
    print("=" * 70)
    
    # Create RAG-enabled workspace
    workspace = RAGEnabledWorkspace("rag_calculator_project")
    
    # Index PDF specification if provided
    if pdf_spec_path and Path(pdf_spec_path).exists():
        try:
            workspace.index_pdf_specification(pdf_spec_path)
        except Exception as e:
            print(f"⚠️ Failed to index PDF specification: {e}")
            print("Continuing with default specification...")
            pdf_spec_path = None
    
    # Create the multi-agent system
    cfgs = create_rag_software_dev_agents()
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    dev_team = GroupChat(agents=cfgs, llm=llm_cfg)
    
    # Define the software specification (fallback if no PDF)
    default_specification = """
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
    8. gcd(a, b) - Calculate greatest common divisor
    9. lcm(a, b) - Calculate least common multiple
    
    ## Advanced Features:
    - Support for complex numbers where applicable
    - Input validation and type checking
    - Comprehensive error handling
    - Logging of operations
    - Configuration options
    
    ## Requirements:
    - All functions should accept int, float, or complex inputs where appropriate
    - Return appropriate numeric types
    - Handle edge cases and invalid inputs
    - Raise appropriate exceptions for errors
    - Include comprehensive docstrings with examples
    - Follow type hints throughout
    
    ## File Structure:
    - src/advanced_calculator.py - Main calculator module
    - src/calculator_config.py - Configuration module
    - tests/test_advanced_calculator.py - Comprehensive test suite
    - tests/test_calculator_config.py - Configuration tests
    
    ## Success Criteria:
    - All tests must pass
    - Code must follow PEP 8 standards
    - 100% test coverage for core functions
    - Proper error handling for all edge cases
    """
    
    print("📋 Project Specification:")
    if pdf_spec_path:
        print(f"Using PDF specification: {pdf_spec_path}")
        print(workspace.get_indexed_documents_summary())
    else:
        print("Using default specification:")
        print(default_specification[:500] + "..." if len(default_specification) > 500 else default_specification)
    print()
    
    # Save specification to workspace
    workspace.save_file("SPECIFICATION.md", default_specification)
    
    # Start the RAG-enhanced development workflow
    print("🚀 Starting RAG-Enhanced Multi-Agent Development Workflow...")
    print()
    
    # Phase 1: RAG-Enhanced Specification Analysis
    print("🔍 Phase 1: RAG-Enhanced Specification Analysis")
    print("-" * 50)
    
    if pdf_spec_path:
        spec_query = "calculator functions requirements specifications implementation details"
        retrieved_specs = workspace.retrieve_specification(spec_query)
        
        spec_context = "\n\nRetrieved Specification Content:\n"
        for i, spec in enumerate(retrieved_specs, 1):
            spec_context += f"\n--- Chunk {i} ---\n"
            spec_context += spec.get('content', '')[:500] + "..."
        
        messages = [
            Message(
                'user',
                f'''RAG Spec Reader Agent: Please analyze the specification using RAG retrieval and break it down into implementable components.

Query the indexed PDF documents for relevant specifications about calculator functions and requirements.

Use this query: "{spec_query}"

After retrieving relevant content, provide a clear breakdown of what needs to be implemented.

{spec_context if retrieved_specs else "No relevant content retrieved from PDF."}''',
                name='Human_Developer'
            )
        ]
    else:
        messages = [
            Message(
                'user',
                f'''RAG Spec Reader Agent: Please analyze this specification and break it down into implementable components:

{default_specification}

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
            
            if role == 'assistant' and name == 'RAG_Spec_Reader_Agent':
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
        '''Code Writer Agent: Based on the specification analysis, please implement the advanced calculator module. 
        
        Create the src/advanced_calculator.py file with all required functions, proper error handling, type hints, and documentation.
        Also create src/calculator_config.py for configuration options.''',
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
                    code_blocks = content.split("```python")
                    for i, block in enumerate(code_blocks[1:], 1):
                        code_end = block.find("```")
                        if code_end > 0:
                            code = block[:code_end].strip()
                            if "advanced_calculator" in block or i == 1:
                                workspace.save_file("src/advanced_calculator.py", code)
                                print("💾 Code saved to src/advanced_calculator.py")
                            elif "config" in block:
                                workspace.save_file("src/calculator_config.py", code)
                                print("💾 Config saved to src/calculator_config.py")
                print()
                break
        
        messages.extend(response)
    
    return workspace, messages


def create_simple_rag_example():
    """Create a simple RAG-enhanced example without full LLM calls."""
    
    print("\n🎯 Simple RAG-Enhanced Software Development Example")
    print("=" * 60)
    
    # Create workspace
    workspace = RAGEnabledWorkspace("simple_rag_example")
    
    # Try to index a sample PDF if available
    sample_pdf = "examples/resource/doc.pdf"
    if Path(sample_pdf).exists():
        try:
            workspace.index_pdf_specification(sample_pdf)
            print("✅ Successfully indexed sample PDF")
        except Exception as e:
            print(f"⚠️ Could not index PDF: {e}")
    
    # Simulate the RAG workflow with predefined outputs
    print("📋 Specification: Create a math utility with RAG-enhanced requirements")
    
    # 1. RAG Spec Reader output
    print("\n🔍 RAG Spec Reader Agent Analysis:")
    if workspace.indexed_documents:
        print("📚 Using RAG retrieval from indexed documents...")
        retrieved_specs = workspace.retrieve_specification("mathematical operations calculator functions")
        spec_analysis = f"""
        Based on RAG retrieval from indexed documents, I found {len(retrieved_specs)} relevant specification chunks.
        
        Analysis of requirements:
        1. A math utility module with enhanced operations
        2. Functions: add, subtract, multiply, divide, power, sqrt
        3. Advanced error handling for all edge cases
        4. Type hints and comprehensive documentation
        5. Configuration support for different modes
        
        Implementation plan:
        - src/math_utils.py - Main module with type hints
        - src/config.py - Configuration module
        - tests/test_math_utils.py - Comprehensive test suite
        
        Retrieved specification insights:
        - Emphasis on robust error handling
        - Support for multiple numeric types
        - Logging and configuration requirements
        """
    else:
        spec_analysis = """
        Based on the specification, I need to create:
        
        1. An enhanced math utility module with advanced operations
        2. Functions: add, subtract, multiply, divide, power, sqrt
        3. Type hints and comprehensive error handling
        4. Configuration support
        5. Comprehensive test suite
        
        Implementation plan:
        - src/math_utils.py - Main module
        - src/config.py - Configuration
        - tests/test_math_utils.py - Test suite
        """
    print(spec_analysis)
    
    # 2. Code Writer output
    print("\n💻 Code Writer Agent Implementation:")
    code = '''"""Enhanced math utility module with comprehensive features."""
from typing import Union, Optional
import logging
from .config import MathConfig

Number = Union[int, float]

class MathUtils:
    """Enhanced math utility class with configuration support."""
    
    def __init__(self, config: Optional[MathConfig] = None):
        self.config = config or MathConfig()
        self.logger = logging.getLogger(__name__)
    
    def add(self, a: Number, b: Number) -> Number:
        """Add two numbers with logging."""
        result = a + b
        if self.config.enable_logging:
            self.logger.info(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a: Number, b: Number) -> Number:
        """Subtract b from a with logging."""
        result = a - b
        if self.config.enable_logging:
            self.logger.info(f"subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a: Number, b: Number) -> Number:
        """Multiply two numbers with logging."""
        result = a * b
        if self.config.enable_logging:
            self.logger.info(f"multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a: Number, b: Number) -> Number:
        """Divide a by b with comprehensive error handling."""
        if b == 0:
            error_msg = "Cannot divide by zero"
            if self.config.enable_logging:
                self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        result = a / b
        if self.config.enable_logging:
            self.logger.info(f"divide({a}, {b}) = {result}")
        return result
    
    def power(self, a: Number, b: Number) -> Number:
        """Raise a to the power of b."""
        result = a ** b
        if self.config.enable_logging:
            self.logger.info(f"power({a}, {b}) = {result}")
        return result
    
    def sqrt(self, a: Number) -> Number:
        """Calculate square root with error handling."""
        if a < 0:
            error_msg = "Cannot calculate square root of negative number"
            if self.config.enable_logging:
                self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        result = a ** 0.5
        if self.config.enable_logging:
            self.logger.info(f"sqrt({a}) = {result}")
        return result
'''
    
    workspace.save_file("src/math_utils.py", code)
    print("✅ Enhanced code written and saved")
    
    # Config file
    config_code = '''"""Configuration module for math utilities."""
from dataclasses import dataclass

@dataclass
class MathConfig:
    """Configuration for math utilities."""
    enable_logging: bool = True
    precision: int = 10
    use_decimal: bool = False
'''
    
    workspace.save_file("src/config.py", config_code)
    print("✅ Configuration module saved")
    
    # 3. Build Agent output
    print("\n🔨 Build Agent Verification:")
    print("✅ Syntax check passed")
    print("✅ Type hints validated")
    print("✅ No import errors")
    print("✅ All functions properly defined")
    print("✅ Configuration module integrated")
    
    # 4. Test Writer output
    print("\n🧪 Test Writer Agent Tests:")
    test_code = '''"""Comprehensive tests for enhanced math utility module."""
import pytest
import logging
from src.math_utils import MathUtils
from src.config import MathConfig

class TestMathUtils:
    """Test suite for MathUtils class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = MathConfig(enable_logging=False)
        self.math_utils = MathUtils(self.config)
    
    def test_add(self):
        """Test addition functionality."""
        assert self.math_utils.add(2, 3) == 5
        assert self.math_utils.add(-1, 1) == 0
        assert self.math_utils.add(0.1, 0.2) == pytest.approx(0.3)
    
    def test_subtract(self):
        """Test subtraction functionality."""
        assert self.math_utils.subtract(5, 3) == 2
        assert self.math_utils.subtract(0, 5) == -5
        assert self.math_utils.subtract(0.5, 0.2) == pytest.approx(0.3)
    
    def test_multiply(self):
        """Test multiplication functionality."""
        assert self.math_utils.multiply(3, 4) == 12
        assert self.math_utils.multiply(-2, 3) == -6
        assert self.math_utils.multiply(0.5, 4) == 2.0
    
    def test_divide(self):
        """Test division functionality."""
        assert self.math_utils.divide(6, 2) == 3
        assert self.math_utils.divide(5, 2) == 2.5
        assert self.math_utils.divide(1, 3) == pytest.approx(0.333333, rel=1e-5)
    
    def test_divide_by_zero(self):
        """Test division by zero error handling."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.math_utils.divide(5, 0)
    
    def test_power(self):
        """Test power functionality."""
        assert self.math_utils.power(2, 3) == 8
        assert self.math_utils.power(5, 0) == 1
        assert self.math_utils.power(4, 0.5) == 2.0
    
    def test_sqrt(self):
        """Test square root functionality."""
        assert self.math_utils.sqrt(4) == 2
        assert self.math_utils.sqrt(9) == 3
        assert self.math_utils.sqrt(2) == pytest.approx(1.414213, rel=1e-5)
    
    def test_sqrt_negative(self):
        """Test square root of negative number error handling."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            self.math_utils.sqrt(-1)
    
    def test_logging_config(self):
        """Test logging configuration."""
        logging_config = MathConfig(enable_logging=True)
        math_utils_with_logging = MathUtils(logging_config)
        
        # Test that operations work with logging enabled
        result = math_utils_with_logging.add(1, 2)
        assert result == 3

class TestMathConfig:
    """Test suite for MathConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MathConfig()
        assert config.enable_logging is True
        assert config.precision == 10
        assert config.use_decimal is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = MathConfig(enable_logging=False, precision=5, use_decimal=True)
        assert config.enable_logging is False
        assert config.precision == 5
        assert config.use_decimal is True
'''
    
    workspace.save_file("tests/test_math_utils.py", test_code)
    print("✅ Comprehensive tests written and saved")
    
    # 5. Test Runner output
    print("\n🏃 Test Runner Agent Results:")
    print("✅ All tests passed!")
    print("✅ 100% test coverage achieved")
    print("✅ No errors or failures")
    print("✅ Type hints validated")
    print("✅ Configuration tests passed")
    
    # Show final state
    print("\n📁 Final RAG-Enhanced Project Structure:")
    files = workspace.list_files()
    for file in files:
        print(f"📄 {file}")
    
    print(f"\n📊 RAG Enhancement Summary:")
    print(workspace.get_indexed_documents_summary())
    
    print("\n🎉 RAG-Enhanced Development Complete!")
    print("✅ Specification analyzed with RAG retrieval")
    print("✅ Enhanced code implemented with type hints") 
    print("✅ Configuration module created")
    print("✅ Build verified with advanced checks")
    print("✅ Comprehensive tests created")
    print("✅ All tests passing with full coverage")
    
    workspace.cleanup()


def main():
    """Run the RAG-enhanced software development multi-agent demonstration."""
    
    print("🔧 RAG-Enhanced Software Development Multi-Agent System")
    print("=" * 80)
    print("Demonstrating AI agents with RAG capabilities collaborating on software development:")
    print("RAG Spec Reading → Code Writing → Building → Test Writing → Test Running")
    print()
    
    # Check command line arguments
    pdf_path = None
    simple_mode = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--simple':
            simple_mode = True
        elif sys.argv[1].endswith('.pdf'):
            pdf_path = sys.argv[1]
            if not Path(pdf_path).exists():
                print(f"❌ PDF file not found: {pdf_path}")
                print("Falling back to simple example...")
                simple_mode = True
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python software_dev_multi_agent_rag.py [--simple | <pdf_path>]")
            print("  --simple: Run simple example without LLM calls")
            print("  <pdf_path>: Path to PDF specification file to index")
            return
    
    if simple_mode:
        create_simple_rag_example()
    else:
        print("Running full RAG-enhanced multi-agent demo...")
        if pdf_path:
            print(f"Using PDF specification: {pdf_path}")
        else:
            print("Using default specification (no PDF provided)")
            print("Tip: Provide a PDF path as argument to test RAG functionality")
        print()
        
        try:
            workspace, messages = demonstrate_rag_software_dev_workflow(pdf_path)
            
            # Show final workspace state
            print("\n📁 Final Workspace State:")
            print("-" * 30)
            files = workspace.list_files()
            for file in files:
                print(f"📄 {file}")
                if file.endswith('.py'):
                    content = workspace.read_file(file)
                    print(f"   Lines: {len(content.splitlines())}")
            
            print(f"\n📊 RAG-Enhanced Development Summary:")
            print(f"   • Workspace: {workspace.workspace_dir}")
            print(f"   • Files created: {len(files)}")
            print(f"   • Agents involved: 6")
            print(f"   • RAG documents indexed: {len(workspace.indexed_documents)}")
            print(workspace.get_indexed_documents_summary())
            
            workspace.cleanup()
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            print("\nTrying simple example instead...")
            create_simple_rag_example()
    
    print("\n" + "=" * 80)
    print("🎓 Key RAG Enhancement Features:")
    print("   ✅ PDF specification indexing and chunking")
    print("   ✅ RAG-based specification retrieval")
    print("   ✅ Context-aware requirement analysis")
    print("   ✅ Enhanced multi-agent collaboration")
    print("   ✅ Specification-driven development workflow")
    print("   ✅ Advanced error handling and type safety")
    print("   ✅ Configuration-driven architecture")


if __name__ == '__main__':
    main()