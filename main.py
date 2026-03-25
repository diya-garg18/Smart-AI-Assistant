import os
from dotenv import load_dotenv
from files_processor import process_files
from vector_store import VectorStore
from rag import ask

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def main():
    store = VectorStore()

    print("=== Smart AI Assistant v5 - PDF + Word + TXT + PPT ===\n")

    # 👉 Only terminal input now
    paths = input("Enter file paths (comma separated): ").strip()
    file_paths = [p.strip().strip('"') for p in paths.split(",")]

    valid_paths = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
        if not path.lower().endswith((".pdf", ".docx", ".txt", ".pptx")):
            print(f"Unsupported file type: {path}")
            continue
        valid_paths.append(path)

    file_paths = valid_paths

    if not file_paths:
        print("No valid files provided.")
        return

    print(f"\nLoading {len(file_paths)} file(s)...")
    chunks = process_files(file_paths)
    store.add(chunks)

    print(f"\nDone. {len(chunks)} chunks loaded.")
    for p in file_paths:
        print(f"  - {os.path.basename(p)}")

    print("\nAsk questions about your documents. Type 'exit' to quit.")
    print("Type 'sources' to see loaded files.\n")

    history = []

    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if question.lower() == "sources":
            for p in file_paths:
                print(f"  - {os.path.basename(p)}")
            print()
            continue
        if not question:
            continue

        answer, sources = ask(question, store, history)
        print(f"\nAnswer: {answer}")
        print(f"Sources: {sources}\n")

        history.append({"question": question, "answer": answer})

if __name__ == "__main__":
    main()