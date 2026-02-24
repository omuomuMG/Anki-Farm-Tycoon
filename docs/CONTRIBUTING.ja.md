このドキュメントには他の言語版があります:
* [English (英語)](./CONTRIBUTING.md)

---

# Anki Farm Tycoonへの貢献

Anki Farm Tycoonに興味を持っていただき、ありがとうございます！ 🐮🐔🐷

私たちは、バグ報告、新機能の提案、コードの改善、ドキュメントの修正など、あらゆる形の貢献を歓迎します。このプロジェクトは、皆さんの協力によってより良くなります。

## 🤝 貢献の種類

貢献には様々な方法があります。

* **🐛 バグの報告:** ゲームプレイ中に見つけたバグや問題を報告する。
* **💡 機能の提案:** 「こんな動物が欲しい」「こんな機能があったら便利」といったアイデアを提案する。
* **📝 ドキュメントの改善:** `README.md` や `Instruction.md` の誤字脱字の修正や、分かりにくい部分の加筆・修正。
* **💻 コードの貢献:** バグ修正や新機能の実装を行う。
* **🌐 翻訳:** このガイドラインや `README.md` などを他言語へ翻訳する。

## 🚀 貢献の方法

### 🐞 バグ報告と機能提案

バグ報告や新機能の提案は、GitHubの**Issue**からお願いします。
私たちはIssueテンプレートを用意しています。適切なテンプレートを選んで、できるだけ詳細に内容を記述してください。

* **[🐛 バグ報告 (Bug report)](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=bug_report.md):** バグの再現手順や、期待される動作、実際の動作などを記述してください。
* **[💡 機能リクエスト (Feature request)](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=feature_request.md):** どのような機能が欲しいのか、それがどのような問題を解決するのかを記述してください。
* **[💬 その他 (Custom issue)](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=custom.md):** 上記に当てはまらない提案や議論はこちらをお使いください。

### 💻 プルリクエスト (Pull Request) の送り方

コードの修正や機能追加は、**Pull Request (PR)** を通じて受け付けています。

1.  **リポジトリをフォーク(Fork):**
    まず、このリポジトリをご自身のGitHubアカウントにフォークしてください。

2.  **ブランチを作成(Create a branch):**
    フォークしたリポジトリで、変更内容に適した名前のブランチを作成します。
    ```bash
    # 例: 新機能「羊」を追加する場合
    git checkout -b feature/add-sheep

    # 例: ショップボタンのバグを修正する場合
    git checkout -b fix/shop-button-bug
    ```

3.  **変更とコミット(Commit your changes):**
    コードを修正・追加し、変更内容をコミットします。コミットメッセージは分かりやすく記述してください。（可能であれば英語でお願いします）
    ```bash
    git commit -m "feat: Add new animal 'Sheep' model and logic"
    ```

4.  **プッシュ(Push to the branch):**
    作成したブランチを、ご自身のGitHubリポジトリにプッシュします。
    ```bash
    git push origin feature/add-sheep
    ```

5.  **プルリクエストを作成(Open a Pull Request):**
    GitHub上で、フォークしたリポジトリから**元の`omuomuMG/Anki-Farm-Tycoon`リポジトリ**の`main`（または`master`）ブランチに対してプルリクエストを作成します。

    * PRのタイトルと説明を分かりやすく記述してください。
    * 関連するIssueがあれば、説明欄に `Closes #123` のように記述してリンクしてください。
  


## 🎨 コーディングスタイル

* Pythonコードは、基本的に**PEP 8**に準拠してください。
* 既存のコードスタイル（インデント、命名規則、型ヒントの使用など）を参考にしてください。

## ✍️ コミットとPRの命名規則

プロジェクトの履歴を分かりやすく保つため、コミットメッセージとPRのタイトルは以下の規約に従ってください。

### コミットメッセージ
コミットメッセージは、**原則として英語で記述してください**。
`type(scope): subject` という形式を推奨します。

**1. `type` (必須):** コミットの種類を表すキーワード

* `feat`: 新機能の追加（例: 新しい動物、新しいUI）
* `fix`: バグの修正（例: 動物が売れない、お金が正しく計算されない）
* `docs`: ドキュメントのみの変更（例: `README.md`, `Instruction.md` の更新）
* `style`: コードの動作に影響しない変更（例: フォーマット、インデント、typo修正）
* `refactor`: リファクタリング（例: 既存機能の内部的な改善、コードのクリーンアップ）
* `test`: テストコードの追加・修正
* `chore`: ビルドプロセスや補助ツールの変更など（例: `.gitignore` の更新）

**2. `scope` (任意):** 変更の範囲を示す（例：ファイル名や機能名）

* `gui`: GUI関連 (`game_widget.py`, `shop_window.py` など)
* `model`: データモデル (`animal.py`, `employee.py` など)
* `save`: セーブ・ロード (`save_manager.py` など)
* `leaderboard`: リーダーボード機能 (`leaderboard.py` など)

**3. `subject` (必須):** 変更内容の簡潔な説明（動詞の原形で始め、文末にピリオドは不要）

**コミットメッセージの具体例:**

* `feat(model): Add Sheep animal type` (新機能: 羊モデルの追加)
* `fix(gui): Prevent negative money when buying animals` (バグ修正: 動物購入時に所持金がマイナスになるのを防ぐ)
* `docs(README.ja): Add Japanese translation for README` (ドキュメント: READMEの日本語訳追加)
* `refactor(gui): Simplify paint_handler logic` (リファクタリング: paint_handler のロジックを簡素化)
* `style(shop_window): Fix typo in variable name` (スタイル: shop_window.py の変数名のタイポ修正)

---

### プルリクエスト (PR)

**1. PRのタイトル:**
PRのタイトルも、**コミットメッセージの規約（`type(scope): subject`）に従ってください。**
これにより、PRがマージされたときに、リポジトリの履歴が一貫して保たれます。

* **良い例:** `feat(leaderboard): Add user registration window`
* **良い例:** `fix(save): Correctly load employee preferences`
* **悪い例:** `Update` や `Fix bug` (内容が不明確です)

**2. PRの説明 (Description):**
PRを作成する際は、説明欄に以下の内容をできるだけ記述してください。

* **どのような変更か:** 変更の概要。
* **なぜこの変更が必要か:** 変更の動機や背景。
* **関連するIssue:** `Closes #123` や `Fixes #456` のように、関連するIssue番号を記載してください。これにより、PRがマージされると自動的にIssueが閉じられます。
* **スクリーンショット (任意):** UIや表示の変更を含む場合は、変更前後のスクリーンショットを添付するとレビューしやすくなります。
  

## 📜 ライセンス
このプロジェクトに貢献することで、あなたのコードはプロジェクトと同じ**GPL-3.0 License** の下で提供されることに同意したものとみなされます。
