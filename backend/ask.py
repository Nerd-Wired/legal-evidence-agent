import sys

from backend.agent.graph import build_agent
from backend.vector_store import close_vector_store


def main():
    question = " ".join(sys.argv[1:]) or "What is the total contract value?"

    try:
        agent = build_agent()

        result = agent.invoke({
            "question": question,
            "retrieved_chunks": [],
            "answer": "",
            "evidence_sufficient": False,
            "citations_valid": False,
            "retry_count": 0,
            "citation_feedback": "",
            "error": ""
        })

        scores = [c["semantic_score"] for c in result["retrieved_chunks"]]

        print("\nQUESTION:")
        print(result["question"])

        print("\nBEST SEMANTIC SCORE:")
        print(round(max(scores, default=0.0), 3))

        print("\nANSWER:")
        if result["evidence_sufficient"]:
            print("\nCITATIONS VALID:")
            print(result["citations_valid"], "| failed checks:", result["retry_count"])
        print(result["answer"])

        print("\nERROR:")
        print(result["error"])

    finally:
        close_vector_store()


if __name__ == "__main__":
    main()