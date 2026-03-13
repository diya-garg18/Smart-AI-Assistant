import os
from dotenv import load_dotenv
from pdf_processor import process_pdf
from vector_store import VectorStore
from rag import ask

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def main():
    store = VectorStore()

    pdf_path = input("Enter path to your PDF file: ").strip()
    if not os.path.exists(pdf_path):
        print("File not found.")
        return

    print("Processing PDF...")
    chunks = process_pdf(pdf_path)
    store.add(chunks)
    print(f"Done. {len(chunks)} chunks loaded from your PDF.\n")

    history = []
    print("Ask questions about your PDF. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        answer, sources = ask(question, store, history)
        print(f"\nAnswer: {answer}")
        print(f"Sources: {sources}\n")

        history.append({"question": question, "answer": answer})

if __name__ == "__main__":
    main()
