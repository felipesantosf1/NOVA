# Importa a classe Assistant
from nova.assistant import Assistant

#Cria a assistente e a coloca para funcionar.
def main():
    # Cria o objeto Assistant.
    assistant = Assistant()

    # Inicia o ciclo de conversa no terminal.
    assistant.start()


if __name__ == "__main__":
    main()