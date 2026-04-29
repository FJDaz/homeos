#!/usr/bin/env python3
import os
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load defaults from .env
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Qwen CLI - Interact with Qwen models (Local/Cloud)")
    parser.add_argument("prompt", nargs="?", help="The prompt to send to the model")
    parser.add_argument("--local", action="store_true", help="Use local Ollama (http://localhost:11434/v1)")
    parser.add_argument("--model", help="Model name (e.g., qwen-plus, qwen2.5-7b-instruct)")
    parser.add_argument("--key", help="API Key (overrides env)")
    parser.add_argument("--url", help="Base URL (overrides env)")
    parser.add_argument("--stream", action="store_true", default=True, help="Enable streaming (default: True)")
    parser.add_argument("--no-stream", dest="stream", action="store_false", help="Disable streaming")

    args = parser.parse_args()

    # Determine Base URL
    if args.local:
        base_url = "http://localhost:11434/v1"
        api_key = args.key or os.environ.get("QWEN_LOCAL_API_KEY", "ollama")
        model = args.model or os.environ.get("QWEN_LOCAL_MODEL", "qwen2.5")
    else:
        # Defaults for Cloud
        base_url = args.url or os.environ.get("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        api_key = args.key or os.environ.get("QWEN_API_KEY") or os.environ.get("QWEN_KEY")
        model = args.model or os.environ.get("QWEN_MODEL", "qwen-turbo")

    if not api_key and not args.local:
        print("Error: QWEN_API_KEY not found in environment. Please set it or use --key.")
        sys.exit(1)

    # If no prompt, read from stdin
    prompt = args.prompt
    if not prompt:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(0)

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=args.stream,
        )

        if args.stream:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()
        else:
            print(response.choices[0].message.content)

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
