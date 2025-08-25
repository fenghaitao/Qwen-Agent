#!/usr/bin/env python3
"""
Web Development Multi-Agent System

This demonstrates a multi-agent system for modern web development using:
- HTML/CSS for frontend structure and styling
- JavaScript/TypeScript for interactive functionality
- React components and modern frameworks
- API design and backend services
- Database schema design
- DevOps and deployment configurations

No Python code generation - pure web technologies!
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

from qwen_agent.agents import GroupChat
from qwen_agent.llm.schema import Message


class WebDevWorkspace:
    """Manages web development project workspace."""
    
    def __init__(self, project_name: str = "web_app_project"):
        self.project_name = project_name
        self.workspace_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
        
        # Create modern web project structure
        self.frontend_dir = self.workspace_dir / "frontend"
        self.backend_dir = self.workspace_dir / "backend" 
        self.database_dir = self.workspace_dir / "database"
        self.devops_dir = self.workspace_dir / "devops"
        self.docs_dir = self.workspace_dir / "docs"
        
        # Create directories
        for dir_path in [self.frontend_dir, self.backend_dir, self.database_dir, self.devops_dir, self.docs_dir]:
            dir_path.mkdir(exist_ok=True)
            
        print(f"🌐 Created web development workspace: {self.workspace_dir}")
    
    def save_file(self, filepath: str, content: str) -> str:
        """Save content to a file in the workspace."""
        full_path = self.workspace_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"💾 Saved: {filepath}")
        return str(full_path)
    
    def list_files(self) -> List[str]:
        """List all files in the workspace."""
        files = []
        for path in self.workspace_dir.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.workspace_dir)))
        return sorted(files)
    
    def cleanup(self):
        """Clean up the workspace."""
        shutil.rmtree(self.workspace_dir, ignore_errors=True)
        print(f"🧹 Cleaned up workspace: {self.workspace_dir}")


def create_web_dev_agents():
    """Create specialized agents for web development workflow."""
    
    WEB_DEV_CFGS = {
        'background': '''
        A modern web development team building full-stack applications.
        The team uses cutting-edge web technologies including React, Node.js, 
        TypeScript, and cloud deployment. Each agent specializes in different 
        aspects of web development from UI/UX to backend APIs to DevOps.
        ''',
        'agents': [
            {
                'name': 'UI_UX_Designer',
                'description': 'User interface and user experience design specialist',
                'instructions': '''
                You are a UI/UX design expert specializing in modern web applications.
                Your responsibilities:
                - Create responsive HTML5 semantic markup
                - Design modern CSS with Flexbox/Grid layouts
                - Implement CSS animations and transitions
                - Design component-based UI architectures
                - Ensure accessibility (WCAG) compliance
                - Create mobile-first responsive designs
                
                Focus on:
                - Clean, semantic HTML structure
                - Modern CSS techniques (CSS Grid, Flexbox, CSS Variables)
                - Responsive design principles
                - Accessibility best practices
                - Performance optimization
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Frontend_Developer',
                'description': 'React/JavaScript frontend development specialist',
                'instructions': '''
                You are a frontend development expert specializing in React and modern JavaScript.
                Your responsibilities:
                - Build React components with TypeScript
                - Implement state management (Redux/Context)
                - Create interactive user interfaces
                - Handle API integration and data fetching
                - Implement routing and navigation
                - Optimize bundle size and performance
                
                Technologies to use:
                - React 18+ with functional components and hooks
                - TypeScript for type safety
                - Modern ES6+ JavaScript features
                - CSS Modules or Styled Components
                - React Router for navigation
                - Axios or Fetch API for HTTP requests
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Backend_Developer',
                'description': 'Node.js/API backend development specialist',
                'instructions': '''
                You are a backend development expert specializing in Node.js and API design.
                Your responsibilities:
                - Design RESTful APIs with Express.js
                - Implement authentication and authorization
                - Create database integration layers
                - Handle file uploads and processing
                - Implement caching and performance optimization
                - Design microservices architectures
                
                Technologies to use:
                - Node.js with Express.js framework
                - TypeScript for backend development
                - JWT for authentication
                - Middleware for request processing
                - Error handling and logging
                - API documentation with Swagger/OpenAPI
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Database_Architect',
                'description': 'Database design and SQL specialist',
                'instructions': '''
                You are a database architecture expert specializing in relational and NoSQL databases.
                Your responsibilities:
                - Design normalized database schemas
                - Write efficient SQL queries and procedures
                - Create database migrations and seeds
                - Optimize query performance and indexing
                - Design data models for scalability
                - Implement database security measures
                
                Technologies to use:
                - PostgreSQL for relational data
                - MongoDB for document storage
                - Redis for caching and sessions
                - SQL for complex queries and reports
                - Database migration tools
                - Performance monitoring and optimization
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'DevOps_Engineer',
                'description': 'Deployment, CI/CD, and infrastructure specialist',
                'instructions': '''
                You are a DevOps engineer specializing in cloud deployment and automation.
                Your responsibilities:
                - Create Docker containerization configs
                - Design CI/CD pipelines with GitHub Actions
                - Configure cloud infrastructure (AWS/Azure/GCP)
                - Implement monitoring and logging
                - Set up load balancing and scaling
                - Manage environment configurations
                
                Technologies to use:
                - Docker and Docker Compose
                - GitHub Actions for CI/CD
                - Kubernetes for orchestration
                - Terraform for infrastructure as code
                - Nginx for reverse proxy and load balancing
                - Environment-specific configurations
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'QA_Tester',
                'description': 'Quality assurance and testing specialist',
                'instructions': '''
                You are a QA engineer specializing in web application testing.
                Your responsibilities:
                - Write unit tests for React components
                - Create integration tests for APIs
                - Implement end-to-end testing with Cypress
                - Design test automation strategies
                - Perform accessibility and performance testing
                - Create test documentation and reports
                
                Testing frameworks to use:
                - Jest for unit testing
                - React Testing Library for component tests
                - Cypress for end-to-end testing
                - Postman/Newman for API testing
                - Lighthouse for performance testing
                - axe-core for accessibility testing
                ''',
                'selected_tools': ['code_interpreter']
            },
            {
                'name': 'Product_Manager',
                'description': 'Product requirements and project coordination',
                'is_human': True
            }
        ]
    }
    
    return WEB_DEV_CFGS


def demonstrate_web_dev_workflow():
    """Demonstrate the complete web development workflow."""
    
    print("🌐 Web Development Multi-Agent System Demo")
    print("=" * 60)
    
    # Create workspace
    workspace = WebDevWorkspace("ecommerce_app")
    
    # Create the multi-agent system
    cfgs = create_web_dev_agents()
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    dev_team = GroupChat(agents=cfgs, llm=llm_cfg)
    
    # Define the project specification
    project_spec = """
    # E-Commerce Web Application Specification
    
    Build a modern e-commerce web application with the following features:
    
    ## Frontend Requirements:
    - Product catalog with search and filtering
    - Shopping cart functionality
    - User authentication (login/register)
    - Responsive design for mobile and desktop
    - Modern UI with smooth animations
    
    ## Backend Requirements:
    - RESTful API for product management
    - User authentication with JWT
    - Order processing and payment integration
    - Admin dashboard for inventory management
    - File upload for product images
    
    ## Database Requirements:
    - User accounts and profiles
    - Product catalog with categories
    - Shopping cart and order history
    - Inventory management
    - Payment transaction logs
    
    ## Technology Stack:
    - Frontend: React 18 + TypeScript + CSS Modules
    - Backend: Node.js + Express + TypeScript
    - Database: PostgreSQL + Redis for caching
    - Deployment: Docker + GitHub Actions + AWS
    
    ## Success Criteria:
    - Fully functional e-commerce flow
    - Responsive design across devices
    - Comprehensive test coverage
    - Production-ready deployment
    """
    
    print("📋 Project Specification:")
    print(project_spec)
    print()
    
    workspace.save_file("PROJECT_SPEC.md", project_spec)
    
    # Phase 1: UI/UX Design
    print("🎨 Phase 1: UI/UX Design & HTML Structure")
    print("-" * 50)
    
    messages = [
        Message(
            'user',
            f'''UI/UX Designer: Please create the HTML structure and CSS styling for our e-commerce application.

{project_spec}

Create:
1. Semantic HTML5 structure for the main pages
2. Modern CSS with responsive design
3. Component-based layout system
4. Accessibility-compliant markup''',
            name='Product_Manager'
        )
    ]
    
    # Get UI/UX design
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'UI_UX_Designer':
                print(f"🤖 {name}:")
                print(content[:600] + "..." if len(content) > 600 else content)
                
                # Extract and save HTML/CSS if present
                if "```html" in content:
                    html_start = content.find("```html") + 7
                    html_end = content.find("```", html_start)
                    if html_end > html_start:
                        html_code = content[html_start:html_end].strip()
                        workspace.save_file("frontend/index.html", html_code)
                
                if "```css" in content:
                    css_start = content.find("```css") + 6
                    css_end = content.find("```", css_start)
                    if css_end > css_start:
                        css_code = content[css_start:css_end].strip()
                        workspace.save_file("frontend/styles.css", css_code)
                print()
                break
        
        messages.extend(response)
    
    # Phase 2: React Frontend Development
    print("⚛️ Phase 2: React Frontend Development")
    print("-" * 50)
    
    frontend_request = Message(
        'user',
        '''Frontend Developer: Based on the UI/UX design, please create React components with TypeScript.

Create:
1. Main App component with routing
2. Product catalog component
3. Shopping cart component
4. User authentication components
5. TypeScript interfaces for data models''',
        name='Product_Manager'
    )
    messages.append(frontend_request)
    
    # Get React components
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Frontend_Developer':
                print(f"🤖 {name}:")
                print(content[:600] + "..." if len(content) > 600 else content)
                
                # Extract and save React/TypeScript code
                if "```typescript" in content or "```tsx" in content:
                    code_start = content.find("```t") + 4
                    if content[code_start:code_start+10] == "ypescript":
                        code_start += 9
                    elif content[code_start:code_start+2] == "sx":
                        code_start += 2
                    code_end = content.find("```", code_start)
                    if code_end > code_start:
                        react_code = content[code_start:code_end].strip()
                        workspace.save_file("frontend/src/App.tsx", react_code)
                print()
                break
        
        messages.extend(response)
    
    # Phase 3: Backend API Development
    print("🔧 Phase 3: Node.js Backend API Development")
    print("-" * 50)
    
    backend_request = Message(
        'user',
        '''Backend Developer: Please create the Node.js Express API with TypeScript.

Create:
1. Express server with TypeScript configuration
2. RESTful API endpoints for products and users
3. JWT authentication middleware
4. Database connection and models
5. Error handling and validation''',
        name='Product_Manager'
    )
    messages.append(backend_request)
    
    # Get backend implementation
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Backend_Developer':
                print(f"🤖 {name}:")
                print(content[:600] + "..." if len(content) > 600 else content)
                
                # Extract and save Node.js/TypeScript code
                if "```typescript" in content:
                    code_start = content.find("```typescript") + 13
                    code_end = content.find("```", code_start)
                    if code_end > code_start:
                        backend_code = content[code_start:code_end].strip()
                        workspace.save_file("backend/src/server.ts", backend_code)
                print()
                break
        
        messages.extend(response)
    
    # Phase 4: Database Design
    print("🗄️ Phase 4: Database Schema Design")
    print("-" * 50)
    
    database_request = Message(
        'user',
        '''Database Architect: Please design the PostgreSQL database schema and create SQL migrations.

Create:
1. Database schema for users, products, orders
2. SQL migration scripts
3. Database indexes for performance
4. Sample data seeds
5. Redis caching strategy''',
        name='Product_Manager'
    )
    messages.append(database_request)
    
    # Get database design
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'Database_Architect':
                print(f"🤖 {name}:")
                print(content[:600] + "..." if len(content) > 600 else content)
                
                # Extract and save SQL code
                if "```sql" in content:
                    sql_start = content.find("```sql") + 6
                    sql_end = content.find("```", sql_start)
                    if sql_end > sql_start:
                        sql_code = content[sql_start:sql_end].strip()
                        workspace.save_file("database/migrations/001_initial_schema.sql", sql_code)
                print()
                break
        
        messages.extend(response)
    
    # Phase 5: DevOps Configuration
    print("🚀 Phase 5: DevOps & Deployment Configuration")
    print("-" * 50)
    
    devops_request = Message(
        'user',
        '''DevOps Engineer: Please create deployment configurations and CI/CD pipeline.

Create:
1. Dockerfile for frontend and backend
2. Docker Compose for local development
3. GitHub Actions workflow for CI/CD
4. Kubernetes deployment manifests
5. Environment configuration files''',
        name='Product_Manager'
    )
    messages.append(devops_request)
    
    # Get DevOps configuration
    response_count = 0
    for response in dev_team.run(messages=messages):
        response_count += 1
        if response_count > 2:
            break
            
        for msg in response:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name == 'DevOps_Engineer':
                print(f"🤖 {name}:")
                print(content[:600] + "..." if len(content) > 600 else content)
                
                # Extract and save Docker/YAML configs
                if "```dockerfile" in content:
                    docker_start = content.find("```dockerfile") + 13
                    docker_end = content.find("```", docker_start)
                    if docker_end > docker_start:
                        docker_code = content[docker_start:docker_end].strip()
                        workspace.save_file("devops/Dockerfile", docker_code)
                
                if "```yaml" in content:
                    yaml_start = content.find("```yaml") + 8
                    yaml_end = content.find("```", yaml_start)
                    if yaml_end > yaml_start:
                        yaml_code = content[yaml_start:yaml_end].strip()
                        workspace.save_file("devops/docker-compose.yml", yaml_code)
                print()
                break
        
        messages.extend(response)
    
    # Show final project structure
    print("📁 Final Project Structure:")
    print("-" * 30)
    files = workspace.list_files()
    for file in files:
        # Add appropriate emoji based on file type
        if file.endswith('.html'):
            emoji = "🌐"
        elif file.endswith('.css'):
            emoji = "🎨"
        elif file.endswith(('.ts', '.tsx', '.js', '.jsx')):
            emoji = "⚛️"
        elif file.endswith('.sql'):
            emoji = "🗄️"
        elif file.endswith(('.yml', '.yaml')):
            emoji = "🔧"
        elif 'Dockerfile' in file:
            emoji = "🐳"
        else:
            emoji = "📄"
        
        print(f"{emoji} {file}")
    
    print(f"\n📊 Web Development Summary:")
    print(f"   • Project: E-commerce Web Application")
    print(f"   • Workspace: {workspace.workspace_dir}")
    print(f"   • Files created: {len(files)}")
    print(f"   • Technologies: React, Node.js, PostgreSQL, Docker")
    print(f"   • Agents involved: 6 specialists")
    
    print("\n🎯 Multi-Agent Web Development Features:")
    print("   ✅ Modern HTML5/CSS3 responsive design")
    print("   ✅ React + TypeScript frontend components")
    print("   ✅ Node.js + Express RESTful API")
    print("   ✅ PostgreSQL database schema design")
    print("   ✅ Docker containerization & CI/CD")
    print("   ✅ Full-stack application architecture")
    
    workspace.cleanup()


def main():
    """Run the web development multi-agent demonstration."""
    
    print("🌐 Web Development Multi-Agent System")
    print("=" * 70)
    print("Demonstrating AI agents building modern web applications:")
    print("UI/UX → React Frontend → Node.js Backend → Database → DevOps")
    print()
    print("Technologies: HTML5, CSS3, React, TypeScript, Node.js, PostgreSQL, Docker")
    print("No Python code generation - pure web development stack!")
    print()
    
    try:
        demonstrate_web_dev_workflow()
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("This would work with proper GitHub Copilot authentication")
    
    print("\n" + "=" * 70)
    print("🎓 Key Takeaways:")
    print("   • Multi-agent systems work with ANY technology stack")
    print("   • Each agent specializes in specific web technologies")
    print("   • Agents collaborate across frontend, backend, database, DevOps")
    print("   • Framework is language and domain agnostic")
    print("   • Real-world web development workflows can be fully automated")


if __name__ == '__main__':
    main()