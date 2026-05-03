from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

def main():
    print("Hello from c1-t2-hello-world-app!")
    print(f"API Key: {os.getenv('OPENAI_API_KEY')}")

if __name__ == "__main__":
    main()
