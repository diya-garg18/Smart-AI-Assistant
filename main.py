import os
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
from pdf_processor import process_pdfs
from vector_store import VectorStore
from rag import ask

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def pick_files():
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Select PDF files",
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()
    return list(files)

def main():
    store = VectorStore()

    print("=== Smart AI Assistant v2 - Multiple PDFs ===\n")
    print("How do you want to load PDFs?")
    print("  1. Browse and select files (file picker)")
    print("  2. Type file paths manually")
    choice = input("\nEnter 1 or 2: ").strip()

    pdf_paths = []

    if choice == "1":
        print("\nA file picker window will open...")
        pdf_paths = pick_files()
        if not pdf_paths:
            print("No files selected.")
            return

    elif choice == "2":
        print("\nEnter PDF paths one by one. Press Enter with no input when done.")
        while True:
            path = input("PDF path: ").strip().strip('"')
            if not path:
                break
            if not os.path.exists(path):
                print(f"  File not found: {path}")
                continue
            if not path.lower().endswith(".pdf"):
                print(f"  Not a PDF: {path}")
                continue
            pdf_paths.append(path)
    else:
        print("Invalid choice.")
        return

    if not pdf_paths:
        print("No valid PDFs provided.")
        return

    print(f"\nLoading {len(pdf_paths)} PDF(s)...")
    chunks = process_pdfs(pdf_paths)
    store.add(chunks)

    print(f"\nDone. {len(chunks)} chunks loaded from {len(pdf_paths)} PDF(s).")
    for p in pdf_paths:
        print(f"  - {os.path.basename(p)}")

    print("\nAsk questions about your documents. Type 'exit' to quit.")
    print("Type 'sources' to see which PDFs are loaded.\n")

    history = []

    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if question.lower() == "sources":
            for p in pdf_paths:
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