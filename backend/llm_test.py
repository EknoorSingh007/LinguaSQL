from llm_interface import parse_prompt

prompt = "Add a new user named Alice from India"
parsed = parse_prompt(prompt)

print("Parsed LLM Output:")
print(parsed)
