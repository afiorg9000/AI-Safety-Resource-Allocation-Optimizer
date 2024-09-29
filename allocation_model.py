from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import csv
import random
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")


projects = []

with open('aisf_projects.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row['Project Title']
        try:
            raised = float(row['Funding Raised'].replace(',', '').replace('$', '')) if row['Funding Raised'] != 'N/A' else 0
            goal = float(row['Funding Goal'].replace(',', '').replace('$', '')) if row['Funding Goal'] != 'N/A' else 0
        except ValueError:
            raised = 0
            goal = 0
        summary = row['Project Summary']
        comments = row['Project Comments'] if 'Project Comments' in row else ''

        projects.append({
            'title': title,
            'goal': goal,
            'raised': raised,
            'summary': summary,
            'comments': comments
        })

def analyze_impact_potential(summary, comments):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Analyze the impact potential of this project."},
            {"role": "user", "content": f"Summary: {summary}\nComments: {comments}"}
        ]
    )
    return response.choices[0].message.content

def apply_risk_tolerance(uncertainty, risk_tolerance):
    if risk_tolerance == 'high':
        return uncertainty * 0.5
    elif risk_tolerance == 'low':
        return uncertainty * 1.5
    else:
        return uncertainty

def flag_data_integrity(project):
    if isinstance(project['goal'], str) and 'arbitrary' in project['goal']:
        return True
    if isinstance(project['summary'], str) and 'vague' in project['summary']:
        return True
    return False

def score_project(project, risk_tolerance='medium', timeframe_priority='near-term', geographic_scope='global'):
    if flag_data_integrity(project):
        print(f"Warning: {project['title']} has questionable data quality!")
        project['raised'] = 0

    goal = project['goal']
    raised = project['raised']
    impact_analysis = analyze_impact_potential(project['summary'], project['comments'])
    
    try:
        impact = float(impact_analysis)
    except ValueError:
        impact = 5

    if goal > 100000:
        impact += 2
    elif goal > 50000:
        impact += 1

    if goal > 0:
        if raised / goal >= 0.8 and goal > 50000:
            impact += 2
        elif raised / goal < 0.5:
            impact -= 1

    uncertainty = 10 if goal > 0 and raised / goal < 0.2 else 5
    uncertainty = apply_risk_tolerance(uncertainty, risk_tolerance)
    scalability = 10 if goal > 10000 else 5
    impact += score_timeframe(project, timeframe_priority)
    impact += score_geographic_scope(project, geographic_scope)

    return impact, uncertainty, scalability

def score_timeframe(project, timeframe_priority):
    if timeframe_priority == 'near-term':
        return 10 if project['goal'] < 50000 else 7
    elif timeframe_priority == 'long-term':
        return 5 if project['goal'] < 50000 else 10
    else:
        return 7

def score_geographic_scope(project, geographic_scope):
    if geographic_scope == 'global':
        return 10
    elif geographic_scope == 'national':
        return 7
    elif geographic_scope == 'local':
        return 5
    else:
        return 6

def score_neglectedness(project):
    return 10 if project['goal'] < 50000 else 5

def score_tractability(project):
    return 10 if project['goal'] < 50000 else 5

def simulate_opportunity_cost(current_projects, budget):
    external_projects = [{'expected_value': random.uniform(0.1, 0.9)} for _ in range(5)]
    opportunity_cost = sum(project['expected_value'] * budget * 0.1 for project in external_projects)
    return opportunity_cost

model = LpProblem("AI_Projects_Allocation", LpMaximize)

allocation_vars = [LpVariable(f"allocation_{i}", 0, 1) for i in range(len(projects))]

model += lpSum([
    score_project(project, risk_tolerance='medium', timeframe_priority='near-term', geographic_scope='global')[0] * allocation_vars[i] -
    score_project(project)[1] + score_neglectedness(project) + score_tractability(project)
    for i, project in enumerate(projects)
])

total_budget = 700000
budget_constraint = lpSum([allocation_vars[i] * projects[i]['goal'] for i in range(len(projects))])
model += budget_constraint <= total_budget

model.solve()

selected_projects = []
total_cost = 0

print("Selected Projects:")
for i, project in enumerate(projects):
    if allocation_vars[i].varValue > 0:
        allocated_amount = allocation_vars[i].varValue * project['goal']
        selected_projects.append({
            'title': project['title'],
            'allocated_fraction': allocation_vars[i].varValue,
            'allocated_amount': allocated_amount,
            'impact': score_project(project)[0],
            'uncertainty': score_project(project)[1]
        })
        total_cost += allocated_amount
for project in selected_projects:
    print(f"Project: {project['title']}, Allocated Fraction: {project['allocated_fraction']:.2f}, "
          f"Allocated Amount: ${project['allocated_amount']:.2f}, Impact: {project['impact']}, "
          f"Uncertainty: {project['uncertainty']}")
print(f"\nTotal Allocated Cost: ${total_cost:.2f}")

opportunity_cost = simulate_opportunity_cost(selected_projects, total_budget)
print(f"Estimated Opportunity Cost: ${opportunity_cost:.2f}")

def generate_description(project_title, allocated_amount, impact, uncertainty):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (
            f"Generate a description for the project titled '{project_title}' "
            f"with an allocated amount of {allocated_amount}, impact of {impact}, "
            f"and uncertainty of {uncertainty}."
        )}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

for project in selected_projects:
    project_title = project['title']
    allocated_amount = project['allocated_amount']
    impact = project['impact']
    uncertainty = project['uncertainty']
    
    description = generate_description(project_title, allocated_amount, impact, uncertainty)
    
    print(f"\nProject: {project_title}")
    print(f"Allocated Amount: ${allocated_amount:.2f}")
    print(f"Impact: {impact}")
    print(f"Uncertainty: {uncertainty}")
    print(f"Qualitative Description: {description}")
