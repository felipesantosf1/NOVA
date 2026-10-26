from pathlib import Path

APP_NAME = "NOVA"
VERSION = "0.3.0"

# Endereço onde o Ollama está rodando.
OLLAMA_HOST = "http://localhost:11434"
# Nome do modelo.
OLLAMA_MODEL = "gemma4"

# Número máximo de mensagens anteriores mantidas no contexto.
MAX_HISTORY_MESSAGES = 20

# .gitignore, então suas conversas pessoais não vão pro GitHub.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_FILE = DATA_DIR / "history.json"  # conversa recente
FACTS_FILE = DATA_DIR / "facts.json"      # coisas que você pediu pra ela lembrar

# conversa. É ele que define o jeito de ser da NOVA.
SYSTEM_PROMPT = """
Você é a NOVA, uma assistente virtual pessoal.

Regras de comportamento:
- Responda em português do Brasil.
- Seja clara, útil e objetiva.
- Explique conceitos de forma compreensível.
- Considere o contexto das mensagens anteriores.
- Seja transparente quando não souber uma resposta.
- Não invente informações para preencher lacunas.
- Não afirme que executou ações, acessou arquivos ou consultou serviços externos quando 
isso não tiver acontecido.
"""