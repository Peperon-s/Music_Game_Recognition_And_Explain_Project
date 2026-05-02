# YouTube動画ダウンロード（yt-dlp ラッパー）
import os
import yt_dlp
import logging
from src.utils.config import load_config

logger = logging.getLogger(__name__)
cfg = load_config()

class YouTubeDownLoader:
    download_dir = cfg["collection"]["download_dir"]

    def __init__(self):
        self.ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }

    def download(self, url: str) -> str:
        """単一動画をダウンロードする
        Args:
            url: YouTube動画のURL
        Returns:
            ダウンロードしたファイルのパス
        """
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    def download_playlist(self, url: str, difficulty: str) -> list[str]:
        """プレイリスト内の全動画をダウンロードする
        Args:
            url:        プレイリストのURL
            difficulty: 難易度区分（ログ用）
        Returns:
            ダウンロードしたファイルパスのリスト
        """
        logger.info(f"[{difficulty}] プレイリストのダウンロードを開始: {url}")
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            entries = info.get('entries', [info])
            paths = [ydl.prepare_filename(e) for e in entries if e]
        logger.info(f"[{difficulty}] {len(paths)} 件ダウンロード完了")
        return paths

    def download_all(self) -> dict[str, list[str]]:
        """config.yaml の playlists に定義された全難易度をダウンロードする
        Returns:
            難易度区分をキー、ファイルパスリストを値とする辞書
        """
        playlists: dict = cfg["collection"]["playlists"]
        results = {}
        for difficulty, url in playlists.items():
            if not url:
                logger.warning(f"[{difficulty}] URLが未設定のためスキップ")
                continue
            results[difficulty] = self.download_playlist(url, difficulty)
        return results
