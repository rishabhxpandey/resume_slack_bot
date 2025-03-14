from typing import Dict, List, Tuple, Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
import json

# Define our state type
class WorkflowState(TypedDict):
    """Type for the workflow state"""
    messages: List[BaseMessage]
    job_text: str
    current_step: str
    analysis_results: Dict
    matching_results: Dict
    recommendations: List[str]
    errors: List[str]

# Define structured output models
class JobClassification(BaseModel):
    """Output schema for job classification"""
    is_job_posting: bool = Field(description="Whether the text is a job posting")
    confidence: float = Field(description="Confidence score between 0 and 1")
    posting_type: str = Field(description="Type of posting: full-time, internship, contract, etc.")

class DetailedJobAnalysis(BaseModel):
    """Output schema for detailed job analysis"""
    job_title: str = Field(description="The title of the job position")
    company_name: str = Field(description="Name of the company")
    required_skills: List[str] = Field(description="Required technical and soft skills")
    preferred_skills: List[str] = Field(description="Preferred but not required skills")
    experience_level: str = Field(description="Required experience level")
    salary_range: str = Field(description="Salary range if mentioned")
    location: str = Field(description="Job location or remote status")
    key_responsibilities: List[str] = Field(description="Main job responsibilities")
    industry: str = Field(description="Industry sector")
    application_deadline: str = Field(description="Application deadline if mentioned")

class SkillGapAnalysis(BaseModel):
    """Output schema for skill gap analysis"""
    critical_skills_needed: List[str] = Field(description="Most important skills needed")
    skill_development_paths: List[Dict] = Field(description="Suggested paths for skill development")
    recommended_resources: List[Dict] = Field(description="Learning resources for skill development")
    estimated_learning_time: Dict = Field(description="Estimated time to acquire each skill")

def create_job_analysis_workflow() -> StateGraph:
    """Create the job analysis workflow graph"""
    
    # Initialize our LLM
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0
    )
    
    # Create our output parsers
    classification_parser = PydanticOutputParser(pydantic_object=JobClassification)
    analysis_parser = PydanticOutputParser(pydantic_object=DetailedJobAnalysis)
    skill_gap_parser = PydanticOutputParser(pydantic_object=SkillGapAnalysis)

    # Define workflow nodes
    def classify_posting(state: WorkflowState) -> WorkflowState:
        """Classify if the text is a job posting and its type"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze if the following text is a job posting. Consider structure, content, and language used."),
            ("user", "{text}"),
            ("system", "Provide classification according to this schema: {format_instructions}")
        ])
        
        messages = prompt.format_messages(
            text=state["job_text"],
            format_instructions=classification_parser.get_format_instructions()
        )
        
        response = llm.invoke(messages)
        classification = classification_parser.parse(response.content)
        
        state["analysis_results"]["classification"] = classification.model_dump()
        state["current_step"] = "classification_complete"
        return state

    def analyze_job_details(state: WorkflowState) -> WorkflowState:
        """Perform detailed analysis of the job posting"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze this job posting in detail. Extract all relevant information 
            about requirements, responsibilities, and company details."""),
            ("user", "{text}"),
            ("system", "Format your analysis according to this schema: {format_instructions}")
        ])
        
        messages = prompt.format_messages(
            text=state["job_text"],
            format_instructions=analysis_parser.get_format_instructions()
        )
        
        response = llm.invoke(messages)
        analysis = analysis_parser.parse(response.content)
        
        state["analysis_results"]["details"] = analysis.model_dump()
        state["current_step"] = "analysis_complete"
        return state

    def analyze_skill_gaps(state: WorkflowState) -> WorkflowState:
        """Analyze skill gaps and provide learning recommendations"""
        job_details = state["analysis_results"]["details"]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on the job requirements, analyze the critical skills needed 
            and provide detailed recommendations for skill development."""),
            ("user", "Job Details: {job_details}"),
            ("system", "Provide analysis according to this schema: {format_instructions}")
        ])
        
        messages = prompt.format_messages(
            job_details=json.dumps(job_details),
            format_instructions=skill_gap_parser.get_format_instructions()
        )
        
        response = llm.invoke(messages)
        skill_analysis = skill_gap_parser.parse(response.content)
        
        state["analysis_results"]["skill_gaps"] = skill_analysis.model_dump()
        state["current_step"] = "skill_analysis_complete"
        return state

    def prepare_final_response(state: WorkflowState) -> WorkflowState:
        """Prepare the final formatted response"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Create a comprehensive, well-formatted response that combines all analysis results.
            Format it for Slack with appropriate markdown and emojis."""),
            ("user", "Analysis Results: {results}")
        ])
        
        messages = prompt.format_messages(
            results=json.dumps(state["analysis_results"])
        )
        
        response = llm.invoke(messages)
        
        state["recommendations"] = [response.content]
        state["current_step"] = "complete"
        return state

    # Define conditional routing
    def should_continue_analysis(state: WorkflowState) -> Tuple[bool, str]:
        """Determine if we should continue with detailed analysis"""
        classification = state["analysis_results"].get("classification", {})
        is_job = classification.get("is_job_posting", False)
        confidence = classification.get("confidence", 0)
        
        if is_job and confidence > 0.8:
            return True, "continue"
        return False, "end"

    # Create the workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("classification", classify_posting)
    workflow.add_node("analysis", analyze_job_details)
    workflow.add_node("skill_gaps", analyze_skill_gaps)
    workflow.add_node("final_response", prepare_final_response)

    # Add edges
    workflow.add_edge("classification", "analysis")
    workflow.add_edge("analysis", "skill_gaps")
    workflow.add_edge("skill_gaps", "final_response")
    workflow.add_edge("final_response", END)

    # Set entry point
    workflow.set_entry_point("classification")

    return workflow

# Function to run the workflow
def analyze_job_posting(text: str) -> Dict:
    """Run the job posting through the analysis workflow"""
    
    # Initialize the workflow
    workflow = create_job_analysis_workflow()
    
    # Create initial state
    initial_state: WorkflowState = {
        "messages": [],
        "job_text": text,
        "current_step": "start",
        "analysis_results": {},
        "matching_results": {},
        "recommendations": [],
        "errors": []
    }
    
    # Run the workflow
    try:
        final_state = workflow.invoke(initial_state)
        return {
            "success": True,
            "results": final_state["analysis_results"],
            "recommendations": final_state["recommendations"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 