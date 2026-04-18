# Naukri Resume Auto-Updater 🤖

Automatically refreshes your Naukri resume daily at **9 AM IST** using GitHub Actions — **completely free**, no local machine required.

## How It Works

1. GitHub Actions wakes up at 9 AM IST every day
2. Spins up a free Ubuntu cloud machine
3. Runs a Java + Selenium script that logs into your Naukri account
4. Deletes your old resume and uploads a fresh copy
5. Shuts down — your profile appears "recently updated" ✅

---

## One-Time Setup (5 minutes)

### Step 1 — Create a GitHub Repository

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `naukri-auto-update` (or anything you like)
3. Set it to **Private** ← important for security
4. Clone it and copy ALL these project files into it

### Step 2 — Add Your Resume PDF

1. Place your resume PDF file directly into this project folder.
2. The script will automatically find the `.pdf` file in the folder and upload it.
3. Make sure you only have ONE `.pdf` file in the folder to avoid confusion.

### Step 3 — Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 2 secrets:

| Secret Name | Value |
|-------------|-------|
| `NAUKRI_EMAIL` | Your Naukri login email |
| `NAUKRI_PASSWORD` | Your Naukri password |

> ⚠️ Secrets are encrypted and never visible after saving. Even GitHub cannot read them.

### Step 4 — Enable & Test

1. Push all files to your GitHub repo
2. Go to **Actions** tab in your repo
3. Click **"Naukri Resume Update"** workflow
4. Click **"Run workflow"** → **"Run workflow"** button
5. Watch the logs — it should complete in ~3-5 minutes ✅
6. Log in to Naukri and verify your resume "last updated" timestamp changed

---

## Schedule

The workflow runs automatically at **3:30 AM UTC = 9:00 AM IST** every day.

To change the time, edit `.github/workflows/naukri-update.yml`:
```yaml
- cron: '30 3 * * *'   # minute hour * * *  (UTC)
```

Use [crontab.guru](https://crontab.guru) to calculate your desired UTC time.

---

## Project Structure

```
naukri-auto-update/
├── .github/
│   └── workflows/
│       └── naukri-update.yml      ← GitHub Actions schedule
├── src/
│   └── main/
│       └── java/
│           └── com/naukri/
│               └── NaukriUpdate.java  ← Selenium automation
├── pom.xml                            ← Maven dependencies
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Login fails | Double-check `NAUKRI_EMAIL` / `NAUKRI_PASSWORD` secrets |
| Resume not uploading | Naukri may have changed their UI — open an issue |
| Action not running | Check Actions tab is enabled in repo settings |
| No PDF found error | Make sure your PDF file is pushed to the GitHub repository |

---

## Cost

**$0 forever.** GitHub Actions provides 2,000 free minutes/month. This job uses ~4-5 min/day = ~150 min/month.
