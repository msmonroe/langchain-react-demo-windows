import json
from textwrap import dedent

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma


PROMPT = dedent(
    """
    You are a helpful pharmaceutical sales representative.
    Use only the provided drug context to answer the customer question.
    Always mention a drug's side effects alongside its indication.
    If the context does not contain the answer, say you do not know.

    Context:
    {context}

    Question: {question}
    Answer:
    """
).strip()


def load_texts():
    with open("drug_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    formatted = []
    for row in data:
        name = row.get("name", "Unknown drug")
        indication = row.get("indication") or row.get("description") or ""
        side_effects = row.get("side_effects")
        if isinstance(side_effects, list):
            side_effects_text = ", ".join(side_effects)
        elif side_effects:
            side_effects_text = str(side_effects)
        else:
            side_effects_text = "not specified"

        formatted.append(
            f"{name}: {indication} Side effects: {side_effects_text}."
        )

    return formatted


def ask_question(query: str) -> str:
    texts = load_texts()
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_texts(texts, embeddings)
    docs = db.similarity_search(query, k=4)
    context = "\n".join(doc.page_content for doc in docs)
    llm = OpenAI(temperature=0)
    prompt = PROMPT.format(context=context, question=query)
    return llm.invoke(prompt).strip()
