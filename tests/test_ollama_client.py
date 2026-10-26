
import pytest

from nova.ai.ollama_client import AIConnectionError, OllamaClient


def test_erro_de_conexao_e_convertido(monkeypatch):
    class OllamaIndisponivel:
        def __init__(self, *, host: str):
            pass

        def chat(self, **kwargs):
            raise ConnectionError("Ollama indisponível")

    monkeypatch.setattr(
        "nova.ai.ollama_client.Client",
        OllamaIndisponivel,
    )

    cliente = OllamaClient()

    with pytest.raises(
        AIConnectionError,
        match="Não foi possível conectar ao Ollama",
    ):
        cliente.generate_response([
            {"role": "user", "content": "Olá"},
        ])
