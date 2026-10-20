from nova.ai.ollama_client import AIError, OllamaClient
from nova.config import (
    APP_NAME,
    MAX_HISTORY_MESSAGES,
    SYSTEM_PROMPT,
    VERSION,
)

class Assistant:
    def __init__(
        self,
        ai_client: OllamaClient | None = None,
    ) -> None:
        self.name = APP_NAME
        self.version = VERSION

        self.ai_client = (
            ai_client if ai_client is not None else OllamaClient()
        )

        # Histórico temporário da conversa.
        self.history: list[dict[str, str]] = []

    def start(self) -> None:
        print(f"\n{self.name} v{self.version}")
        print("Assistente iniciada.")
        print("Digite 'ajuda' para ver os comandos.")
        print("Digite 'limpar' para apagar o contexto da conversa.")
        print("Digite 'sair' para encerrar.\n")

        while True:
            try:
                message = input("Você: ").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{self.name}: Até mais!")
                break

            if not message:
                continue

            command = message.casefold()

            if command in {"sair", "exit", "quit"}:
                print(f"{self.name}: Até mais!")
                break

            if command == "ajuda":
                self.show_help()
                continue

            if command in {"limpar", "limpar conversa"}:
                self.history.clear()
                print(f"{self.name}: Contexto da conversa apagado.")
                continue

            self.respond(message)

    def respond(self, message: str) -> None:
        self.history.append({
            "role": "user",
            "content": message,
        })

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            *self.history,
        ]

        try:
            answer = self.ai_client.generate_response(messages)

        except AIError as exc:
            # Remove a pergunta que não obteve resposta.
            self.history.pop()
            print(f"{self.name}: {exc}")
            return

        self.history.append({
            "role": "assistant",
            "content": answer,
        })

        # Mantém somente as mensagens mais recentes.
        if len(self.history) > MAX_HISTORY_MESSAGES:
            del self.history[:-MAX_HISTORY_MESSAGES]

        print(f"{self.name}: {answer}")

    def show_help(self) -> None:
        print("\nComandos disponíveis:")
        print("- ajuda: mostra os comandos")
        print("- limpar: apaga o contexto da conversa")
        print("- sair: encerra a NOVA\n")