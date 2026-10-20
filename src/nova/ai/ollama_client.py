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

    def generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        try:
            response = self._client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
            )

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
                "Não foi possível estabelecer a comunicação "
                "com o serviço do Ollama."
            ) from exc

        content = response.message.content

        if not content or not content.strip():
            raise AIResponseError(
                "O modelo não retornou uma resposta válida."
            )

        return content.strip()