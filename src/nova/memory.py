import json
from pathlib import Path

# Lê uma lista salva em um arquivo JSON.
def load_list(path: Path) -> list:

    # Primeira vez rodando: ainda não há arquivo, então não há nada a ler.
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    # O arquivo existe, mas o conteúdo não é um JSON válido.# O arquivo existe, mas o conteúdo não é um JSON válido.
    except json.JSONDecodeError:
        path.replace(path.with_suffix(".corrompido"))
        return []

    # Não foi possível ler o arquivo (por exemplo, sem permissão).
    except OSError:
        return []

    # Garante que o conteúdo é mesmo uma lista.
    return data if isinstance(data, list) else []

# Salva uma lista em um arquivo JSON.
def save_list(path: Path, data: list) -> None:
    
    # Cria a pasta data/ se ela ainda não existir.
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        # ensure_ascii=False mantém acentos legíveis (ç, ã, é...).
        json.dump(data, file, ensure_ascii=False, indent=2)

    temp_path.replace(path)

# Guarda duas coisas, ambas salvas em disco "history" últimas mensagens e facts "coisas que você pediu para ela lembrar"
class Memory:

    # Roda ao criar uma Memory.
    def __init__(
        self,
        history_file: Path,
        facts_file: Path,
        max_history: int,
    ) -> None:
        # Carrega o que já estava salvo, descartando itens malformados.
        self._history_file = history_file
        self._facts_file = facts_file
        self._max_history = max_history

        # Carrega o que já estava salvo, descartando itens malformados.
        self.history: list[dict[str, str]] = []
        for item in load_list(history_file):
            if (
                isinstance(item, dict)
                and isinstance(item.get("role"), str)
                and isinstance(item.get("content"), str)
            ):
                self.history.append({
                    "role": item["role"],
                    "content": item["content"],
                })

        # Fatos: só mantém o que for texto.
        self.facts: list[str] = [
            fact for fact in load_list(facts_file)
            if isinstance(fact, str)
        ]

    # Registra uma pergunta e a resposta, e salva no disco.
    def add_exchange(self, user_message: str, answer: str) -> None:

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": answer})

        # Mantém só as mensagens mais recentes.
        self.history = self.history[-self._max_history:]

        save_list(self._history_file, self.history)

    # Apaga a conversa (só o histórico; os fatos continuam guardados).
    def clear_history(self) -> None:
        self.history.clear()
        save_list(self._history_file, self.history)

    # Guarda um fato. Devolve False se ele já existia.
    def add_fact(self, fact: str) -> bool:

        # casefold() ignora maiúsculas/minúsculas ao comparar
        already_saved = any(
            fact.casefold() == saved.casefold() for saved in self.facts
        )
        if already_saved:
            return False

        self.facts.append(fact)
        save_list(self._facts_file, self.facts)
        return True

    # Limpa um fato. Devolve False se ele já existia.
    def clear_facts(self) -> None:
        self.facts.clear()
        save_list(self._facts_file, self.facts)