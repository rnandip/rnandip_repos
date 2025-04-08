# mcp_client_llm.py
import requests
import json
import base64
import os
from openai import OpenAI  # Or your preferred LLM library

SERVER_URL = "http://127.0.0.1:5000/execute_tool"  # Replace if your server is running elsewhere
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key

client = OpenAI(api_key=OPENAI_API_KEY)

def get_llm_response(prompt):
    """Sends a prompt to the LLM and returns the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or your preferred model
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        return None

def ask_question(question):
    """Takes a natural language question, uses LLM to determine intent, and interacts with the MCP server."""
    print(f"Question: {question}")

    # --- LLM for Intent Recognition and Parameter Extraction ---
    prompt = f"""You are an intelligent agent that understands user questions related to Jira tickets and reports.
Your goal is to identify the user's intent and extract the necessary information to call specific tools.

Available Tools:
1. get_jira_tickets: Retrieves a list of Jira ticket keys for a given Jira project link.
   - Requires argument: 'jira_link' (the full Jira issue link, e.g., 'YOUR_JIRA_SERVER_URL/browse/PROJECT-123').
2. get_velocity_chart: Generates a velocity chart for a given Jira Agile board ID.
   - Requires argument: 'board_id' (the numerical ID of the Jira Agile board).

For the user's question: "{question}"

Determine the most likely tool and the corresponding arguments. Respond with a JSON object in the following format:
{{
  "tool": "tool_name",
  "arguments": {{
    "arg_name": "arg_value",
    "...": "..."
  }}
}}

If you cannot identify a valid tool or extract the necessary arguments, respond with:
{{
  "tool": null,
  "arguments": null
}}
"""

    llm_response_str = get_llm_response(prompt)

    if llm_response_str:
        try:
            action_data = json.loads(llm_response_str)
            tool = action_data.get("tool")
            arguments = action_data.get("arguments")

            if tool and arguments:
                print(f"LLM identified tool: {tool} with arguments: {arguments}")
                payload = {"tool": tool, "arguments": arguments}
                response = requests.post(SERVER_URL, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        if tool == "get_jira_tickets":
                            print("Jira Tickets:", ", ".join(data["tickets"]))
                        elif tool == "get_velocity_chart" and "image" in data:
                            image_data = base64.b64decode(data["image"])
                            filename = "velocity_chart.png"
                            with open(filename, "wb") as f:
                                f.write(image_data)
                            print(f"Velocity chart saved to {filename}. Please open it to view.")
                            os.startfile(filename) # For Windows - adjust for other OS
                        else:
                            print("Response from server:", data)
                    else:
                        print("Error from server:", data["message"])
                else:
                    print("Error communicating with the server:", response.status_code)
            else:
                print("LLM could not identify a valid tool and arguments.")

        except json.JSONDecodeError:
            print("Error decoding LLM response:", llm_response_str)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("Could not get a response from the LLM.")

if __name__ == "__main__":
    while True:
        user_input = input("Ask a question (or type 'exit'): ")
        if user_input.lower() == 'exit':
            break
        ask_question(user_input)
