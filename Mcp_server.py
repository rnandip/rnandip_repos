# mcp_server.py
from flask import Flask, request, jsonify
from jira import JIRA
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# --- Configuration ---
JIRA_SERVER = 'YOUR_JIRA_SERVER_URL'  # Replace with your Jira instance URL
JIRA_USERNAME = 'YOUR_JIRA_USERNAME'  # Replace with your Jira username/email
JIRA_PASSWORD = 'YOUR_PASSWORD_OR_API_TOKEN'  # Replace with your password or API token

jira_options = {'server': JIRA_SERVER}
jira = JIRA(options=jira_options, basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))

# --- Tools ---

def get_jira_tickets(jira_link):
    """Extracts the project key from a Jira link and returns a list of tickets."""
    try:
        project_key = jira_link.split('/browse/')[1].split('-')[0]
        issues = jira.search_issues(f'project={project_key}')
        ticket_list = [issue.key for issue in issues]
        return {"status": "success", "tickets": ticket_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_velocity_chart(board_id):
    """Generates a velocity chart for a given Jira Agile board ID."""
    try:
        sprints = jira.agile_board(board_id).sprints()
        completed_points = []
        sprint_names = []

        for sprint in sprints:
            issues_in_sprint = jira.search_issues(f'sprint={sprint.id}', fields='statusCategoryChangeDate, customfield_10004') # Assuming 'customfield_10004' is Story Points
            total_points = 0
            for issue in issues_in_sprint:
                if hasattr(issue.fields, 'customfield_10004') and issue.fields.customfield_10004:
                    total_points += issue.fields.customfield_10004
            completed_points.append(total_points)
            sprint_names.append(sprint.name)

        plt.figure(figsize=(10, 6))
        plt.bar(sprint_names, completed_points, color='skyblue')
        plt.xlabel('Sprint')
        plt.ylabel('Completed Story Points')
        plt.title(f'Velocity Chart - Board ID: {board_id}')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the plot to a buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
        plt.close()

        return {"status": "success", "image": img_base64}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- API Endpoints ---

@app.route('/execute_tool', methods=['POST'])
def execute_tool():
    data = request.get_json()
    if not data or 'tool' not in data or 'arguments' not in data:
        return jsonify({"status": "error", "message": "Invalid request format."}), 400

    tool = data['tool']
    arguments = data['arguments']

    if tool == 'get_jira_tickets':
        if 'jira_link' in arguments:
            result = get_jira_tickets(arguments['jira_link'])
            return jsonify(result)
        else:
            return jsonify({"status": "error", "message": "Missing 'jira_link' argument."}), 400
    elif tool == 'get_velocity_chart':
        if 'board_id' in arguments:
            result = get_velocity_chart(arguments['board_id'])
            return jsonify(result)
        else:
            return jsonify({"status": "error", "message": "Missing 'board_id' argument."}), 400
    else:
        return jsonify({"status": "error", "message": f"Tool '{tool}' not found."}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
  
