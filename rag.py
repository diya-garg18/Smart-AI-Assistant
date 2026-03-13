import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def ask(question, store, history):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    results = store.search(question)

    if not results:
        return "I couldn't find relevant information in the document.", []

    context = "\n\n".join([f"[Page {c['page']}] {c['text']}" for c, _ in results])
    sources = list(set([f"Page {c['page']}" for c, _ in results]))

    memory = ""
    if history:
        memory = "Previous conversation:\n"
        for turn in history[-4:]:
            memory += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    prompt = f"""{memory}
Document context:
{context}

Answer the question using ONLY the document context above. Cite page numbers.
If the answer isn't in the document, say so.

Question: {question}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2
    )

    return response.choices[0].message.content.strip(), sources