#!/usr/bin/env python3
"""
Research Workflow Manager - Advanced Multi-Agent Coordination

This module demonstrates advanced multi-agent patterns including:
- Workflow orchestration
- State management across agents
- Dynamic agent selection
- Progress tracking
- Error handling and recovery

Usage:
python examples/research_workflow_manager.py
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

from qwen_agent.agents import GroupChat, Assistant, ReActChat, Router
from qwen_agent.llm.schema import Message


class WorkflowStage(Enum):
    """Stages in the research paper writing workflow."""
    INITIALIZATION = "initialization"
    LITERATURE_REVIEW = "literature_review"
    OUTLINE_CREATION = "outline_creation"
    METHODOLOGY = "methodology"
    WRITING_DRAFT = "writing_draft"
    PEER_REVIEW = "peer_review"
    REVISION = "revision"
    FINAL_EDITING = "final_editing"
    SUBMISSION_PREP = "submission_prep"
    COMPLETED = "completed"


@dataclass
class WorkflowState:
    """Tracks the current state of the research workflow."""
    current_stage: WorkflowStage = WorkflowStage.INITIALIZATION
    completed_stages: List[WorkflowStage] = None
    paper_topic: str = ""
    target_journal: str = ""
    word_count_target: int = 0
    current_word_count: int = 0
    literature_sources: List[str] = None
    outline: Dict[str, Any] = None
    draft_sections: Dict[str, str] = None
    review_feedback: List[str] = None
    revision_notes: List[str] = None
    
    def __post_init__(self):
        if self.completed_stages is None:
            self.completed_stages = []
        if self.literature_sources is None:
            self.literature_sources = []
        if self.outline is None:
            self.outline = {}
        if self.draft_sections is None:
            self.draft_sections = {}
        if self.review_feedback is None:
            self.review_feedback = []
        if self.revision_notes is None:
            self.revision_notes = []
    
    def advance_stage(self, next_stage: WorkflowStage):
        """Advance to the next workflow stage."""
        if self.current_stage not in self.completed_stages:
            self.completed_stages.append(self.current_stage)
        self.current_stage = next_stage
    
    def get_progress_percentage(self) -> float:
        """Calculate workflow completion percentage."""
        total_stages = len(WorkflowStage)
        completed_count = len(self.completed_stages)
        return (completed_count / total_stages) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['current_stage'] = self.current_stage.value
        data['completed_stages'] = [stage.value for stage in self.completed_stages]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create from dictionary."""
        data['current_stage'] = WorkflowStage(data['current_stage'])
        data['completed_stages'] = [WorkflowStage(stage) for stage in data['completed_stages']]
        return cls(**data)


class ResearchWorkflowManager:
    """Manages the research paper writing workflow with multiple agents."""
    
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        self.workflow_state = WorkflowState()
        self.agents = self._create_agents()
        self.workflow_coordinator = self._create_coordinator()
        
    def _create_agents(self) -> Dict[str, Any]:
        """Create specialized agents for different workflow stages."""
        
        agents = {}
        
        # Literature Review Agent
        agents['literature_reviewer'] = ReActChat(
            llm=self.llm_config,
            name='Literature_Reviewer',
            description='Expert in systematic literature review and source analysis',
            function_list=['web_search', 'doc_parser'],
            system_message='''
            You are a systematic literature review expert. Your responsibilities:
            1. Conduct comprehensive literature searches
            2. Analyze and categorize research papers
            3. Identify research gaps and trends
            4. Create annotated bibliographies
            5. Suggest citation strategies
            
            Always provide structured, evidence-based literature reviews.
            '''
        )
        
        # Methodology Agent
        agents['methodology_expert'] = Assistant(
            llm=self.llm_config,
            name='Methodology_Expert',
            description='Specialist in research methodology and experimental design',
            system_message='''
            You are a research methodology expert. Your responsibilities:
            1. Design appropriate research methodologies
            2. Suggest experimental protocols and procedures
            3. Recommend statistical analysis approaches
            4. Ensure methodological rigor and validity
            5. Address potential limitations and biases
            
            Provide detailed, scientifically sound methodological guidance.
            '''
        )
        
        # Data Analysis Agent
        agents['data_analyst'] = ReActChat(
            llm=self.llm_config,
            name='Data_Analyst',
            description='Expert in statistical analysis and data visualization',
            function_list=['code_interpreter'],
            system_message='''
            You are a data analysis expert. Your responsibilities:
            1. Perform statistical analyses and hypothesis testing
            2. Create publication-quality visualizations
            3. Interpret results and provide insights
            4. Ensure statistical validity and significance
            5. Generate tables and figures for papers
            
            Provide rigorous, reproducible data analysis.
            '''
        )
        
        # Academic Writer Agent
        agents['academic_writer'] = Assistant(
            llm=self.llm_config,
            name='Academic_Writer',
            description='Expert in academic writing and scientific communication',
            system_message='''
            You are an expert academic writer. Your responsibilities:
            1. Write clear, compelling academic prose
            2. Maintain consistent style and tone
            3. Create engaging abstracts and conclusions
            4. Ensure proper academic formatting
            5. Optimize for target journal requirements
            
            Write publication-ready academic content.
            '''
        )
        
        # Quality Assurance Agent
        agents['quality_reviewer'] = Assistant(
            llm=self.llm_config,
            name='Quality_Reviewer',
            description='Expert in peer review and quality assessment',
            system_message='''
            You are a quality assurance expert. Your responsibilities:
            1. Conduct thorough peer reviews
            2. Check scientific accuracy and rigor
            3. Identify logical inconsistencies
            4. Suggest improvements for clarity and impact
            5. Ensure compliance with publication standards
            
            Provide constructive, detailed feedback for improvement.
            '''
        )
        
        return agents
    
    def _create_coordinator(self) -> Router:
        """Create a coordinator agent that routes tasks to appropriate specialists."""
        
        agent_list = list(self.agents.values())
        
        coordinator = Router(
            llm=self.llm_config,
            agents=agent_list,
            name='Workflow_Coordinator',
            description='Coordinates the research paper writing workflow'
        )
        
        return coordinator
    
    def start_workflow(self, topic: str, target_journal: str = "", word_count: int = 5000):
        """Initialize a new research workflow."""
        
        self.workflow_state = WorkflowState(
            paper_topic=topic,
            target_journal=target_journal,
            word_count_target=word_count
        )
        
        print(f"🚀 Starting research workflow for: '{topic}'")
        print(f"📊 Target: {word_count} words for {target_journal or 'general publication'}")
        print(f"📈 Progress: {self.workflow_state.get_progress_percentage():.1f}% complete")
        print()
        
        return self._execute_stage(WorkflowStage.LITERATURE_REVIEW)
    
    def _execute_stage(self, stage: WorkflowStage) -> List[Message]:
        """Execute a specific workflow stage."""
        
        print(f"🔄 Executing stage: {stage.value.replace('_', ' ').title()}")
        
        # Define stage-specific prompts and agent assignments
        stage_configs = {
            WorkflowStage.LITERATURE_REVIEW: {
                'agent': 'literature_reviewer',
                'prompt': f'''
                Conduct a comprehensive literature review for the research topic: "{self.workflow_state.paper_topic}"
                
                Please:
                1. Search for relevant academic papers and sources
                2. Identify key themes and research directions
                3. Highlight research gaps and opportunities
                4. Suggest 15-20 high-quality sources
                5. Provide a structured summary of the literature landscape
                
                Target journal: {self.workflow_state.target_journal or "General academic journal"}
                '''
            },
            
            WorkflowStage.OUTLINE_CREATION: {
                'agent': 'academic_writer',
                'prompt': f'''
                Create a detailed outline for the research paper: "{self.workflow_state.paper_topic}"
                
                Based on the literature review findings, create:
                1. A structured paper outline with main sections and subsections
                2. Estimated word counts for each section (total target: {self.workflow_state.word_count_target} words)
                3. Key points to cover in each section
                4. Logical flow and transitions between sections
                5. Suggested figures/tables for each section
                
                Literature sources found: {len(self.workflow_state.literature_sources)} papers
                Target journal: {self.workflow_state.target_journal or "General academic journal"}
                '''
            },
            
            WorkflowStage.METHODOLOGY: {
                'agent': 'methodology_expert',
                'prompt': f'''
                Design the research methodology for: "{self.workflow_state.paper_topic}"
                
                Please provide:
                1. Appropriate research design and approach
                2. Data collection methods and procedures
                3. Analysis techniques and statistical methods
                4. Validation and quality assurance measures
                5. Potential limitations and mitigation strategies
                
                Consider the paper outline and literature review findings.
                Target journal requirements: {self.workflow_state.target_journal or "Standard academic standards"}
                '''
            },
            
            WorkflowStage.WRITING_DRAFT: {
                'agent': 'academic_writer',
                'prompt': f'''
                Write the first draft of key sections for: "{self.workflow_state.paper_topic}"
                
                Based on the outline and methodology, write:
                1. Abstract (250 words)
                2. Introduction (800-1000 words)
                3. Methodology section (600-800 words)
                4. Conclusion (400-500 words)
                
                Ensure:
                - Clear, engaging academic writing
                - Proper citations and references
                - Logical flow and coherent arguments
                - Adherence to target journal style
                
                Total target: {self.workflow_state.word_count_target} words
                '''
            },
            
            WorkflowStage.PEER_REVIEW: {
                'agent': 'quality_reviewer',
                'prompt': f'''
                Conduct a comprehensive peer review of the draft paper: "{self.workflow_state.paper_topic}"
                
                Review for:
                1. Scientific accuracy and methodological rigor
                2. Clarity and organization of content
                3. Strength of arguments and evidence
                4. Completeness and quality of literature review
                5. Writing quality and presentation
                6. Compliance with journal standards
                
                Provide specific, constructive feedback with suggestions for improvement.
                Current word count: {self.workflow_state.current_word_count}/{self.workflow_state.word_count_target}
                '''
            }
        }
        
        if stage not in stage_configs:
            print(f"⚠️  Stage {stage.value} not implemented yet")
            return []
        
        config = stage_configs[stage]
        agent_name = config['agent']
        prompt = config['prompt']
        
        # Execute the stage using the appropriate agent
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            messages = [Message('user', prompt)]
            
            print(f"🤖 Assigned to: {agent.name}")
            print("⏳ Processing...")
            
            responses = []
            for response in agent.run(messages=messages):
                responses.extend(response)
            
            # Update workflow state based on stage results
            self._update_state_from_response(stage, responses)
            
            # Advance to next stage
            next_stage = self._get_next_stage(stage)
            if next_stage:
                self.workflow_state.advance_stage(next_stage)
            
            print(f"✅ Stage completed: {stage.value.replace('_', ' ').title()}")
            print(f"📈 Progress: {self.workflow_state.get_progress_percentage():.1f}% complete")
            print()
            
            return responses
        
        else:
            print(f"❌ Agent '{agent_name}' not found")
            return []
    
    def _update_state_from_response(self, stage: WorkflowStage, responses: List[Message]):
        """Update workflow state based on agent responses."""
        
        if not responses:
            return
        
        response_content = responses[-1].content if responses else ""
        
        if stage == WorkflowStage.LITERATURE_REVIEW:
            # Extract literature sources (simplified)
            if "sources" in response_content.lower():
                self.workflow_state.literature_sources.append(f"Literature review completed: {len(response_content)} chars")
        
        elif stage == WorkflowStage.OUTLINE_CREATION:
            # Store outline information
            self.workflow_state.outline = {
                "created": True,
                "content_length": len(response_content),
                "sections_identified": response_content.count("##") + response_content.count("###")
            }
        
        elif stage == WorkflowStage.WRITING_DRAFT:
            # Update word count estimate
            word_count = len(response_content.split())
            self.workflow_state.current_word_count = word_count
            self.workflow_state.draft_sections["main_draft"] = response_content[:500] + "..."
        
        elif stage == WorkflowStage.PEER_REVIEW:
            # Store review feedback
            self.workflow_state.review_feedback.append(f"Review completed: {len(response_content)} chars of feedback")
    
    def _get_next_stage(self, current_stage: WorkflowStage) -> Optional[WorkflowStage]:
        """Determine the next stage in the workflow."""
        
        stage_order = [
            WorkflowStage.INITIALIZATION,
            WorkflowStage.LITERATURE_REVIEW,
            WorkflowStage.OUTLINE_CREATION,
            WorkflowStage.METHODOLOGY,
            WorkflowStage.WRITING_DRAFT,
            WorkflowStage.PEER_REVIEW,
            WorkflowStage.REVISION,
            WorkflowStage.FINAL_EDITING,
            WorkflowStage.SUBMISSION_PREP,
            WorkflowStage.COMPLETED
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def continue_workflow(self) -> Optional[List[Message]]:
        """Continue the workflow from the current stage."""
        
        if self.workflow_state.current_stage == WorkflowStage.COMPLETED:
            print("🎉 Workflow already completed!")
            return None
        
        return self._execute_stage(self.workflow_state.current_stage)
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of the current workflow state."""
        
        return {
            "topic": self.workflow_state.paper_topic,
            "current_stage": self.workflow_state.current_stage.value,
            "progress_percentage": self.workflow_state.get_progress_percentage(),
            "completed_stages": [stage.value for stage in self.workflow_state.completed_stages],
            "word_count": f"{self.workflow_state.current_word_count}/{self.workflow_state.word_count_target}",
            "literature_sources": len(self.workflow_state.literature_sources),
            "outline_created": bool(self.workflow_state.outline),
            "draft_sections": len(self.workflow_state.draft_sections),
            "review_feedback": len(self.workflow_state.review_feedback)
        }
    
    def save_workflow(self, filepath: str):
        """Save the current workflow state to a file."""
        
        with open(filepath, 'w') as f:
            json.dump(self.workflow_state.to_dict(), f, indent=2)
        
        print(f"💾 Workflow saved to: {filepath}")
    
    def load_workflow(self, filepath: str):
        """Load a workflow state from a file."""
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.workflow_state = WorkflowState.from_dict(data)
        print(f"📂 Workflow loaded from: {filepath}")
        print(f"📈 Current progress: {self.workflow_state.get_progress_percentage():.1f}%")


def demo_workflow_manager():
    """Demonstrate the workflow manager functionality."""
    
    print("🔬 Research Workflow Manager Demo")
    print("=" * 50)
    
    # Initialize the workflow manager
    llm_config = {'model': 'qwen-max'}
    manager = ResearchWorkflowManager(llm_config)
    
    # Start a new research workflow
    topic = "Applications of Transformer Models in Climate Science"
    target_journal = "Nature Climate Change"
    word_count = 6000
    
    print(f"📝 Starting workflow for: '{topic}'")
    print(f"🎯 Target: {word_count} words for {target_journal}")
    print()
    
    # Execute the first few stages
    stages_to_demo = [
        WorkflowStage.LITERATURE_REVIEW,
        WorkflowStage.OUTLINE_CREATION,
        WorkflowStage.METHODOLOGY
    ]
    
    # Start the workflow
    manager.start_workflow(topic, target_journal, word_count)
    
    # Execute additional stages
    for stage in stages_to_demo[1:]:  # Skip first as it's already executed
        print(f"\n🔄 Continuing to: {stage.value.replace('_', ' ').title()}")
        manager.continue_workflow()
    
    # Show workflow summary
    print("\n📊 Workflow Summary:")
    print("-" * 30)
    summary = manager.get_workflow_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Save workflow state
    save_path = "research_workflow_state.json"
    manager.save_workflow(save_path)
    
    print(f"\n✅ Demo completed!")
    print(f"💾 Workflow state saved to: {save_path}")
    print("\nIn a real scenario, you could:")
    print("- Load the saved state and continue the workflow")
    print("- Execute remaining stages (writing, review, editing)")
    print("- Iterate on sections based on feedback")
    print("- Generate the final publication-ready paper")


if __name__ == '__main__':
    demo_workflow_manager()