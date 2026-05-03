import os
import re
import shutil
import logging
from src.utils.config import load_config

logger = logging.getLogger(__name__)
cfg = load_config()

# [プロセカ]{title}({difficulty}{level})譜面確認(速さ 10.0) をパースする正規表現
_RAW_PATTERN = re.compile(
    r"^\[プロセカ\](.+?)\((EASY|NORMAL|HARD|EXPERT|MASTER|APPEND)(\d+)\)譜面確認\(速さ 10\.0\)"
)
_VIDEO_EXTS = {'.mp4', '.mkv', '.avi'}


class Organizer:
    def __init__(self):
        self.parent_dir = cfg["collection"]["download_dir"]
        self.organized_dir = cfg["collection"]["organized_dir"]

    def _parse_filename(self, filename: str) -> dict | None:
        stem, ext = os.path.splitext(filename)
        if ext not in _VIDEO_EXTS:
            return None
        m = _RAW_PATTERN.match(stem)
        if not m:
            return None
        return {
            "title": m.group(1),
            "difficulty": m.group(2),
            "level": int(m.group(3)),
            "ext": ext,
            "original": filename,
        }

    def organize(self) -> None:
        entries = []
        for filename in os.listdir(self.parent_dir):
            parsed = self._parse_filename(filename)
            if parsed is None:
                if os.path.splitext(filename)[1] in _VIDEO_EXTS:
                    logger.warning(f"パース失敗、スキップ: {filename}")
                continue
            entries.append(parsed)

        if not entries:
            logger.info("整理対象のファイルが見つかりませんでした")
            return

        # global_index の採番が確定的になるようにソート
        entries.sort(key=lambda e: (e["difficulty"], e["level"], e["title"]))

        # global_index（全体通し）と index（難易度区分＋レベル内連番）を採番
        level_counters: dict[tuple, int] = {}
        for global_index, entry in enumerate(entries, start=1):
            key = (entry["difficulty"], entry["level"])
            level_counters[key] = level_counters.get(key, 0) + 1
            entry["global_index"] = global_index
            entry["index"] = level_counters[key]

        for entry in entries:
            new_name = (
                f"<{entry['global_index']:03d}>"
                f"[{entry['difficulty']} {entry['level']}]"
                f"{entry['title']} - {entry['index']:02d}"
                f"{entry['ext']}"
            )
            dst_dir = os.path.join(self.organized_dir, entry["difficulty"])
            os.makedirs(dst_dir, exist_ok=True)
            src = os.path.join(self.parent_dir, entry["original"])
            dst = os.path.join(dst_dir, new_name)
            shutil.move(src, dst)
            logger.info(f"{entry['original']} → {new_name}")

        logger.info(f"整理完了: {len(entries)} 件")
