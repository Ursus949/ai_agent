import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    agent_loop(client, messages, verbose)


def generate_content(client, messages, verbose):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        if verbose:
            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
            print("Response tokens:", response.usage_metadata.candidates_token_count)

        return response

    except ClientError as e:
        print(f"\nError: {e}")
        if "RESOURCE_EXHAUSTED" in str(e):
            retry_time = 15  # Default retry delay
            print(f"Rate limit hit. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return generate_content(client, messages, verbose)
        else:
            raise


def agent_loop(client, messages, verbose):
    for _ in range(20):
        response = generate_content(client, messages, verbose)

        for candidate in response.candidates:
            messages.append(candidate.content)

        if not response.function_calls and response.text:
            print("\nFinal response:")
            print(response.text)
            break

        for function_call in response.function_calls:
            messages.append(
                types.Content(
                    role="model",
                    parts=[
                        types.Part.from_function_call(
                            name=function_call.name,
                            args=function_call.args,
                        )
                    ],
                )
            )

            function_result = call_function(function_call, verbose=verbose)

            if (
                not function_result.parts
                or not hasattr(function_result.parts[0], "function_response")
                or not function_result.parts[0].function_response
            ):
                raise RuntimeError("Fatal error: No function response from tool")

            output = function_result.parts[0].function_response.response.get("result") \
                     or str(function_result.parts[0].function_response.response)

            if verbose:
                print("->", output)

            print("\nTool Response:")
            print(output)

            messages.append(function_result)
    else:
        print("Stopping after 20 interaction rounds to avoid infinite loop.")


if __name__ == "__main__":
    main()

