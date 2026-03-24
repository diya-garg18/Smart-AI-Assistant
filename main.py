import os
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
from pdf_processor import process_files
from vector_store import VectorStore
from rag import ask

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def pick_files():
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Select files",
        filetypes=[
            ("Supported files", "*.pdf *.docx *.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Text files", "*.txt"),
        ]
    )
    root.destroy()
    return list(files)

def main():
    store = VectorStore()

    print("=== Smart AI Assistant v4 - PDF + Word + TXT ===\n")
    print("How do you want to load files?")
    print("  1. Browse and select files (file picker)")
    print("  2. Type file paths manually")
    choice = input("\nEnter 1 or 2: ").strip()

    file_paths = []

    if choice == "1":
        print("\nA file picker window will open...")
        file_paths = pick_files()
        if not file_paths:
            print("No files selected.")
            return

    elif choice == "2":
        print("\nEnter file paths one by one. Press Enter with no input when done.")
        while True:
            path = input("File path: ").strip().strip('"')
            if not path:
                break
            if not os.path.exists(path):
                print(f"  File not found: {path}")
                continue
            if not path.lower().endswith((".pdf", ".docx", ".txt")):
                print(f"  Unsupported file type (use .pdf, .docx, .txt): {path}")
                continue
            file_paths.append(path)
    else:
        print("Invalid choice.")
        return

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