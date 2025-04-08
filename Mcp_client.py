# mcp_client.py
import requests
import json
import base64
import os

SERVER_URL = "http://127.0.0.1:5000/execute_tool"  # Replace if your server is running elsewhere

def ask_question(question):
    """Takes a natural language question and interacts with the MCP server."""
    print(f"Question: {question}")

    # --- Simple Intent Recognition (Improve this for more complex queries) ---
    if "jira tickets" in question and "link" in question:
        # Assuming the user provides a Jira link in the question
        parts = question.split()
        for part in parts:
            if "browse" in part:
                jira_link = part
                payload = {
                    "tool": "get_jira_tickets",
                    "arguments": {"jira_link": jira_link}
                }
                response = requests.post(SERVER_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        print("Jira Tickets:", ", ".join(data["tickets"]))
                    else:
                        print("Error:", data["message"])
                    return
                else:
                    print("Error communicating with the server:", response.status_code)
                    return
        print("Could not find a valid Jira link in the question.")
        return

    elif "velocity chart" in question and "board" in question:
        # Assuming the user mentions a board ID
        parts = question.split()
        for part in parts:
            if part.isdigit():
                board_id = part
                payload = {
                    "tool": "get_velocity_chart",
                    "arguments": {"board_id": board_id}
                }
                response = requests.post(SERVER_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success" and "image" in data:
                        # Display the image (you might need a library like Pillow for more advanced display)
                        image_data = base64.b64decode(data["image"])
                        filename = "velocity_chart.png"
                        with open(filename, "wb") as f:
                            f.write(image_data)
                        print(f"Velocity chart saved to {filename}. Please open it to view.")
                        os.startfile(filename) # For Windows - adjust for other OS
                    else:
                        print("Error:", data["message"])
                    return
                else:
                    print("Error communicating with the server:", response.status_code)
                    return
        print("Could not find a valid board ID in the question.")
        return

    else:
        print("Sorry, I don't understand that question yet.")

if __name__ == "__main__":
    while True:
        user_input = input("Ask a question (or type 'exit'): ")
        if user_input.lower() == 'exit':
            break
        ask_question(user_input)
      
