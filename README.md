# Requirements для трёх банковских проектов

Версии актуальны на **30 июня 2026**. Использован формат `>=<latest>` (floor на текущую версию):
при установке подтягивается **самый свежий совместимый релиз**, а точную фиксацию даёт lock-файл.

## Как поставить (рекомендуемый способ — uv)
```bash
pip install uv                      # если ещё нет
uv venv && source .venv/bin/activate
uv pip install -r requirements/project1_scoring.txt
# зафиксировать ТОЧНЫЕ версии на сегодня в lock:
uv pip compile requirements/project1_scoring.txt -o requirements/project1_scoring.lock.txt
```
Аналогично для project2/project3/cv_swap. `uv pip compile` (или `uv lock` в pyproject) запишет
точные версии всего дерева зависимостей — это и есть «latest на сегодня», но воспроизводимо.

## Важные нюансы
- **PyTorch + CUDA.** `torch`/`torchvision` для GPU ставятся с индекса PyTorch, не с обычного PyPI:
  ```bash
  uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
  ```
  Версия CUDA (`cu124`/`cu126`/…) — под твою видеокарту/драйвер. CPU-версия ставится с PyPI как обычно.
- **torch-geometric** ставить ПОСЛЕ torch (совместимость с конкретной сборкой torch/CUDA).
- **vLLM** — только GPU и Linux; для локального демо без GPU используй **Ollama**.
- **PaddleOCR** требует `paddlepaddle` (CPU или GPU-сборка отдельно).
- **pandas 3.x / numpy 2.x** — текущие мажоры; если какая-то библиотека ещё отстаёт, resolver сам
  подберёт совместимую версию (поэтому floor, а не жёсткий `==`).
- Python: рекомендую **3.12** (максимум готовых wheels). 3.13 поддерживается почти везде.

## Файлы
- `project1_scoring.txt` — кредитный скоринг (PD)
- `project2_fraud_aml.txt` — антифрод real-time + AML на графах
- `project3_genai_rukz.txt` — GenAI/NLP-ассистент RU/KZ
- `cv_swap_document_ai.txt` — альтернатива под Kaspi CV (document AI / KYC)

## Проверенные «latest» на 30.06.2026 (ключевые)
torch 2.12.1 · torchvision 0.27.1 · pytorch-lightning 2.6.5 · torch-geometric 2.8.0 ·
langgraph 1.2.6 · langchain 1.3.11 · vllm 0.23.0 · lightgbm 4.6.0 · xgboost 3.2.0 ·
catboost 1.2.10 · scikit-learn 1.8.0 · numpy 2.4 · pandas 3.0.
Остальные пакеты — floor на актуальную ветку; точные патчи фиксирует lock.
