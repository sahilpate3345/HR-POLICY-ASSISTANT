from typing import List, Any


class HRPolicySearchTool:
    name = "search_hr_policy"
    description = "Searches company HR policy handbook for relevant information."

    def __init__(self, retriever: Any):
        self.retriever = retriever

    def search(self, query: str) -> str:
        if hasattr(self.retriever, "invoke"):
            docs = self.retriever.invoke(query)
        elif hasattr(self.retriever, "get_relevant_documents"):
            docs = self.retriever.get_relevant_documents(query)
        else:
            docs = []
            
        if not docs:
            return "No relevant HR policy information found."
        formatted = []
        for i, doc in enumerate(docs, 1):
            sec = doc.metadata.get("section", "General")
            formatted.append(f"--- EXCERPT {i} (Section: {sec}) ---\n{doc.page_content}")
        return "\n\n".join(formatted)


def create_search_tool(retriever: Any) -> HRPolicySearchTool:
    """Creates a search tool from retriever."""
    return HRPolicySearchTool(retriever)
