from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import LLM_MODEL_NAME, LLM_TEMPERATURE, GOOGLE_API_KEY
from src.retriever import TrafficLawRetriever


def format_docs(docs):
    """Format tài liệu tìm được"""
    formatted = []
    for doc in docs:
        source = doc.metadata.get("source", "N/A")
        article = doc.metadata.get("dieu", "")
        title = doc.metadata.get("tieu_de_dieu", "")
        formatted.append(
            f"Nguồn: {source} | {article}. {title}\nNội dung: {doc.page_content}"
        )
    return "\n\n".join(formatted)


class TrafficLawChatbot:
    def __init__(self):
        self.retriever = TrafficLawRetriever()

        if not GOOGLE_API_KEY:
            raise ValueError("Vui lòng điền GOOGLE_API_KEY trong file src/config.py")

        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            temperature=LLM_TEMPERATURE,
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True,
        )

        # --- 1. PROMPT ĐỊNH TUYẾN (ROUTER) ---
        self.router_prompt = ChatPromptTemplate.from_template(
            """
        Bạn là hệ thống phân loại câu hỏi cho Chatbot Luật Giao thông.
        Hãy phân tích câu hỏi của người dùng và chọn 1 trong 3 nhãn sau:
        
        1. "LAW": Nếu câu hỏi liên quan đến luật giao thông, mức phạt, biển báo, quy định lái xe, tai nạn, giấy tờ xe.
        2. "SOCIAL": Nếu là câu chào hỏi, hỏi tên bot, cảm ơn, tạm biệt hoặc câu hỏi "Tôi là ai" (mang tính cá nhân/xã giao).
        3. "OTHER": Các câu hỏi không liên quan đến luật giao thông (nấu ăn, code, toán học, chính trị, thời tiết...).

        Chỉ trả về đúng 1 từ nhãn (LAW, SOCIAL, hoặc OTHER).

        Câu hỏi: {question}
        Nhãn:
        """
        )

        # --- 2. PROMPT XÃ GIAO (CHAT) ---
        self.social_prompt = ChatPromptTemplate.from_template(
            """
        Bạn là Trợ lý Luật Giao thông thông minh.
        Người dùng hỏi: "{question}"
        
        Hãy trả lời thân thiện, ngắn gọn. 
        Nếu người dùng hỏi "Tôi là ai?", hãy nói đùa nhẹ nhàng rằng bạn là AI nên không biết danh tính của họ, nhưng rất vui được hỗ trợ.
        Luôn nhắc khéo người dùng rằng bạn ở đây để hỗ trợ tra cứu luật giao thông.
        """
        )

        # --- 3. PROMPT TRA CỨU LUẬT (RAG) ---
        self.law_prompt = ChatPromptTemplate.from_template(
            """
        Bạn là chuyên gia Luật Giao thông Việt Nam.
        Dựa vào ngữ cảnh sau, hãy trả lời câu hỏi.

        <Dữ liệu luật>:
        {context}

        <Câu hỏi>: {question}

        Yêu cầu:
        - Trả lời chính xác, trích dẫn Điều/Khoản cụ thể có trong ngữ cảnh.
        - Nếu ngữ cảnh không có thông tin, hãy nói "Hiện tại cơ sở dữ liệu của tôi chưa cập nhật quy định này".
        """
        )

        # --- 4. PROMPT TỪ CHỐI (OFF-TOPIC) ---
        self.refusal_prompt = ChatPromptTemplate.from_template(
            """
        Người dùng hỏi về chủ đề không liên quan: "{question}"
        Hãy từ chối lịch sự và nói rằng bạn chỉ chuyên về Luật Giao thông đường bộ Việt Nam.
        """
        )

    def ask(self, question):
        # BƯỚC 1: ĐỊNH TUYẾN (ROUTER)
        # Chỉ print log để debug, không dùng rich ở đây
        print(f"--- [DEBUG] Router phân loại: '{question}' ---")
        router_chain = self.router_prompt | self.llm | StrOutputParser()
        topic = router_chain.invoke({"question": question}).strip().upper()

        print(f"--- [DEBUG] Chủ đề: {topic} ---")

        if "LAW" in topic:
            # Tìm kiếm (Retriever)
            relevant_docs = self.retriever.search(question, k=10)

            if not relevant_docs:
                return (
                    "Xin lỗi, tôi không tìm thấy văn bản luật nào phù hợp trong dữ liệu.",
                    [],
                )

            context_text = format_docs(relevant_docs)

            # Trả lời (Generator)
            rag_chain = self.law_prompt | self.llm | StrOutputParser()
            response = rag_chain.invoke({"context": context_text, "question": question})

            # Lấy nguồn
            sources = list(
                set([doc.metadata.get("source", "Unknown") for doc in relevant_docs])
            )

            return response, sources

        elif "SOCIAL" in topic:
            social_chain = self.social_prompt | self.llm | StrOutputParser()
            response = social_chain.invoke({"question": question})

            return response, []

        else:
            refusal_chain = self.refusal_prompt | self.llm | StrOutputParser()
            response = refusal_chain.invoke({"question": question})

            return response, []
