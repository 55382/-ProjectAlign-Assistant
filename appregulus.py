import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Assuming the necessary classes and functions like ProjectPlan, TaskList, DependencyList, etc. are imported here

# Define the function to generate the project plan
def project_plan_generation_node(state: SimpleAgentState):
    description = state["project_description"]
    team = state["team"]
    prompt = f"""You are an experienced project description analyzer, who needs to create a project plan.
        Create the project plan using the following steps:
        - Analyze the project description '{description}' and create a list of actionable and realistic tasks with estimated time (in days) to complete each task. If the task takes longer than 5 days, break it down into independent smaller tasks.
        - Assess dependency between tasks. For each task, identify the blocking tasks. Provide for each task the list of dependent tasks.
        - Schedule tasks based on the dependencies.
        - Allocate tasks to team members {team} based on their skills and availability, such that there is no overlapping task assigned for a team member. Ensure that no team member has 2 tasks assigned for the same time period.
    """
    structure_llm = llm.with_structured_output(ProjectPlan)
    project_plan: ProjectPlan = structure_llm.invoke(prompt)
    return {"tasks": project_plan.tasks, "dependencies": project_plan.dependencies, "schedule": project_plan.schedule, "task_allocations": project_plan.task_allocations}

# Define the Streamlit app interface
def app():
    st.title("Project Plan Generator")
    
    # User input for project description and team members
    project_description = st.text_area("Enter project description", height=200)
    team_members = st.text_input("Enter team members (comma separated)").split(',')
    
    # Add button to generate project plan
    if st.button("Generate Project Plan"):
        if project_description and team_members:
            state = {
                "project_description": project_description,
                "team": team_members,
                "tasks": [],
                "dependencies": [],
                "schedule": [],
                "task_allocations": []
            }
            
            # Generate the project plan
            project_plan = project_plan_generation_node(state)
            
            # Extract task schedule and task allocations
            task_schedules = project_plan['schedule']
            task_allocations = project_plan['task_allocations']
            
            # Prepare data for display
            task_schedule_data = []
            for task_schedule in task_schedules:
                task_schedule_data.append([
                    task_schedule.task.task_name,
                    task_schedule.start_day,
                    task_schedule.end_day
                ])
            df_schedule = pd.DataFrame(task_schedule_data, columns=['task_name', 'start', 'end'])
            
            task_allocation_data = []
            for task_allocation in task_allocations:
                task_allocation_data.append([
                    task_allocation.task.task_name,
                    task_allocation.team_member.name
                ])
            df_allocation = pd.DataFrame(task_allocation_data, columns=['task_name', 'team_member'])
            
            # Merge dataframes
            df = df_allocation.merge(df_schedule, on='task_name')
            
            # Convert start and end days to actual dates
            current_date = datetime.today()
            df['start'] = df['start'].apply(lambda x: current_date + timedelta(days=x))
            df['end'] = df['end'].apply(lambda x: current_date + timedelta(days=x))
            
            # Rename columns
            df.rename(columns={'team_member': 'Team Member'}, inplace=True)
            df.sort_values(by='Team Member', inplace=True)
            
            # Create a Gantt chart
            fig = px.timeline(df, x_start="start", x_end="end", y="task_name", color="Team Member", title=f"Gantt Chart - Project Plan")
            
            # Update layout for better visualization
            fig.update_layout(
                xaxis_title="Timeline",
                yaxis_title="Tasks",
                yaxis=dict(autorange="reversed"),
                title_x=0.5
            )
            
            # Display the plot
            st.plotly_chart(fig)
        else:
            st.error("Please provide both project description and team members.")

# Run the Streamlit app
if __name__ == "__main__":
    app()
