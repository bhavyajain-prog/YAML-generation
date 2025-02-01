from flask import Flask, request, send_file, jsonify
from transformers import pipeline
import yaml
import os
import re

# Load the NLP model
generator = pipeline("text2text-generation", model="google/flan-t5-large")

app = Flask(__name__)

def extract_configuration(user_prompt):
    """
    Extract structured YAML from user prompt using the model.
    """
    # Enhanced system prompt to encourage structured output
    system_prompt = f"Generate a valid YAML configuration based on the following input: Input: {user_prompt} Make sure the output strictly follows YAML format. Include key-value pairs and proper indentation."

    result = generator(system_prompt, max_length=300)

    extracted_text = result[0]['generated_text']
    print("Raw model output:\n", extracted_text)



    try:
        # Try parsing the generated text as YAML
        config = yaml.safe_load(extracted_text)
        return config if isinstance(config, dict) else {}
    except yaml.YAMLError as e:
        print(f"YAML Parsing Error: {e}")
        return {}

def generate_spheron_yaml(user_prompt):
    """
    Converts extracted configuration into valid Spheron YAML format.
    """
    extracted_data = extract_configuration(user_prompt)

    # Ensure extracted data is not empty before proceeding
    if not extracted_data:
        return "Error: Failed to extract valid configuration from the prompt."

    # Ensure the output structure matches Spheron YAML specs
    yaml_data = {
        "services": [
            {
                "name": extracted_data.get("service", "default-service"),
                "resources": {
                    "memory": extracted_data.get("memory", "1GB"),
                    "cpu": extracted_data.get("cpu", "500m"),
                },
                "scaling": {
                    "enabled": extracted_data.get("scaling", {}).get("enabled", False),
                    "min": extracted_data.get("scaling", {}).get("min_instances", 1),
                    "max": extracted_data.get("scaling", {}).get("max_instances", 5),
                },
                "env": extracted_data.get("env", {})
            }
        ]
    }

    try:
        # Convert dictionary into YAML format
        yaml_str = yaml.dump(yaml_data, default_flow_style=False)
        return yaml_str
    except yaml.YAMLError as e:
        return f"Error: Invalid YAML format - {e}"

@app.route('/generate_yaml', methods=['POST'])
def generate_yaml():
    user_prompt = request.json.get("prompt", "")
    if not user_prompt:
        return jsonify({"error": "Missing prompt in the request"}), 400

    yaml_content = generate_spheron_yaml(user_prompt)

    # Check if the YAML content is an error message
    if "Error" in yaml_content:
        return jsonify({"error": yaml_content}), 400

    # Save YAML to a file
    file_path = "generated_spheron.yaml"
    with open(file_path, "w") as yaml_file:
        yaml_file.write(yaml_content)

    return send_file(file_path, as_attachment=True, mimetype="text/yaml")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
