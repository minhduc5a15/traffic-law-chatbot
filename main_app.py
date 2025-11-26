from src.chatbot import TrafficLawChatbot
import os

def main():
    # Xoa man hinh cho sach
    os.system('clear' if os.name == 'posix' else 'cls')

    print("=== CHATBOT LUAT GIAO THONG (Ver 1.0) ===")
    print("Dang khoi dong he thong...")

    bot = TrafficLawChatbot()

    print("\nHe thong da san sang! (Go 'exit' de thoat)")

    while True:
        try:
            question = input("\n[BAN]: ")
            if question.lower() in ['exit', 'quit']:
                print("Tam biet!")
                break

            if not question.strip():
                continue

            response, sources = bot.ask(question)

            print(f"\n[BOT]: {response}")
            print("\n--- Nguon tham khao ---")
            for src in sources:
                print(f"- {os.path.basename(src)}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Da xay ra loi: {e}")

if __name__ == "__main__":
    main()