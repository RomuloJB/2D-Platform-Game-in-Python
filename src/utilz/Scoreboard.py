"""
Scoreboard — histórico de pontuações dos jogadores (salvo em JSON).

Cada partida (do "JOGAR" até vencer, morrer ou voltar ao menu) gera UM
registro, identificado por um id. Enquanto a partida continua, o mesmo
registro é atualizado — assim o histórico não enche de entradas repetidas
da mesma jogatina.

Arquivo gerado em data/scores.json:
    [
        {"id": "20260916-153012-123456", "name": "ROMULO", "score": 1250,
         "coins": 40, "level": 3, "status": "DERROTA",
         "date": "16/09/2026 15:30"},
        ...
    ]

O módulo é tolerante a falhas: se o arquivo não existir, estiver corrompido
ou não puder ser escrito, o jogo continua rodando normalmente — apenas sem
histórico.
"""

import json
import os
from datetime import datetime

# Raiz do projeto (…/src/utilz/Scoreboard.py -> sobe 3 níveis). Assim o
# histórico é sempre gravado no mesmo lugar, não importa de qual pasta o
# jogo foi executado.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

SCORES_DIR  = os.path.join(_PROJECT_ROOT, "data")
SCORES_PATH = os.path.join(SCORES_DIR, "scores.json")

MAX_ENTRIES  = 50          # guarda só as 50 melhores pontuações
MAX_NAME_LEN = 12
DEFAULT_NAME = "JOGADOR"

# status possíveis de uma partida
STATUS_PLAYING = "EM JOGO"
STATUS_WIN     = "VITÓRIA"
STATUS_LOSS    = "DERROTA"
STATUS_QUIT    = "SAIU"


# ─────────────────────────────────────────────────────────────────
#  Leitura
# ─────────────────────────────────────────────────────────────────
def load_scores() -> list:
    """Lê o arquivo e devolve a lista de registros (vazia se não houver)."""
    if not os.path.exists(SCORES_PATH):
        return []
    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and "score" in e]


def top_scores(limit: int = 10) -> list:
    """Registros do maior para o menor score."""
    scores = sorted(load_scores(), key=lambda e: e.get("score", 0), reverse=True)
    return scores[:limit]


def last_player_name() -> str:
    """Nome usado na partida mais recente — pré-preenche o menu."""
    scores = load_scores()
    if not scores:
        return ""
    latest = max(scores, key=lambda e: str(e.get("id", "")))
    return str(latest.get("name", ""))


def sanitize_name(name: str) -> str:
    """Nome em caixa alta, sem espaços nas pontas e limitado no tamanho."""
    clean = (name or "").strip().upper()[:MAX_NAME_LEN]
    return clean or DEFAULT_NAME


# ─────────────────────────────────────────────────────────────────
#  Escrita
# ─────────────────────────────────────────────────────────────────
def _write(scores: list) -> bool:
    """Grava a lista já ordenada e cortada em MAX_ENTRIES."""
    scores = sorted(scores, key=lambda e: e.get("score", 0),
                    reverse=True)[:MAX_ENTRIES]
    try:
        os.makedirs(SCORES_DIR, exist_ok=True)
        with open(SCORES_PATH, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


def new_run_id() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def save_run(entry_id, name: str, score: int, coins: int = 0,
             level: int = 1, status: str = STATUS_PLAYING):
    """
    Cria (entry_id=None) ou atualiza um registro de partida.
    Devolve o id usado, ou None se não foi possível salvar.
    """
    entry_id = entry_id or new_run_id()
    entry = {
        "id":     entry_id,
        "name":   sanitize_name(name),
        "score":  int(score),
        "coins":  int(coins),
        "level":  int(level),
        "status": status,
        "date":   datetime.now().strftime("%d/%m/%Y %H:%M"),
    }

    scores = load_scores()
    for i, old in enumerate(scores):
        if old.get("id") == entry_id:
            scores[i] = entry
            break
    else:
        scores.append(entry)

    return entry_id if _write(scores) else None


def clear_scores() -> bool:
    """Apaga todo o histórico."""
    return _write([])
