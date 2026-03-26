import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def ask(question, store, history, min_score=0.1, debug=False):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    results = store.search(question, top_k=10)

    if not results:
        if debug:
            return "I couldn't find relevant information in the documents.", [], []
        return "I couldn't find relevant information in the documents.", []

    context = "\n\n".join([
        f"[Source: {c['source']} | Page {c['page']} | Score: {score:.4f}]\n{c['text']}"
        for (c, score) in results
    ])

    sources = list({f"{c['source']} (Page {c['page']})" for (c, _) in results})

    memory = ""
    if history:
        memory = "Previous conversation:\n"
        for turn in history[-4:]:
            memory += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    prompt = f"""{memory}
Document context:
{context}

Answer the question using ONLY the document context above.
Always cite which file and page number your answer comes from.
If the answer isn't in the documents, say so.

Question: {question}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2
    )

    if debug:
        return response.choices[0].message.content.strip(), sources, results

    return response.choices[0].message.content.strip(), sources