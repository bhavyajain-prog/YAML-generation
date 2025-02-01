from flask import Flask, request, send_file, jsonify
from transformers import pipeline
import yaml
import os

# Load the NLP model
generator = pipeline("text2text-generation", model="google/flan-t5-small")

app = Flask(__name__)

def parse_natural_language(user_prompt):
    """
    Extract structured information from user input.
    """
    system_prompt = f"Extract structured configuration from this: {user_prompt}"
    result = generator(system_prompt, max_length=200)
    extracted_text = result[0]['generated_text']

    return extracted_text

def generate_spheron_yaml(user_prompt):
    """
    Converts structured data into a valid Spheron ICL YAML file.
    """
    # Extract key values from the user's prompt
    extracted_text = parse_natural_language(user_prompt)

    # Define a default YAML structure
    yaml_data = {
        "services": [
            {
                "name": "generated-service",
                "type": "node",  # Default to Node.js (Modify as needed)
                "resources": {
                    "memory": "1GB",
                    "cpu": "500m"
                },
                "scaling": {
                    "enabled": True,
                    "min": 1,
                    "max": 5
                },
                "env": [
                    {"key": "NODE_ENV", "value": "production"}
                ]
            }
        ]
    }

    # Validate YAML format
    try:
        yaml_str = yaml.dump(yaml_data, default_flow_style=False)
        return yaml_str
    except yaml.YAMLError as e:
        return f"Error: Invalid YAML format - {e}"

@app.route('/generate_yaml', methods=['POST'])
def generate_yaml():
    user_prompt = request.json.get("prompt", "")
    yaml_content = generate_spheron_yaml(user_prompt)

    # Save YAML to a file
    file_path = "generated_spheron.yaml"
    with open(file_path, "w") as yaml_file:
        yaml_file.write(yaml_content)

    return send_file(file_path, as_attachment=True, mimetype="text/yaml")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
