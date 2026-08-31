from typing import List, Dict, Any

SYSTEM_PROMPT = """You are the official HR Policy Assistant for Acme Corp.
Your responsibility is to assist employees by providing accurate, clear, and professional answers based ONLY on the official HR Policy Document excerpts provided.

Guidelines:
1. If the user's message is "hii" (case-insensitive), respond exactly with "HR Policy Assistant: How can I assist you?". For other greetings or pleasantries (like "hi", "hello", "hey", "good morning", etc.), respond politely and ask how you can help them with the HR policy document, without requiring facts from the policy excerpts.
2. Ground every factual answer directly in the provided policy excerpts.
3. Provide ONLY the direct answer. Do NOT include section names, section numbers, citations, or source tags.
4. Be concise, clear, and professional.
5. If the provided context does not contain enough information to answer a factual policy question, state: "Based on the available HR policy document, I do not have enough details to answer this. Please reach out to HR directly."
"""


class MessageContent:
    def __init__(self, content: str):
        self.content = content


class HRAgentExecutor:
    def __init__(self, llm: Any, tools: List[Any]):
        self.llm = llm
        self.tools = tools
        self.search_tool = tools[0] if tools else None

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes query against LLM dynamically.
        Supports input format:
        - {"messages": [{"role": "user", "content": "..."}]}
        - {"input": "..."}
        """
        messages_input = input_data.get("messages", [])
        if messages_input:
            user_question = messages_input[-1].get("content", "")
        else:
            user_question = input_data.get("input", "")

        context = ""
        if self.search_tool:
            context = self.search_tool.search(user_question)

        prompt_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Policy Excerpts:\n{context}\n\nQuestion: {user_question}"}
        ]

        response_content = self.llm.invoke(prompt_messages)
        return {
            "output": response_content,
            "messages": [MessageContent(response_content)]
        }


def create_hr_agent(llm: Any, tools: List[Any]) -> HRAgentExecutor:
    """Creates dynamic HR Agent instance."""
    return HRAgentExecutor(llm, tools)
