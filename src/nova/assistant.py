from nova.ai.ollama_client import AIError, OllamaClient
from nova.config import (
    APP_NAME,
    FACTS_FILE,
    HISTORY_FILE,
    MAX_HISTORY_MESSAGES,
    SYSTEM_PROMPT,
    VERSION,
)
from nova.memory import Memory


class Assistant:
    def __init__(
        self,
        ai_client: OllamaClient | None = None,
        memory: Memory | None = None,
        ) -> None:
        self.name = APP_NAME
        self.version = VERSION

        self.ai_client = (
            ai_client if ai_client is not None else OllamaClient()
        )

        # A memória agora vem do disco, não começa mais vazia.
        self.memory = (
            memory
            if memory is not None
            else Memory(HISTORY_FILE, FACTS_FILE, MAX_HISTORY_MESSAGES)
        )

    def start(self) -> None:
        print(f"\n{self.name} v{self.version}")
        print("Assistente iniciada.")
        print("Digite 'ajuda' para ver os comandos.")

        # Avisa se encontrou uma conversa de antes.
        if self.memory.history:
            print(
                f"(Conversa anterior carregada: "
                f"{len(self.memory.history)} mensagens)"
            )
        print()

        while True:
            try:
                message = input("Você: ").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{self.name}: Até mais!")
                break

            if not message:
                continue

            # casefold() deixa tudo minúsculo, para "SAIR" e "sair"
            # funcionarem igual. Usado só para comparar comandos.
            command = message.casefold()

            if command in {"sair", "exit", "quit"}:
                print(f"{self.name}: Até mais!")
                break

            if command == "ajuda":
                self.show_help()
                continue

            if command in {"limpar", "limpar conversa"}:
                self.memory.clear_history()
                print(f"{self.name}: Contexto da conversa apagado.")
                continue

            # "lembrar <texto>" guarda um fato permanente.
            # Usamos `message` (e não `command`) para preservar
            # maiúsculas, tipo o seu nome.
            if command.startswith("lembrar "):
                fact = message[len("lembrar "):].strip()
                self.remember(fact)
                continue

            if command in {"memorias", "memórias"}:
                self.show_facts()
                continue

            if command in {"apagar memorias", "apagar memórias"}:
                self.memory.clear_facts()
                print(f"{self.name}: Memórias apagadas.")
                continue

            self.respond(message)
    # Monta o prompt do sistema, incluindo o que ela sabe de você.
    def build_system_prompt(self) -> str:
        prompt = SYSTEM_PROMPT.strip()

        if self.memory.facts:
            facts_text = "\n".join(f"- {fact}" for fact in self.memory.facts)
            prompt += (
                "\n\nInformações que o usuário pediu para você lembrar:\n"
                f"{facts_text}"
            )

        return prompt

    def respond(self, message: str) -> None:
        # A lista que a IA recebe: instruções + histórico + pergunta nova.
        # Repare que a pergunta nova ainda NÃO está no histórico salvo;
        # ela só entra lá se a resposta chegar completa.
        messages = [
            {"role": "system", "content": self.build_system_prompt()},
            *self.memory.history,
            {"role": "user", "content": message},
        ]

        # end="" evita pular linha; flush=True força o texto a aparecer
        # na hora, sem esperar o Python juntar mais texto para imprimir.
        print(f"{self.name}: ", end="", flush=True)

        parts: list[str] = []

        try:
            for piece in self.ai_client.stream_response(messages):
                print(piece, end="", flush=True)
                parts.append(piece)

        except AIError as exc:
            # Se deu erro, a pergunta não é salva no histórico.
            print(f"\n{self.name}: {exc}")
            return

        except KeyboardInterrupt:
            # Ctrl+C durante a resposta: interrompe só ela, sem fechar
            # o programa.
            print("\n[resposta interrompida]")
            return

        print()  # pula a linha ao final da resposta

        # Junta os pedaços numa resposta só.
        answer = "".join(parts).strip()

        if not answer:
            print(f"{self.name}: O modelo não retornou uma resposta válida.")
            return

        # Só agora, com a resposta completa, gravamos no histórico.
        self.memory.add_exchange(message, answer)

    def remember(self, fact: str) -> None:
        if not fact:
            print(f"{self.name}: O que você quer que eu lembre?")
            return

        if self.memory.add_fact(fact):
            print(f"{self.name}: Anotado! Vou lembrar disso.")
        else:
            print(f"{self.name}: Isso eu já sabia.")

    def show_facts(self) -> None:
        if not self.memory.facts:
            print(f"{self.name}: Ainda não tenho nada anotado sobre você.")
            return

        print(f"\n{self.name}: Isto é o que eu sei:")
        for number, fact in enumerate(self.memory.facts, start=1):
            print(f"{number}. {fact}")
        print()

    def show_help(self) -> None:
        print("\nComandos disponíveis:")
        print("- ajuda: mostra os comandos")
        print("- limpar: apaga o contexto da conversa")
        print("- lembrar <texto>: guarda uma informação sobre você")
        print("- memorias: mostra o que a NOVA sabe sobre você")
        print("- apagar memorias: esquece tudo que você pediu pra lembrar")
        print("- sair: encerra a NOVA\n")