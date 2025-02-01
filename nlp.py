import openai
import yaml

# Set your OpenAI API Key
openai.api_key = "your-openai-api-key"

def generate_spheron_yaml(user_prompt):
    """
    Converts natural language input into Spheron YAML.
    """
    system_prompt = "You are an expert in Spheron ICL YAML. Convert user requests into valid YAML."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    yaml_output = response["choices"][0]["message"]["content"]

    # Validate if YAML is correct
    try:
        yaml.safe_load(yaml_output)  # Ensure it’s valid YAML
        return yaml_output
    except yaml.YAMLError as e:
        return f"Invalid YAML generated: {e}"

# Example test
user_input = "I want a Node.js service with auto-scaling and 1 GB of memory."
print(generate_spheron_yaml(user_input))
