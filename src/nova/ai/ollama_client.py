from collections.abc import Iterator

from httpx import HTTPError
from ollama import Client, ResponseError

from nova.config import OLLAMA_HOST, OLLAMA_MODEL

# Erro geral relacionado à inteligência artificial.
class AIError(Exception):
    pass

# Erro de comunicação com o serviço de IA.
class AIConnectionError(AIError):
    pass

# Erro ao solicitar ou receber uma resposta da IA.
class AIResponseError(AIError):
    pass


class OllamaClient:
    def __init__(self) -> None:
        self._client = Client(host=OLLAMA_HOST) # Cria a "conexão" com o Ollama.

    # É isso que cria o efeito de a resposta ser "digitada" na tela.
    def stream_response(
        self,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
    
        # O try envolve TODO o processo (inclusive o for)
        try:
            # stream=True faz o Ollama mandar a resposta em pedaços.
            stream = self._client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                stream=True,
            )

            for chunk in stream:
                piece = chunk.message.content

                # Alguns pedaços vêm vazios; só repassamos os que têm texto.
                if piece:
                    yield piece

        except ConnectionError as exc:
            # O Ollama está desligado ou o endereço está errado.
            raise AIConnectionError(
                "Não foi possível conectar ao Ollama. "
                f"Endereço configurado: {OLLAMA_HOST}. "
                "Verifique se ele está em execução."
            ) from exc

        except ResponseError as exc:
            # O Ollama respondeu, mas com um erro.
            if exc.status_code == 404:
                raise AIResponseError(
                    f"Modelo '{OLLAMA_MODEL}' não encontrado. "
                    "Confira o nome configurado em config.py."
                ) from exc

            # Para os outros erros, mostramos o detalhe que o Ollama informou.
            detail = exc.error or "Erro sem detalhes."

            raise AIResponseError(
                f"O serviço de IA retornou um erro: {detail}"
            ) from exc

        except HTTPError as exc:
            # Qualquer outro problema de rede (queda, tempo esgotado etc.).
            raise AIConnectionError(
                "Ocorreu um erro de comunicação com o serviço de IA."
            ) from exc