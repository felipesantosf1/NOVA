from collections.abc import Iterator

from httpx import HTTPError
from ollama import Client, ResponseError

from nova.config import OLLAMA_HOST, OLLAMA_MODEL


class AIError(Exception):
    """Erro geral relacionado à inteligência artificial."""


class AIConnectionError(AIError):
    """Erro de comunicação com o serviço de IA."""


class AIResponseError(AIError):
    """Erro ao solicitar ou receber uma resposta da IA."""


class OllamaClient:
    def __init__(self) -> None:
        self._client = Client(host=OLLAMA_HOST)

    # Envia a conversa para a IA e devolve a resposta aos poucos.
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
            raise AIConnectionError(
                "Não foi possível conectar ao Ollama. "
                f"Endereço configurado: {OLLAMA_HOST}. "
                "Verifique se ele está em execução."
            ) from exc

        except ResponseError as exc:
            if exc.status_code == 404:
                raise AIResponseError(
                    f"Modelo '{OLLAMA_MODEL}' não encontrado. "
                    "Confira o nome configurado em config.py."
                ) from exc

            detail = exc.error or "Erro sem detalhes."

            raise AIResponseError(
                f"O serviço de IA retornou um erro: {detail}"
            ) from exc

        except HTTPError as exc:
            raise AIConnectionError(
                "Ocorreu um erro de comunicação com o serviço de IA."
            ) from exc