
from nova.ai.ollama_client import AIConnectionError
from nova.assistant import Assistant
from nova.config import SYSTEM_PROMPT


class FakeAIClient:
    """Simula respostas da IA sem acessar o Ollama."""

    def __init__(self, results: list[str | Exception] | None = None):
        self.results = list(results or [])
        self.calls = []

    def generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        self.calls.append([message.copy() for message in messages])

        result = self.results.pop(0)

        if isinstance(result, Exception):
            raise result

        return result


def test_ajuda_pode_ser_repetida(monkeypatch, capsys):
    entradas = iter(["ajuda", "ajuda", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    cliente = FakeAIClient()
    assistant = Assistant(ai_client=cliente)

    assistant.start()

    saida = capsys.readouterr().out

    assert saida.count("Comandos disponíveis:") == 2
    assert saida.count("- limpar:") == 2
    assert cliente.calls == []


def test_historico_e_enviado_para_a_ia(monkeypatch):
    entradas = iter([
        "Meu nome é Felipe.",
        "Qual é o meu nome?",
        "sair",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    cliente = FakeAIClient([
        "Prazer, Felipe!",
        "Seu nome é Felipe.",
    ])
    assistant = Assistant(ai_client=cliente)

    assistant.start()

    assert len(cliente.calls) == 2

    segunda_conversa = cliente.calls[1]

    assert segunda_conversa == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Meu nome é Felipe."},
        {"role": "assistant", "content": "Prazer, Felipe!"},
        {"role": "user", "content": "Qual é o meu nome?"},
    ]


def test_limpar_apaga_o_contexto(monkeypatch):
    entradas = iter([
        "Meu nome é Felipe.",
        "limpar",
        "Qual é o meu nome?",
        "sair",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    cliente = FakeAIClient([
        "Entendi.",
        "Não tenho essa informação nesta conversa.",
    ])
    assistant = Assistant(ai_client=cliente)

    assistant.start()

    segunda_conversa = cliente.calls[1]

    assert segunda_conversa == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Qual é o meu nome?"},
    ]


def test_falha_da_ia_nao_encerra_a_aplicacao(monkeypatch, capsys):
    entradas = iter([
        "Primeira pergunta",
        "Segunda pergunta",
        "sair",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    cliente = FakeAIClient([
        AIConnectionError("Falha de conexão simulada"),
        "Resposta normal.",
    ])
    assistant = Assistant(ai_client=cliente)

    assistant.start()

    saida = capsys.readouterr().out

    assert "Falha de conexão simulada" in saida
    assert "Resposta normal." in saida
    assert len(cliente.calls) == 2

    # A pergunta que falhou não fica no contexto enviado depois.
    segunda_conversa = cliente.calls[1]

    assert not any(
        message["content"] == "Primeira pergunta"
        for message in segunda_conversa
    )
