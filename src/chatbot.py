from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.config import LLM_MODEL_NAME, LLM_TEMPERATURE
from src.retriever import TrafficLawRetriever


class TrafficLawChatbot:
    def __init__(self):
        self.retriever = TrafficLawRetriever()

        # Khoi tao LLM
        print(f"Dang khoi tao LLM ({LLM_MODEL_NAME})...")
        self.llm = ChatOllama(
            model=LLM_MODEL_NAME,
            temperature=LLM_TEMPERATURE
        )

        # Tao Prompt Template (Khuon mau cau hoi)
        self.prompt = ChatPromptTemplate.from_template("""
        Bạn là trợ lý AI am hiểu về Luật Giao thông Việt Nam. 
        Dựa vào các đoạn văn bản luật được cung cấp dưới đây, hãy trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn và dễ hiểu.
        Nếu thông tin không có trong văn bản được cung cấp, hãy nói "Tôi chưa tìm thấy thông tin này trong dữ liệu luật hiện có".
        
        <Thông tin luật>:
        {context}
        
        <Câu hỏi>: {question}
        
        Trả lời:
        """)

    def format_docs(self, docs):
        """Ghep noi dung cac doan van ban tim duoc thanh 1 chuoi"""
        return "\n\n".join(doc['content'] for doc in docs)

    def ask(self, question):
        """Ham xu ly chinh: Nhan cau hoi -> Tim kiem -> Tra loi"""
        # 1. Tim kiem
        print(f"Dang tim kiem thong tin cho: '{question}'...")
        relevant_docs = self.retriever.search(question, k=3)

        if not relevant_docs:
            return "Xin lỗi, tôi không tìm thấy văn bản luật nào liên quan."

        # 2. Xay dung Context
        context_text = self.format_docs(relevant_docs)

        # 3. Gui cho LLM
        print("Dang suy nghi cau tra loi...")
        chain = ({"context": lambda x: context_text,
                  "question": lambda x: question} | self.prompt | self.llm | StrOutputParser())

        response = chain.invoke(question)

        # Tra ve kem theo nguon tham khao
        sources = list(set([doc['source'] for doc in relevant_docs]))
        return response, sources
