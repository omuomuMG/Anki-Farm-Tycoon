本文档有其他语言版本：
* [日本語 (Japanese)](./CONTRIBUTING.ja.md)
---
# 为 Anki Farm Tycoon 贡献代码

感谢你对 **Anki Farm Tycoon** 的关注！🐮🐔🐷

我们欢迎所有形式的贡献，例如：bug 报告、新功能建议、代码优化、文档修正等。有你的帮助，这个项目会变得更好。

## 🤝 贡献类型

你可以通过多种方式参与贡献：

* **🐛 报告 Bug**：报告你在游戏过程中发现的错误或问题。
* **💡 建议功能**：提出想法，例如“我想要这种动物”或“这个功能会很方便”。
* **📝 完善文档**：修正错别字，或对 `README.md`、`Instruction.md` 中难以理解的部分进行补充/修改。
* **💻 贡献代码**：修复 bug 或实现新功能。
* **🌐 翻译**：将本指南或 `README.md` 翻译成其他语言。

## 🚀 如何贡献

### 🐞 报告 Bug 与功能建议

请使用 GitHub **Issues** 来报告 bug 或建议新功能。
我们已准备好 Issue 模板，请选择合适的模板，并尽可能详细地描述内容。

* **[🐛 Bug 报告](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=bug_report.md)**：请描述复现 bug 的步骤、预期行为与实际表现。
* **[💡 功能请求](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=feature_request.md)**：请描述你想要的功能以及它能解决什么问题。
* **[💬 自定义 Issue](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=custom.md)**：用于上述类别以外的建议或讨论。

### 💻 如何提交 Pull Request（PR）

我们通过 **Pull Request（PR）** 接收代码修复与新功能。

1. **Fork 仓库**：首先，将本仓库 Fork 到你自己的 GitHub 账号。

2. **创建分支**：在你 Fork 的仓库中，根据修改内容创建一个合适名称的分支。
    ```bash
    # 示例：添加新“绵羊”功能
    git checkout -b feature/add-sheep

    # 示例：修复商店按钮 bug
    git checkout -b fix/shop-button-bug
    ```

3. **提交修改**：修改或新增代码后提交更改。请编写清晰的提交信息（尽量用英文）。
    ```bash
    git commit -m "feat: Add new animal 'Sheep' model and logic"
    ```

4. **推送到分支**：将创建的分支推送到你的 GitHub 仓库。
    ```bash
    git push origin feature/add-sheep
    ```

5. **发起 Pull Request**：在 GitHub 上，从你 Fork 仓库的分支，向**原仓库 `omuomuMG/Anki-Farm-Tycoon` 的 `main`（或 `master`）分支**创建 Pull Request。

    * 为 PR 编写清晰的标题和描述。
    * 如果与某个 Issue 相关，请在描述中关联，例如 `Closes #123`。

## 🎨 代码风格

* Python 代码应基本遵循 **PEP 8**。
* 请参考现有代码风格（缩进、命名规范、类型提示使用等）。

## ✍️ 提交信息与 PR 命名规范

为了让项目历史清晰易读，请遵循以下提交信息与 PR 标题规范。

### 提交信息（Commit Message）

提交信息**原则上使用英文**。
推荐格式：`type(scope): subject`。

**1. `type`（必填）**：描述本次提交类型的关键词

* `feat`：添加新功能（如新动物、新界面）
* `fix`：修复 bug（如动物无法出售、金钱计算错误）
* `docs`：仅修改文档（如更新 `README.md`、`Instruction.md`）
* `style`：不影响代码行为的修改（如格式化、缩进、错别字修正）
* `refactor`：重构（如对现有功能的内部优化、代码清理）
* `test`：添加或修改测试代码
* `chore`：构建过程或辅助工具的变动（如更新 `.gitignore`）

**2. `scope`（可选）**：修改范围（如文件名或功能名）

* `gui`：与界面相关（`game_widget.py`、`shop_window.py` 等）
* `model`：数据模型（`animal.py`、`employee.py` 等）
* `save`：存档/读档（`save_manager.py` 等）
* `leaderboard`：排行榜功能（`leaderboard.py` 等）

**3. `subject`（必填）**：简洁描述修改内容（使用祈使动词开头，句末不加句号）

**提交信息示例：**

* `feat(model): Add Sheep animal type`（新功能：添加绵羊动物模型）
* `fix(gui): Prevent negative money when buying animals`（修复：购买动物时防止金额变为负数）
* `docs(README.ja): Add Japanese translation for README`（文档：为 README 添加日文翻译）
* `refactor(gui): Simplify paint_handler logic`（重构：简化 paint_handler 逻辑）
* `style(shop_window): Fix typo in variable name`（格式：修复 shop_window.py 中变量名的拼写错误）

---

### Pull Request（PR）

**1. PR 标题**：PR 标题也请遵循**提交信息规范**：`type(scope): subject`。这样在合并 PR 时能保持仓库历史一致。

* **良好示例**：`feat(leaderboard): Add user registration window`
* **良好示例**：`fix(save): Correctly load employee preferences`
* **不良示例**：`Update` 或 `Fix bug`（内容不清晰）

**2. PR 描述**：创建 PR 时，请在描述中尽可能包含以下内容：

* **这是哪类修改？**：修改概要。
* **为什么需要这个修改？**：修改的动机或背景。
* **关联 Issue**：关联相关 Issue，例如 `Closes #123` 或 `Fixes #456`。PR 合并后会自动关闭对应 Issue。
* **截图（可选）**：如果修改包含界面或视觉变化，附上前后对比截图会更便于审核。

## 📜 许可证
为该项目贡献代码，即表示你同意你的代码将与项目采用相同的 **GPL-3.0 许可证** 发布。
