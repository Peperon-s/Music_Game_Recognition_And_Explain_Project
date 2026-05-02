# config.yaml の読み込みユーティリティ
import yaml
from pathlib import Path
default_config_path = Path(__file__).parent.parent.parent / 'configs' / 'config.yaml'
def load_config(config_path: Path = default_config_path) -> dict:
    """YAML形式の設定ファイルを読み込むユーティリティ関数
    Returns:
        dict: 読み込んだ設定内容
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config