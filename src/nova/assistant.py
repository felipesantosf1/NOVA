from nova.config import APP_NAME, VERSION


class Assistant:
    def __init__(self):
        self.name = APP_NAME
        self.version = VERSION

    def start(self):
        print(f"\n{self.name} v{self.version}")
        print("Assistente iniciada.")
        print("Digite 'ajuda' para ver os comandos.")
        print("Digite 'sair' para encerrar.\n")

        while True:
            message = input("Você: ").strip()

            if not message:
                continue

            command = message.casefold()

            if command in {"sair", "exit", "quit"}:
                print(f"{self.name}: Até mais!")
                break

            if command == "ajuda":
                self.show_help()
                continue

            print(
                f"{self.name}: Ainda estou em desenvolvimento. "
                "Minha inteligência artificial será integrada "
                "na próxima etapa."
            )

    def show_help(self):
        print("\nComandos disponíveis:")
        print("- ajuda: mostra os comandos")
        print("- sair: encerra a NOVA\n")