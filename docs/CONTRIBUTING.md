This document is available in other languages:
* [日本語 (Japanese)](./CONTRIBUTING.ja.md)

---

# Contributing to Anki Farm Tycoon

Thank you for your interest in Anki Farm Tycoon! 🐮🐔🐷

We welcome all forms of contributions, such as bug reports, new feature suggestions, code improvements, and documentation fixes. This project gets better with your help.

## 🤝 Types of Contributions

There are many ways to contribute:

* **🐛 Report Bugs:** Report bugs or issues you find during gameplay.
* **💡 Suggest Features:** Propose ideas like "I want this animal" or "This feature would be convenient."
* **📝 Improve Documentation:** Fix typos or make additions/corrections to confusing parts in `README.md` or `Instruction.md`.
* **💻 Contribute Code:** Perform bug fixes or implement new features.
* **🌐 Translate:** Translate this guideline or `README.md` into other languages.

## 🚀 How to Contribute

### 🐞 Bug Reports and Feature Suggestions

Please use GitHub **Issues** to report bugs or suggest new features.
We have prepared Issue templates. Please select the appropriate template and describe the content in as much detail as possible.

* **[🐛 Bug report](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=bug_report.md):** Please describe the steps to reproduce the bug, the expected behavior, and the actual behavior.
* **[💡 Feature request](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=feature_request.md):** Please describe what feature you want and what problem it solves.
* **[💬 Custom issue](https://github.com/omuomuMG/Anki-Farm-Tycoon/issues/new?template=custom.md):** Please use this for suggestions or discussions that do not fall into the above categories.

### 💻 How to Send a Pull Request (PR)

We accept code fixes and new features through **Pull Requests (PRs)**.

1.  **Fork the repository:**
    First, fork this repository to your own GitHub account.

2.  **Create a branch:**
    In your forked repository, create a branch with a name suitable for your changes.
    ```bash
    # Example: When adding a new "Sheep" feature
    git checkout -b feature/add-sheep

    # Example: When fixing a shop button bug
    git checkout -b fix/shop-button-bug
    ```

3.  **Commit your changes:**
    Modify or add code, and then commit your changes. Please write clear commit messages (in English, if possible).
    ```bash
    git commit -m "feat: Add new animal 'Sheep' model and logic"
    ```

4.  **Push to the branch:**
    Push the branch you created to your GitHub repository.
    ```bash
    git push origin feature/add-sheep
    ```

5.  **Open a Pull Request:**
    On GitHub, create a pull request from your forked repository's branch to the `main` (or `master`) branch of the **original `omuomuMG/Anki-Farm-Tycoon` repository**.

    * Write a clear title and description for the PR.
    * If it relates to an Issue, link it in the description, such as `Closes #123`.
  
## 🎨 Coding Style

* Python code should generally adhere to **PEP 8**.
* Please refer to the existing code style (indentation, naming conventions, use of type hints, etc.).

## ✍️ Commit and PR Naming Conventions

To keep the project history easy to understand, please follow the conventions below for commit messages and PR titles.

### Commit Messages
Commit messages should **be written in English, as a rule**.
The `type(scope): subject` format is recommended.

**1. `type` (Required):** A keyword describing the type of commit.

* `feat`: Addition of a new feature (e.g., new animal, new UI)
* `fix`: A bug fix (e.g., animal cannot be sold, money calculation error)
* `docs`: Documentation only changes (e.g., updating `README.md`, `Instruction.md`)
* `style`: Changes that do not affect code behavior (e.g., formatting, indentation, typo fixes)
* `refactor`: Refactoring (e.g., internal improvements to existing features, code cleanup)
* `test`: Adding or correcting test code
* `chore`: Changes to the build process or auxiliary tools, etc. (e.g., updating `.gitignore`)

**2. `scope` (Optional):** The scope of the change (e.g., file name or feature name)

* `gui`: GUI related (`game_widget.py`, `shop_window.py`, etc.)
* `model`: Data model (`animal.py`, `employee.py`, etc.)
* `save`: Save/Load (`save_manager.py`, etc.)
* `leaderboard`: Leaderboard feature (`leaderboard.py`, etc.)

**3. `subject` (Required):** A concise description of the change (start with an imperative verb, no period at the end)

**Specific Examples of Commit Messages:**

* `feat(model): Add Sheep animal type` (New feature: Add Sheep model)
* `fix(gui): Prevent negative money when buying animals` (Bug fix: Prevent negative money when buying animals)
* `docs(README.ja): Add Japanese translation for README` (Documentation: Add Japanese translation for README)
* `refactor(gui): Simplify paint_handler logic` (Refactoring: Simplify paint_handler logic)
* `style(shop_window): Fix typo in variable name` (Style: Fix typo in shop_window.py variable name)

---

### Pull Requests (PRs)

**1. PR Title:**
The PR title should also follow the **commit message convention (`type(scope): subject`)**.
This keeps the repository history consistent when the PR is merged.

* **Good Example:** `feat(leaderboard): Add user registration window`
* **Good Example:** `fix(save): Correctly load employee preferences`
* **Bad Example:** `Update` or `Fix bug` (The content is unclear)

**2. PR Description:**
When creating a PR, please describe the following content as much as possible in the description:

* **What kind of change is this?:** Summary of the change.
* **Why is this change necessary?:** The motivation or background for the change.
* **Related Issues:** Link any related Issues, such as `Closes #123` or `Fixes #456`. This will automatically close the issue when the PR is merged.
* **Screenshots (Optional):** If the change includes UI or visual modifications, attaching before-and-after screenshots will make it easier to review.
  

## 📜 License
By contributing to this project, you agree that your code will be provided under the same **GPL-3.0 License** as the project.
