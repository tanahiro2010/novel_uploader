# 小説コンバーター / Syosetu Converter

Web小説サイトから小説をダウンロードして変換するツールです。

## 対応サイト

- **カクヨム (Kakuyomu)**: https://kakuyomu.jp/
- **小説家になろう (Narou)**: https://syosetu.com/

## 必要な環境

- Google Chrome ブラウザ
- インターネット接続

## セットアップ方法

### 1. 設定ファイルの編集

`config.json` ファイルを開いて、各サイトのログイン情報を入力してください：

```json
{
  "kakuyomu": {
    "email": "your-email@example.com",
    "password": "your-password"
  },
  "narou": {
    "email": "your-email@example.com",
    "password": "your-password"
  },
  "alphapolic": {
    "email": "",
    "password": ""
  }
}
```

**⚠️ 重要**: `config.json` には実際のログイン情報が含まれるため、他人と共有しないでください。

### 3. 実行方法

`run.bat` をダブルクリックするだけで起動します。

- 自動的に必要なパッケージがインストールされます
- アプリケーションが起動し、ダウンロードする小説を選択できます

## 使い方

1. `run.bat` を実行
2. ダウンロードしたいサイトを選択
3. 小説のURLまたはIDを入力
4. ダウンロード完了を待つ

## ログファイル

- アプリケーションの動作ログは `syosetu_converter.log` に保存されます
- エラーが発生した場合は、このファイルを確認してください

## トラブルシューティング

### 仮想環境が見つからない

```bash
python -m venv .venv
```

を実行してから、再度 `run.bat` を起動してください。

### 依存関係のインストールに失敗する

Pythonとpipが最新バージョンであることを確認してください：

```bash
python -m pip install --upgrade pip
```

### Chrome ドライバーのエラー

Google Chrome が最新バージョンであることを確認してください。Seleniumは自動的に適切なドライバーをダウンロードします。

## ライセンス

このツールは教育目的で作成されています。各小説サイトの利用規約を遵守して使用してください。

## 注意事項

- ダウンロードした小説の著作権は作者に帰属します
- 個人的な利用の範囲でご使用ください
- サイトに過度な負荷をかけないようにしてください

