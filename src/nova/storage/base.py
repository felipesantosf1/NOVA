from abc import ABC, abstractmethod

# Qualquer problema ao guardar ou ler mensagens.
class StorageError(Exception):
    pass

# O contrato: o que qualquer "lugar de guardar mensagens" precisa saber fazer.
class MessageStorage(ABC):

    @abstractmethod
    # Devolve as últimas `limit` mensagens da conversa atual.
    def load_recent(self, limit: int) -> list[dict[str, str]]:
        pass

    @abstractmethod
    # Salva uma troca completa: a pergunta e a resposta.
    def add_exchange(self, user_message: str, answer: str) -> None:
        pass

    @abstractmethod
    # Começa uma conversa nova (é o que o comando "limpar" faz).
    def start_new_session(self) -> None:
        pass