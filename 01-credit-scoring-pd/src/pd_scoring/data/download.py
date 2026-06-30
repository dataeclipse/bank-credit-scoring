from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from typing import Any

from pd_scoring.config import get_settings
from pd_scoring.logging_config import configure_logging, get_logger

COMPETITION = "home-credit-default-risk"
REQUIRED_FILES: tuple[str, ...] = (
    "application_train.csv",
    "application_test.csv",
    "bureau.csv",
    "bureau_balance.csv",
    "previous_application.csv",
    "installments_payments.csv",
    "POS_CASH_balance.csv",
    "credit_card_balance.csv",
    "HomeCredit_columns_description.csv",
)


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _authenticate() -> Any:
    _load_env()
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api


def _human(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def list_manifest(api: Any) -> list[tuple[str, int]]:
    files = api.competition_list_files(COMPETITION).files
    manifest: list[tuple[str, int]] = []
    for item in files:
        name = str(getattr(item, "name", item))
        size = int(getattr(item, "total_bytes", getattr(item, "size", 0)) or 0)
        manifest.append((name, size))
    return manifest


def download_file(api: Any, name: str, raw_dir: Path, log: Any) -> bool:
    target = raw_dir / name
    if target.exists() and target.stat().st_size > 0:
        log.info("cached", file=name)
        return False
    raw_dir.mkdir(parents=True, exist_ok=True)
    api.competition_download_file(COMPETITION, name, path=str(raw_dir), force=False, quiet=True)

    zip_path = raw_dir / f"{name}.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(raw_dir)
        zip_path.unlink()
    log.info("downloaded", file=name)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download Home Credit dataset via Kaggle API.")
    parser.add_argument(
        "--yes", action="store_true", help="реально скачать (иначе только манифест)"
    )
    parser.add_argument(
        "--raw-dir", default=None, help="куда класть CSV (по умолчанию <data_dir>/raw)"
    )
    args = parser.parse_args(argv)

    configure_logging()
    log = get_logger("ingest")
    settings = get_settings()
    raw_dir = Path(args.raw_dir) if args.raw_dir else settings.data_dir / "raw"

    try:
        api = _authenticate()
    except Exception as exc:
        log.error(
            "kaggle_auth_failed",
            error=str(exc),
            hint="нужны KAGGLE_USERNAME/KAGGLE_KEY в .env и принятые правила соревнования",
        )
        return 1

    manifest = [(n, s) for n, s in list_manifest(api) if n in REQUIRED_FILES]
    total = sum(size for _, size in manifest)
    print(f"\nHome Credit Default Risk — файлы к загрузке (в {raw_dir}):")
    for name, size in manifest:
        print(f"  {name:42s} {_human(size):>10s}")
    print(f"  {'ИТОГО':42s} {_human(total):>10s}\n")

    if not args.yes:
        print("Dry-run. Для реальной загрузки добавь --yes.")
        return 0

    downloaded = sum(download_file(api, name, raw_dir, log) for name in REQUIRED_FILES)
    log.info(
        "ingest_done",
        downloaded=downloaded,
        cached=len(REQUIRED_FILES) - downloaded,
        raw_dir=str(raw_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
