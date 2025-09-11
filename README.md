# GithubActions
GithubActions

# 🚀 BRLiquibase GitHub Actions

Welcome to the **BRLiquibase GitHub Actions** repo — your one-stop-shop for automating Liquibase workflows using GitHub Actions! 🎉

---

## 🧩 What’s Inside

This repository contains examples and configurations to demonstrate how to:

- **Run Liquibase commands** automatically in CI pipelines  
- Generate changelogs, validate changes, and deploy database updates  
- Use official Liquibase GitHub Actions (e.g. `update`, `diff`, `status`, `history`, `checks run`, and more)  
- Integrate with different frameworks — CLI, Maven, Gradle, Docker and more :contentReference[oaicite:1]{index=1}

---

## 🔧 Quick Start

1. Fork or clone this repo  
2. Customize `.github/workflows/*.yml` files to match your changelog layout  
3. Configure secrets like:
   - `LIQUIBASE_LICENSE_KEY`
   - `DATABASE_URL`, `DB_USER`, `DB_PASSWORD`
4. Commit your changes to trigger Liquibase via GitHub Actions  
5. Watch the magic happen in the **Actions** tab!

---

## ⚙️ Included Workflow Examples

| Use Case                  | What it Shows                              |
|---------------------------|--------------------------------------------|
| `update.yml`              | Apply new changelogs to your target DB     |
| `diffAndSnapshot.yml`     | Compare schema differences and snapshot    |
| `qualityChecks.yml`       | Validate changelogs using Liquibase Pro checks :contentReference[oaicite:2]{index=2} |

Each job shows how to leverage different Liquibase commands like `update`, `diff`, `status`, and `checks run` via the GitHub Action.  
Check out the workflow YAML files for practical configurations and usage patterns. :contentReference[oaicite:3]{index=3}

---

## ✨ Why Use This?

- ✅ Simplifies Liquibase automation in CI/CD  
- 🧪 Keeps your schema changes consistent and version-controlled  
- 🚨 Adds optional quality gate checks using Liquibase Pro  
- 🤖 Works with Java-based, CLI or containerized Liquibase setups

---

## 🧠 Tips & Tricks

- Remember to place changelogs and Liquibase config files in accessible paths for the runner  
- Use `$GITHUB_STEP_SUMMARY` for custom Markdown logs or summaries in your CI runs :contentReference[oaicite:4]{index=4}  
- If you’re modifying parts of the README or docs, you can even automate those updates via script + Actions! :contentReference[oaicite:5]{index=5}

---

## 📚 Additional Resources

- GitHub Actions for Liquibase: official plugin documentation and examples :contentReference[oaicite:6]{index=6}  
- How to enforce policy and quality checks in your CI pipeline using Liquibase Pro :contentReference[oaicite:7]{index=7}

---

## 🚀 Contributions & Feedback

Love improvements? Want to add new example workflows?  
**Please open a PR or raise an issue!**  
Let’s automate, validate, and deploy with confidence.

