import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict

# Define the necessary classes for the project plan
class Task:
    def __init__(self, task_name: str, estimated_time: int):
        self.task_name = task_name
        self.estimated_time = estimated_time  # in days

class TaskList:
    def __init__(self):
        self.tasks: List[Task] = []
    
    def add_task(self, task: Task):
        self.tasks.append(task)

class Dependency:
    def __init__(self, task_name: str, dependent_tasks: List[str]):
        self.task_name = task_name
        self.dependent_tasks = dependent_tasks

class DependencyList:
    def __init__(self):
        self.dependencies: List[Dependency] = []
    
    def add_dependency(self, dependency: Dependency):
        self.dependencies.append(dependency)

class TaskAllocation:
    def __init__(self, task: Task, team_member: str):
        self.task = task
        self.team_member = team_member

class TaskAllocationList:
    def __init__(self):
        self.task_allocations: List[TaskAllocation] = []
    
    def add_task_allocation(self, task_allocation: TaskAllocation):
        self.task_allocations.append(task_allocation)

class Schedule:
    def __init__(self):
        self.schedule: List[Dict] = []
    
    def add_schedule(self, task_name: str, start_day: int, end_day: int):
        self.schedule.append({
            "task_name": task_name,
            "start_day": start_day,
            "end_day": end_day
        })

class ProjectPlan:
    def __init__(self):
        self.tasks = TaskList()
        self.dependencies = DependencyList()
        self.schedule = Schedule()
        self.task_allocations = TaskAllocationList()

# Define the agent state
class SimpleAgentState:
    def __init__(self, project_description: str, team: List[str]):
        self.project_description = project_description
        self.team = team
        self.tasks = []
        self.dependencies = []
        self.schedule = []
        self.task_allocations = []

# Define the function to generate the project plan
def project_plan_generation_node(state: SimpleAgentState):
    description = state.project_description
    team = state.team
    
    # Simple prompt (replace with actual analysis code if required)
    prompt = f"""You are an experienced project description analyzer, who needs to create a project plan.
        Create the project plan using the following steps:
        - Analyze the project description '{description}' and create a list of actionable and realistic tasks with estimated time (in days) to complete each task. If the task takes longer than 5 days, break it down into independent smaller tasks.
        - Assess dependency between tasks. For each task, identify the blocking tasks. Provide for each task the list of dependent tasks.
        - Schedule tasks based on the dependencies.
        - Allocate tasks to team members {team} based on their skills and availability, such that there is no overlapping task assigned for a team member. Ensure that no team member has 2 tasks assigned for the same time period.
    """
    
    # Simulated structured output (replace with your actual logic)
    project_plan = ProjectPlan()
    
    # Example tasks, dependencies, and allocations (use logic to generate these)
    task1 = Task("Define project requirements", 2)
    task2 = Task("Design architecture", 4)
    task3 = Task("Develop code", 7)
    task4 = Task("Test solution", 3)
    
    project_plan.tasks.add_task(task1)
    project_plan.tasks.add_task(task2)
    project_plan.tasks.add_task(task3)
    project_plan.tasks.add_task(task4)
    
    dep1 = Dependency("Design architecture", ["Define project requirements"])
    dep2 = Dependency("Develop code", ["Design architecture"])
    dep3 = Dependency("Test solution", ["Develop code"])
    
    project_plan.dependencies.add_dependency(dep1)
    project_plan.dependencies.add_dependency(dep2)
    project_plan.dependencies.add_dependency(dep3)
    
    # Example schedule
    project_plan.schedule.add_schedule("Define project requirements", 0, 2)
    project_plan.schedule.add_schedule("Design architecture", 2, 6)
    project_plan.schedule.add_schedule("Develop code", 6, 13)
    project_plan.schedule.add_schedule("Test solution", 13, 16)
    
    # Example task allocation
    project_plan.task_allocations.add_task_allocation(TaskAllocation(task1, "Alice"))
    project_plan.task_allocations.add_task_allocation(TaskAllocation(task2, "Bob"))
    project_plan.task_allocations.add_task_allocation(TaskAllocation(task3, "Charlie"))
    project_plan.task_allocations.add_task_allocation(TaskAllocation(task4, "David"))
    
    return {
        "tasks": project_plan.tasks,
        "dependencies": project_plan.dependencies,
        "schedule": project_plan.schedule,
        "task_allocations": project_plan.task_allocations
    }

# Define the Streamlit app interface
def app():
    st.title("Project Plan Generator")
    
    # User input for project description and team members
    project_description = st.text_area("Enter project description", height=200)
    team_members = st.text_input("Enter team members (comma separated)").split(',')
    
    # Add button to generate project plan
    if st.button("Generate Project Plan"):
        if project_description and team_members:
            state = SimpleAgentState(project_description=project_description, team=team_members)
            
            # Generate the project plan
            project_plan = project_plan_generation_node(state)
            
            # Extract task schedule and task allocations
            task_schedules = project_plan['schedule'].schedule
            task_allocations = project_plan['task_allocations'].task_allocations
            
            # Prepare data for display
            task_schedule_data = []
            for task_schedule in task_schedules:
                task_schedule_data.append([
                    task_schedule["task_name"],
                    task_schedule["start_day"],
                    task_schedule["end_day"]
                ])
            df_schedule = pd.DataFrame(task_schedule_data, columns=['task_name', 'start', 'end'])
            
            task_allocation_data = []
            for task_allocation in task_allocations:
                task_allocation_data.append([
                    task_allocation.task.task_name,
                    task_allocation.team_member
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
