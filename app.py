from job_workflow import analyze_job_posting

@app.event("message")
def handle_message(event, say):
    """Handle messages that might contain job postings"""
    try:
        text = event.get("text", "")
        
        # Run the job posting through our workflow
        analysis_results = analyze_job_posting(text)
        
        if analysis_results["success"]:
            # If we have recommendations, post them
            if analysis_results["recommendations"]:
                say(analysis_results["recommendations"][0])
            
            # If we have detailed results, find matching members
            if "details" in analysis_results["results"]:
                required_skills = analysis_results["results"]["details"]["required_skills"]
                matching_members = resume_parser.find_matching_members(required_skills)
                
                if matching_members:
                    matches_text = "*Matching Members:*\n"
                    for user_id, skills in matching_members.items():
                        matches_text += f"• <@{user_id}> - Matching skills: {', '.join(skills)}\n"
                    say(matches_text)
        else:
            # Log the error but don't send to channel
            print(f"Error analyzing job posting: {analysis_results['error']}")
            
    except Exception as e:
        print(f"Error in message handler: {str(e)}") 