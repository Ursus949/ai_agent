import os
import sys
import json
from google.genai import types
from google import genai
from dotenv import load_dotenv

from prompts import system_prompt
from call_function import available_functions
from functions.get_files_info import get_files_info, schema_get_files_info

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Agent")
        print('Usage: python3 main.py <"Your prompt here"> [--verbose]')
        print('Example: python3 main.py "How do I clean a cast iron skillet?"')
        sys.exit(1)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}")

    messages = [
            types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    available_functions = types.Tool(
            function_declarations=[schema_get_files_info]
    )
    generate_content(client, messages, verbose, available_functions)

def generate_content(client, messages, verbose, available_functions):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt)
    )

    if response.candidates and response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call:
            fn_name = part.function_call.name
            try:
                args = part.function_call.args or "{}"
            except Exception as e:
                print(f"Error parsing arguments: {e}")
                args = {}

            print(f"Calling function: {fn_name}({args})")

            # Execute the function if it's known
            if fn_name == "get_files_info":
                directory = args.get("directory", ".") or "."
                result = get_files_info("calculator", directory)
                print("Response:")
                print(result)
            else:
                print(f"Unknown function: {fn_name}")
        else:
            print("Response:")
            print(response.text)
    else:
        print("No response generated.")

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    main()
