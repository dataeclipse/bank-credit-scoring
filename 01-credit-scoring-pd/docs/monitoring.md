# Monitoring - дрейф входов и PD (Фаза 4)

Что мониторим стабильность модели во времени: распределения входных фич и распределение PD
не должны «уезжать» относительно reference (обучающая выборка / витрина).

## Метрики
- **PSI / CSI** по каждой входной фиче - `population_stability_index` (квантильные бины по reference).
  PSI = Σ (a% − e%)·ln(a%/e%). Эмпирические пороги: **<0.1** нет сдвига, **0.1-0.2** умеренный,
  **>0.2** значимый дрейф.
- **Дрейф PD** - PSI между распределением PD на reference и на текущей партии.

## Порог алерта
`PD_PSI` или PSI любой фичи **> 0.2** (config `psi_threshold`) → алерт.

## Запуск
```bash
make ingest && make features          # нужна витрина (reference)
uv run python -m pd_scoring.monitoring.drift --demo-drift     # синтетический сдвиг (демо)
uv run python -m pd_scoring.monitoring.drift --current batch.parquet   # реальная партия
```
Генерирует `docs/drift_report.md` (PSI-таблица + алерты) и опц. `docs/img/evidently_drift.html`
(Evidently Data Drift Preset).

## Демонстрация «ловли» дрейфа
`--demo-drift` сдвигает распределения `EXT_SOURCE_2/3` (−0.15), `AMT_CREDIT` (×1.4),
`DAYS_EMPLOYED` (×1.3). Результат - алерт срабатывает:

| Фича | PSI | алерт |
|------|-----|-------|
| `EXT_SOURCE_2` | 2.47 | ⚠️ |
| `EXT_SOURCE_3` | 1.66 | ⚠️ |
| `AMT_CREDIT` | 0.43 | ⚠️ |
| дрейф PD | 0.22 | ⚠️ |

→ при подмене распределения входов мониторинг ловит дрейф и поднимает алерт.

## В прод (Фаза 5)
Планово: запуск drift-джобы по расписанию, экспорт PSI в Prometheus/Grafana, периодическая
ревалидация и пороги по бизнес-стабильности скорборда.
