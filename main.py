import sys
import argparse

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from hr_assistant.pipeline import build_hr_assistant, ask


def main():
    parser = argparse.ArgumentParser(description="Acme Corp HR Policy Assistant")
    parser.add_argument("--query", "-q", type=str, help="Single query to ask the HR Policy Assistant")
    parser.add_argument("--file", "-f", type=str, help="Custom document path to load dynamically")
    args = parser.parse_args()

    print("Initializing dynamic HR Policy Assistant...")
    agent = build_hr_assistant(file_path=args.file) if args.file else build_hr_assistant()

    if args.query:
        print(f"\nQuery: {args.query}\n")
        answer = ask(agent, args.query)
        print(f"Assistant Answer:\n{answer}")
    else:
        print("\nSystem initialized! Type your query (type 'exit' to stop):\n")
        while True:
            try:
                user_input = input("Employee Query: ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    break
                answer = ask(agent, user_input)
                print(f"\nAssistant Answer:\n{answer}\n")
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
