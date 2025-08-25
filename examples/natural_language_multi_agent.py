#!/usr/bin/env python3
"""
Natural Language Multi-Agent Interface

This implements a BMAD-style interface where users interact with multi-agent systems
using natural language prompts. The system automatically:
1. Understands user intent from natural language
2. Selects appropriate agent teams
3. Orchestrates multi-agent workflows
4. Returns results in natural language

Usage:
python examples/natural_language_multi_agent.py
"""

import re
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from qwen_agent.agents import GroupChat, Assistant
from qwen_agent.llm.schema import Message


class Domain(Enum):
    """Available domains for multi-agent teams."""
    WEB_DEVELOPMENT = "web_development"
    SOFTWARE_ENGINEERING = "software_engineering"
    DATA_ANALYTICS = "data_analytics"
    CONTENT_CREATION = "content_creation"
    DEVOPS = "devops"
    GENERAL = "general"


@dataclass
class Intent:
    """Represents user intent parsed from natural language."""
    domain: Domain
    task_type: str
    requirements: List[str]
    technologies: List[str]
    confidence: float


class WorkspaceManager:
    """Manages project workspaces for different domains."""
    
    def __init__(self):
        self.workspaces = {}
    
    def create_workspace(self, project_name: str) -> Path:
        """Create a new workspace for a project."""
        workspace_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
        self.workspaces[project_name] = workspace_dir
        return workspace_dir
    
    def save_file(self, project_name: str, filepath: str, content: str):
        """Save content to a file in the project workspace."""
        if project_name not in self.workspaces:
            self.create_workspace(project_name)
        
        workspace = self.workspaces[project_name]
        full_path = workspace / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        return str(full_path)
    
    def list_files(self, project_name: str) -> List[str]:
        """List files in a project workspace."""
        if project_name not in self.workspaces:
            return []
        
        workspace = self.workspaces[project_name]
        files = []
        for path in workspace.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(workspace)))
        return sorted(files)
    
    def cleanup(self, project_name: str):
        """Clean up a project workspace."""
        if project_name in self.workspaces:
            shutil.rmtree(self.workspaces[project_name], ignore_errors=True)
            del self.workspaces[project_name]


class IntentClassifier:
    """Classifies user intent from natural language prompts."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.classifier = Assistant(
            llm=llm_config,
            system_message="""
            You are an intent classification expert. Analyze user requests and classify them into domains.
            
            Available domains:
            - web_development: Building websites, web apps, frontends, backends, APIs
            - software_engineering: Creating applications, algorithms, code, testing
            - data_analytics: Data analysis, dashboards, reports, statistics, BI
            - content_creation: Writing articles, documentation, presentations
            - devops: Deployment, CI/CD, infrastructure, containers
            - general: General questions or unclear requests
            
            Respond with JSON format:
            {
                "domain": "domain_name",
                "task_type": "brief description",
                "requirements": ["list", "of", "requirements"],
                "technologies": ["mentioned", "technologies"],
                "confidence": 0.95
            }
            """
        )
    
    def classify(self, user_prompt: str) -> Intent:
        """Classify user intent from natural language."""
        
        # Use LLM to classify intent
        messages = [Message('user', f"Classify this request: {user_prompt}")]
        
        try:
            response = ""
            for rsp in self.classifier.run(messages=messages):
                if rsp and rsp[-1].content:
                    response = rsp[-1].content
                    break
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                intent_data = json.loads(response[json_start:json_end])
                
                return Intent(
                    domain=Domain(intent_data.get('domain', 'general')),
                    task_type=intent_data.get('task_type', 'unknown'),
                    requirements=intent_data.get('requirements', []),
                    technologies=intent_data.get('technologies', []),
                    confidence=intent_data.get('confidence', 0.5)
                )
        except Exception as e:
            print(f"Intent classification error: {e}")
        
        # Fallback to pattern matching
        return self._pattern_classify(user_prompt)
    
    def _pattern_classify(self, prompt: str) -> Intent:
        """Fallback pattern-based classification."""
        prompt_lower = prompt.lower()
        
        # Web development patterns
        web_patterns = [
            r'build.*website', r'create.*web app', r'frontend', r'backend',
            r'react', r'node\.?js', r'api', r'dashboard', r'e-commerce'
        ]
        
        # Software engineering patterns
        software_patterns = [
            r'create.*app', r'build.*software', r'implement.*algorithm',
            r'write.*code', r'develop.*system', r'calculator', r'game'
        ]
        
        # Data analytics patterns
        data_patterns = [
            r'analyze.*data', r'create.*dashboard', r'build.*report',
            r'forecast', r'statistics', r'sql', r'tableau', r'excel'
        ]
        
        # Content creation patterns
        content_patterns = [
            r'write.*article', r'create.*content', r'documentation',
            r'presentation', r'blog', r'tutorial'
        ]
        
        # DevOps patterns
        devops_patterns = [
            r'deploy', r'docker', r'kubernetes', r'ci/cd', r'infrastructure',
            r'terraform', r'ansible'
        ]
        
        # Check patterns
        if any(re.search(pattern, prompt_lower) for pattern in web_patterns):
            domain = Domain.WEB_DEVELOPMENT
        elif any(re.search(pattern, prompt_lower) for pattern in software_patterns):
            domain = Domain.SOFTWARE_ENGINEERING
        elif any(re.search(pattern, prompt_lower) for pattern in data_patterns):
            domain = Domain.DATA_ANALYTICS
        elif any(re.search(pattern, prompt_lower) for pattern in content_patterns):
            domain = Domain.CONTENT_CREATION
        elif any(re.search(pattern, prompt_lower) for pattern in devops_patterns):
            domain = Domain.DEVOPS
        else:
            domain = Domain.GENERAL
        
        return Intent(
            domain=domain,
            task_type="pattern_matched",
            requirements=[prompt],
            technologies=[],
            confidence=0.7
        )


class AgentTeamFactory:
    """Creates specialized agent teams for different domains."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
    
    def create_web_dev_team(self) -> GroupChat:
        """Create web development agent team."""
        config = {
            'background': 'Web development team building modern web applications',
            'agents': [
                {
                    'name': 'Frontend_Developer',
                    'description': 'React/JavaScript frontend specialist',
                    'instructions': '''
                    Create modern web frontends using React, HTML5, CSS3, and JavaScript.
                    Focus on responsive design, user experience, and performance.
                    ''',
                    'selected_tools': ['code_interpreter']
                },
                {
                    'name': 'Backend_Developer',
                    'description': 'Node.js/API backend specialist',
                    'instructions': '''
                    Build robust backend APIs using Node.js, Express, and databases.
                    Implement authentication, data validation, and error handling.
                    ''',
                    'selected_tools': ['code_interpreter']
                },
                {
                    'name': 'UI_Designer',
                    'description': 'User interface and experience designer',
                    'instructions': '''
                    Design intuitive user interfaces with modern CSS and responsive layouts.
                    Create wireframes, mockups, and style guides.
                    ''',
                    'selected_tools': []
                }
            ]
        }
        return GroupChat(agents=config, llm=self.llm_config)
    
    def create_software_team(self) -> GroupChat:
        """Create software engineering agent team."""
        config = {
            'background': 'Software engineering team building applications and systems',
            'agents': [
                {
                    'name': 'Software_Architect',
                    'description': 'System design and architecture specialist',
                    'instructions': '''
                    Design software architecture, choose appropriate patterns,
                    and plan implementation strategies for complex systems.
                    ''',
                    'selected_tools': []
                },
                {
                    'name': 'Developer',
                    'description': 'Application development specialist',
                    'instructions': '''
                    Implement software applications using best practices.
                    Write clean, maintainable code with proper error handling.
                    ''',
                    'selected_tools': ['code_interpreter']
                },
                {
                    'name': 'QA_Engineer',
                    'description': 'Quality assurance and testing specialist',
                    'instructions': '''
                    Create comprehensive test suites, perform quality assurance,
                    and ensure software reliability and performance.
                    ''',
                    'selected_tools': ['code_interpreter']
                }
            ]
        }
        return GroupChat(agents=config, llm=self.llm_config)
    
    def create_analytics_team(self) -> GroupChat:
        """Create data analytics agent team."""
        config = {
            'background': 'Data analytics team for business intelligence and insights',
            'agents': [
                {
                    'name': 'Data_Analyst',
                    'description': 'Data analysis and visualization specialist',
                    'instructions': '''
                    Analyze data to extract insights, create visualizations,
                    and build reports for business decision making.
                    ''',
                    'selected_tools': ['code_interpreter']
                },
                {
                    'name': 'SQL_Expert',
                    'description': 'Database and SQL specialist',
                    'instructions': '''
                    Design database schemas, write efficient SQL queries,
                    and optimize data storage and retrieval.
                    ''',
                    'selected_tools': ['code_interpreter']
                },
                {
                    'name': 'BI_Developer',
                    'description': 'Business intelligence dashboard specialist',
                    'instructions': '''
                    Create interactive dashboards, KPI monitoring systems,
                    and executive reporting solutions.
                    ''',
                    'selected_tools': []
                }
            ]
        }
        return GroupChat(agents=config, llm=self.llm_config)
    
    def create_content_team(self) -> GroupChat:
        """Create content creation agent team."""
        config = {
            'background': 'Content creation team for writing and documentation',
            'agents': [
                {
                    'name': 'Technical_Writer',
                    'description': 'Technical documentation specialist',
                    'instructions': '''
                    Create clear, comprehensive technical documentation,
                    user guides, and API documentation.
                    ''',
                    'selected_tools': ['doc_parser']
                },
                {
                    'name': 'Content_Strategist',
                    'description': 'Content planning and strategy specialist',
                    'instructions': '''
                    Plan content strategies, create content calendars,
                    and optimize content for target audiences.
                    ''',
                    'selected_tools': ['web_search']
                },
                {
                    'name': 'Editor',
                    'description': 'Content editing and quality specialist',
                    'instructions': '''
                    Edit and proofread content for clarity, accuracy,
                    and consistency. Ensure high-quality output.
                    ''',
                    'selected_tools': []
                }
            ]
        }
        return GroupChat(agents=config, llm=self.llm_config)


class NaturalLanguageMultiAgent:
    """
    Main interface for natural language multi-agent interactions.
    Users interact with plain English, system handles agent orchestration.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.intent_classifier = IntentClassifier(llm_config)
        self.team_factory = AgentTeamFactory(llm_config)
        self.workspace_manager = WorkspaceManager()
        self.conversation_history = []
        self.current_project = None
    
    def chat(self, user_prompt: str) -> str:
        """
        Main interface: user provides natural language prompt,
        system returns natural language response with results.
        """
        print(f"🤔 Processing: '{user_prompt}'")
        
        # 1. Classify user intent
        intent = self.intent_classifier.classify(user_prompt)
        print(f"🎯 Detected intent: {intent.domain.value} ({intent.confidence:.2f} confidence)")
        
        # 2. Select and create appropriate agent team
        team = self._get_agent_team(intent.domain)
        if not team:
            return "I'm not sure how to help with that. Could you be more specific?"
        
        # 3. Create project workspace if needed
        if not self.current_project:
            self.current_project = f"project_{len(self.conversation_history)}"
            self.workspace_manager.create_workspace(self.current_project)
        
        # 4. Execute multi-agent workflow
        try:
            result = self._execute_workflow(team, user_prompt, intent)
            
            # 5. Format natural language response
            response = self._format_response(result, intent)
            
            # 6. Update conversation history
            self.conversation_history.append({
                'user_prompt': user_prompt,
                'intent': intent,
                'response': response
            })
            
            return response
            
        except Exception as e:
            return f"I encountered an issue: {str(e)}. Could you try rephrasing your request?"
    
    def _get_agent_team(self, domain: Domain) -> Optional[GroupChat]:
        """Get appropriate agent team for the domain."""
        team_map = {
            Domain.WEB_DEVELOPMENT: self.team_factory.create_web_dev_team,
            Domain.SOFTWARE_ENGINEERING: self.team_factory.create_software_team,
            Domain.DATA_ANALYTICS: self.team_factory.create_analytics_team,
            Domain.CONTENT_CREATION: self.team_factory.create_content_team,
        }
        
        if domain in team_map:
            return team_map[domain]()
        return None
    
    def _execute_workflow(self, team: GroupChat, user_prompt: str, intent: Intent) -> List[Message]:
        """Execute the multi-agent workflow."""
        print(f"🤖 Invoking {intent.domain.value} team...")
        
        # Create initial message for the team
        enhanced_prompt = f"""
        User Request: {user_prompt}
        
        Requirements identified: {', '.join(intent.requirements)}
        Technologies mentioned: {', '.join(intent.technologies)}
        
        Please work together to fulfill this request. Provide a complete solution
        with clear deliverables and explanations.
        """
        
        messages = [Message('user', enhanced_prompt, name='User')]
        
        # Execute team workflow (limit iterations for demo)
        responses = []
        iteration_count = 0
        max_iterations = 3
        
        for response in team.run(messages=messages):
            iteration_count += 1
            if iteration_count > max_iterations:
                break
            
            responses.extend(response)
            messages.extend(response)
            
            # Extract and save any code/files generated
            self._extract_and_save_outputs(response)
        
        return responses
    
    def _extract_and_save_outputs(self, responses: List[Message]):
        """Extract code/files from agent responses and save to workspace."""
        for msg in responses:
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            agent_name = msg.name if hasattr(msg, 'name') else msg.get('name', 'unknown')
            
            # Extract code blocks
            code_patterns = [
                (r'```html(.*?)```', 'html'),
                (r'```css(.*?)```', 'css'),
                (r'```javascript(.*?)```', 'js'),
                (r'```python(.*?)```', 'py'),
                (r'```sql(.*?)```', 'sql'),
                (r'```json(.*?)```', 'json'),
                (r'```yaml(.*?)```', 'yml'),
            ]
            
            for pattern, extension in code_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for i, code in enumerate(matches):
                    filename = f"{agent_name.lower()}_{i}.{extension}"
                    self.workspace_manager.save_file(
                        self.current_project, 
                        filename, 
                        code.strip()
                    )
    
    def _format_response(self, responses: List[Message], intent: Intent) -> str:
        """Format agent responses into natural language for the user."""
        if not responses:
            return "I wasn't able to complete that request. Could you try being more specific?"
        
        # Collect key information from responses
        agents_involved = set()
        key_outputs = []
        
        for msg in responses:
            agent_name = msg.name if hasattr(msg, 'name') else msg.get('name')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            
            if agent_name and agent_name != 'User':
                agents_involved.add(agent_name)
                
                # Extract key deliverables
                if len(content) > 100:  # Substantial response
                    key_outputs.append(f"{agent_name}: {content[:150]}...")
        
        # Get files created
        files_created = self.workspace_manager.list_files(self.current_project)
        
        # Format natural language response
        response_parts = []
        
        response_parts.append(f"✅ I've completed your {intent.domain.value.replace('_', ' ')} request!")
        
        if agents_involved:
            response_parts.append(f"🤖 Team involved: {', '.join(sorted(agents_involved))}")
        
        if files_created:
            response_parts.append(f"📁 Files created: {', '.join(files_created)}")
        
        if key_outputs:
            response_parts.append("\n🎯 Key deliverables:")
            for output in key_outputs[:3]:  # Limit to top 3
                response_parts.append(f"   • {output}")
        
        response_parts.append(f"\n💡 You can ask me to modify, extend, or create something new!")
        
        return "\n".join(response_parts)
    
    def get_project_status(self) -> str:
        """Get current project status."""
        if not self.current_project:
            return "No active project. Start by describing what you'd like me to build!"
        
        files = self.workspace_manager.list_files(self.current_project)
        return f"📊 Current project: {len(files)} files created, {len(self.conversation_history)} interactions"
    
    def start_new_project(self):
        """Start a new project."""
        if self.current_project:
            self.workspace_manager.cleanup(self.current_project)
        
        self.current_project = None
        self.conversation_history = []
        return "🆕 Started new project! What would you like me to build?"


def demonstrate_natural_language_interface():
    """Demonstrate the natural language multi-agent interface."""
    
    print("🗣️ Natural Language Multi-Agent Interface Demo")
    print("=" * 60)
    print("Talk to AI agents using plain English!")
    print("The system automatically selects and coordinates appropriate agent teams.")
    print()
    
    # Initialize the system
    llm_config = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    nl_agent = NaturalLanguageMultiAgent(llm_config)
    
    # Test scenarios
    test_prompts = [
        "Build me a simple calculator web app with React",
        "Create a SQL database for a blog with users and posts", 
        "Write documentation for a REST API",
        "Analyze sales data and create a dashboard",
        "Deploy the calculator app using Docker"
    ]
    
    print("🧪 Testing various natural language requests:")
    print()
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"📝 Test {i}: {prompt}")
        print("-" * 40)
        
        try:
            response = nl_agent.chat(prompt)
            print(f"🤖 System Response:")
            print(response)
            print()
            
            # Show project status
            status = nl_agent.get_project_status()
            print(f"📊 {status}")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
        
        # Start new project for next test
        if i < len(test_prompts):
            nl_agent.start_new_project()
    
    print("🎯 Key Features Demonstrated:")
    print("   ✅ Natural language understanding")
    print("   ✅ Automatic agent team selection")
    print("   ✅ Multi-agent workflow orchestration")
    print("   ✅ File generation and workspace management")
    print("   ✅ Natural language response formatting")


def interactive_demo():
    """Run interactive demo where user can chat with the system."""
    
    print("🗣️ Interactive Natural Language Multi-Agent Chat")
    print("=" * 60)
    print("Type your requests in plain English!")
    print("Examples:")
    print("  • 'Build me a todo app with React'")
    print("  • 'Create a database for an e-commerce site'")
    print("  • 'Analyze customer data and make a report'")
    print("  • 'Write API documentation'")
    print()
    print("Type 'quit' to exit, 'status' for project info, 'new' for new project")
    print()
    
    # Initialize system
    llm_config = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    nl_agent = NaturalLanguageMultiAgent(llm_config)
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'status':
                print(f"📊 {nl_agent.get_project_status()}")
                continue
            elif user_input.lower() == 'new':
                print(f"🆕 {nl_agent.start_new_project()}")
                continue
            elif not user_input:
                continue
            
            # Process user request
            response = nl_agent.chat(user_input)
            print(f"\n🤖 System: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function to run the natural language multi-agent demo."""
    
    import sys
    
    print("🗣️ Natural Language Multi-Agent System")
    print("=" * 70)
    print("Interact with specialized AI agent teams using plain English!")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_demo()
    else:
        print("Running automated demo. Use --interactive for chat mode.")
        print()
        demonstrate_natural_language_interface()
        
        print("\n" + "=" * 70)
        print("🎓 This demonstrates BMAD-style natural language interface where:")
        print("   • Users write requests in plain English")
        print("   • System automatically understands intent")
        print("   • Appropriate agent teams are invoked")
        print("   • Multi-agent workflows execute behind the scenes")
        print("   • Results are returned in natural language")
        print()
        print("🚀 Try interactive mode: python natural_language_multi_agent.py --interactive")


if __name__ == '__main__':
    main()