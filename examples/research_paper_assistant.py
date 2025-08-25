#!/usr/bin/env python3
"""
Research Paper Writing Assistant - Multi-Agent Application

This example demonstrates how to build a sophisticated multi-agent system
for collaborative research paper writing. The system includes:

1. Research Agent - Finds and analyzes relevant papers
2. Outline Agent - Creates structured paper outlines
3. Writer Agent - Writes paper sections
4. Reviewer Agent - Reviews and provides feedback
5. Editor Agent - Final editing and formatting
6. Human Researcher - Provides guidance and feedback

Usage:
python examples/research_paper_assistant.py
"""

import os
from typing import List, Optional

from qwen_agent.agents import GroupChat, Assistant, ReActChat
from qwen_agent.gui import WebUI
from qwen_agent.llm.schema import Message


def create_research_paper_agents():
    """Create specialized agents for research paper writing."""
    
    # Configuration for the research paper writing group
    RESEARCH_PAPER_CFGS = {
        'background': '''
        A collaborative research paper writing environment where multiple AI specialists 
        work together with a human researcher to produce high-quality academic papers. 
        Each agent has specific expertise and responsibilities in the writing process.
        ''',
        'agents': [
            {
                'name': 'Research_Agent',
                'description': 'Specialist in finding and analyzing relevant research papers and data',
                'instructions': '''
                You are a research specialist with expertise in academic literature review.
                Your responsibilities:
                - Search for relevant academic papers and sources
                - Analyze and summarize key findings from literature
                - Identify research gaps and opportunities
                - Provide citations and references
                - Suggest methodologies based on existing research
                
                When responding:
                - Always provide specific citations when mentioning research
                - Summarize key findings clearly and concisely
                - Highlight contradictions or gaps in existing literature
                - Suggest areas for further investigation
                ''',
                'selected_tools': ['web_search', 'doc_parser']
            },
            {
                'name': 'Outline_Agent',
                'description': 'Expert in creating structured academic paper outlines',
                'instructions': '''
                You are an academic writing structure specialist.
                Your responsibilities:
                - Create detailed paper outlines following academic standards
                - Organize content logically and coherently
                - Ensure proper academic paper structure (Abstract, Introduction, Methods, Results, Discussion, Conclusion)
                - Balance section lengths and content distribution
                - Suggest subsection organization
                
                When creating outlines:
                - Follow standard academic paper format
                - Include estimated word counts for each section
                - Provide brief descriptions of what each section should contain
                - Ensure logical flow between sections
                - Consider the target audience and journal requirements
                ''',
                'selected_tools': ['doc_parser']
            },
            {
                'name': 'Writer_Agent',
                'description': 'Specialist in writing high-quality academic content',
                'instructions': '''
                You are an expert academic writer with strong technical writing skills.
                Your responsibilities:
                - Write clear, concise, and engaging academic content
                - Maintain consistent tone and style throughout
                - Ensure proper academic language and terminology
                - Create smooth transitions between ideas
                - Write compelling abstracts and conclusions
                
                Writing guidelines:
                - Use active voice when appropriate
                - Maintain objectivity and scientific rigor
                - Include proper in-text citations
                - Write for the target academic audience
                - Ensure clarity and readability
                - Follow journal-specific style guidelines
                ''',
                'selected_tools': ['doc_parser']
            },
            {
                'name': 'Reviewer_Agent',
                'description': 'Expert in peer review and academic quality assessment',
                'instructions': '''
                You are a peer reviewer with expertise in academic quality assessment.
                Your responsibilities:
                - Review content for scientific accuracy and rigor
                - Check logical consistency and argument flow
                - Identify weaknesses in methodology or reasoning
                - Suggest improvements for clarity and impact
                - Ensure compliance with academic standards
                
                Review criteria:
                - Scientific validity and methodology
                - Clarity and organization of content
                - Strength of evidence and arguments
                - Completeness of literature review
                - Quality of writing and presentation
                - Adherence to academic conventions
                
                Provide constructive feedback with specific suggestions for improvement.
                ''',
                'selected_tools': ['doc_parser']
            },
            {
                'name': 'Editor_Agent',
                'description': 'Specialist in final editing, formatting, and publication preparation',
                'instructions': '''
                You are a professional academic editor with expertise in publication standards.
                Your responsibilities:
                - Final proofreading and copy editing
                - Ensure consistent formatting and style
                - Check citation format and bibliography
                - Optimize for target journal requirements
                - Prepare submission-ready documents
                
                Editing focus:
                - Grammar, spelling, and punctuation
                - Consistency in terminology and style
                - Proper citation format (APA, IEEE, etc.)
                - Figure and table formatting
                - Reference list completeness and accuracy
                - Journal-specific formatting requirements
                
                Provide final polish to make the paper publication-ready.
                ''',
                'selected_tools': ['doc_parser']
            },
            {
                'name': 'Human_Researcher',
                'description': 'The lead researcher providing guidance and domain expertise',
                'is_human': True
            }
        ]
    }
    
    return RESEARCH_PAPER_CFGS


def create_specialized_router_agents():
    """Alternative approach: Create specialized agents with Router pattern."""
    
    # LLM configurations
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    llm_cfg_tools = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    # Research Agent with web search capabilities
    research_agent = ReActChat(
        llm=llm_cfg_tools,
        name='Research_Specialist',
        description='Expert in finding and analyzing academic literature and research data',
        function_list=['web_search', 'doc_parser'],
        system_message='''
        You are a research specialist. Your role is to:
        1. Search for relevant academic papers and sources
        2. Analyze and summarize research findings
        3. Identify research gaps and methodological approaches
        4. Provide proper citations and references
        
        Always provide evidence-based responses with proper citations.
        '''
    )
    
    # Writing Agent with document processing
    writing_agent = ReActChat(
        llm=llm_cfg,
        name='Academic_Writer',
        description='Expert in academic writing and content creation',
        function_list=['doc_parser'],
        system_message='''
        You are an expert academic writer. Your role is to:
        1. Create well-structured academic content
        2. Maintain scientific rigor and clarity
        3. Ensure proper academic tone and style
        4. Create compelling abstracts and conclusions
        
        Write clear, concise, and engaging academic content.
        '''
    )
    
    # Analysis Agent with code capabilities
    analysis_agent = ReActChat(
        llm=llm_cfg_tools,
        name='Data_Analyst',
        description='Expert in data analysis, visualization, and statistical methods',
        function_list=['code_interpreter'],
        system_message='''
        You are a data analysis expert. Your role is to:
        1. Perform statistical analysis and data processing
        2. Create visualizations and figures
        3. Interpret results and provide insights
        4. Suggest appropriate analytical methods
        
        Provide rigorous data analysis with clear visualizations.
        '''
    )
    
    # Router to coordinate the specialists
    from qwen_agent.agents import Router
    
    router = Router(
        llm=llm_cfg,
        agents=[research_agent, writing_agent, analysis_agent],
        name='Research_Coordinator',
        description='Coordinates research paper writing process'
    )
    
    return router


def demo_group_chat_workflow():
    """Demonstrate the GroupChat workflow for research paper writing."""
    
    print("=== Research Paper Writing Assistant (GroupChat Mode) ===")
    print()
    
    # Create the multi-agent system
    cfgs = create_research_paper_agents()
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    # Initialize GroupChat
    research_team = GroupChat(agents=cfgs, llm=llm_cfg)
    
    # Simulate a research paper writing session
    print("Starting research paper writing session...")
    print("Topic: 'Applications of Large Language Models in Scientific Research'")
    print()
    
    # Initial request from human researcher
    messages = [
        Message(
            'user', 
            '''I want to write a research paper on "Applications of Large Language Models in Scientific Research". 
            Let's start by having the Research Agent find relevant literature, 
            then the Outline Agent can create a structure, 
            and we'll proceed from there.''',
            name='Human_Researcher'
        )
    ]
    
    # Process the conversation
    print("Multi-agent conversation:")
    print("-" * 50)
    
    response_count = 0
    max_responses = 60000  # Limit for demo
    
    for response in research_team.run(messages=messages):
        response_count += 1
        if response_count > max_responses:
            break
            
        for msg in response:
            # Handle both Message objects and dictionaries
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
            name = msg.name if hasattr(msg, 'name') else msg.get('name')
            
            if role == 'assistant' and name:
                print(f"\n[{name}]:")
                print(content)
                print("-" * 30)
        
        messages.extend(response)
    
    print("\nDemo completed! In a real scenario, this would continue until the paper is complete.")


def demo_router_workflow():
    """Demonstrate the Router workflow for research assistance."""
    
    print("\n=== Research Paper Writing Assistant (Router Mode) ===")
    print()
    
    # Create the router-based system
    coordinator = create_specialized_router_agents()
    
    # Test different types of requests
    test_queries = [
        "Find recent papers on large language models in scientific research",
        "Write an abstract for a paper on LLM applications in research",
        "Analyze the performance data from this research study: [simulated data]"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest Query {i}: {query}")
        print("-" * 50)
        
        messages = [{'role': 'user', 'content': query}]
        
        for response in coordinator.run(messages):
            for msg in response:
                # Handle both Message objects and dictionaries
                role = msg.role if hasattr(msg, 'role') else msg.get('role')
                content = msg.content if hasattr(msg, 'content') else msg.get('content', '')
                name = msg.name if hasattr(msg, 'name') else msg.get('name')
                
                if role == 'assistant':
                    print(f"Response: {content[:200]}...")
                    if name:
                        print(f"(Handled by: {name})")
                    break
        print()


def create_gui_application():
    """Create a GUI application for the research paper assistant."""
    
    print("=== Launching Research Paper Writing Assistant GUI ===")
    
    # Create the multi-agent system
    cfgs = create_research_paper_agents()
    llm_cfg = {
        'model': 'github_copilot/gpt-4o',
        'model_type': 'github_copilot'
    }
    
    research_team = GroupChat(agents=cfgs, llm=llm_cfg)
    
    # Configure the chatbot
    chatbot_config = {
        'user.name': 'Human_Researcher',
        'prompt.suggestions': [
            'Let\'s start writing a paper on "Machine Learning in Climate Science"',
            'Research Agent: Find papers on neural networks for weather prediction',
            'Outline Agent: Create a structure for our climate ML paper',
            'Writer Agent: Write an introduction about AI in climate research',
            'Reviewer Agent: Review the current draft for scientific accuracy',
            'Editor Agent: Format the paper for journal submission'
        ],
        'verbose': True,
        'description': '''
        Welcome to the Research Paper Writing Assistant!
        
        This multi-agent system helps you write high-quality research papers through collaboration between:
        - Research Agent: Literature review and source finding
        - Outline Agent: Paper structure and organization  
        - Writer Agent: Content creation and writing
        - Reviewer Agent: Quality assessment and feedback
        - Editor Agent: Final editing and formatting
        - You (Human Researcher): Domain expertise and guidance
        
        Simply describe what you want to work on, and the agents will collaborate to help you!
        '''
    }
    
    # Launch the web interface
    WebUI(research_team, chatbot_config=chatbot_config).run()


def main():
    """Main function to run the research paper assistant demo."""
    
    print("Research Paper Writing Assistant - Multi-Agent Demo")
    print("=" * 60)
    
    # Check if we should run GUI or demo mode
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        create_gui_application()
    else:
        print("Running demo mode. Use --gui flag for interactive interface.")
        print()
        
        # Run demonstrations
        #demo_group_chat_workflow()
        demo_router_workflow()
        
        print("\n" + "=" * 60)
        print("Demo completed!")
        print("\nTo try the interactive GUI version, run:")
        print("python examples/research_paper_assistant.py --gui")
        print("\nThe GUI allows you to:")
        print("- Interact with all agents in real-time")
        print("- Guide the research and writing process")
        print("- See how agents collaborate and build on each other's work")
        print("- Experience the full multi-agent workflow")


if __name__ == '__main__':
    main()