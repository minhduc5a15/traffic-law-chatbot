from src.chatbot import TrafficLawChatbot
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def main():
    os.system("clear" if os.name == "posix" else "cls")

    console.print("[bold cyan]=== CHATBOT LUAT GIAO THONG (Ver 1.0) ===[/bold cyan]")
    console.print("Đang khởi động hệ thống...\n")

    bot = TrafficLawChatbot()

    console.print(
        "[bold green]Hệ thống đã sẵn sàng! (Gõ 'exit' để thoát)[/bold green]\n"
    )

    while True:
        try:
            question = console.input("[bold yellow][BAN]: [/bold yellow]")
            if question.lower() in ["exit", "quit"]:
                console.print("[bold red]Tạm biệt![/bold red]")
                break

            if not question.strip():
                continue

            response, sources = bot.ask(question)

            md = Markdown(response)
            console.print(
                Panel(md, title="[BOT]", title_align="left", border_style="blue")
            )

            if sources:
                console.print("\n[bold magenta]Nguồn tham khảo:[/bold magenta]")
                for src in sources:
                    console.print(f"- {os.path.basename(src)}")

        except KeyboardInterrupt:
            console.print("\n[bold red]Tạm biệt![/bold red]")
            break
        except Exception as e:
            console.print(f"[bold red]Đã xảy ra lỗi:[/bold red] {e}")


if __name__ == "__main__":
    main()
