# Naukri Resume Auto-Updater 🤖 (Python Edition)

Automatically refreshes your Naukri resume daily at **9 AM IST** using GitHub Actions — **completely free**, no local machine required.

## Key Features
- **Dynamic Renaming:** Automatically renames your `Resume.pdf` to `resume_YYYYMMDD.pdf` (e.g., `resume_20260424.pdf`) before uploading.
- **Bot Bypass:** Uses `undetected-chromedriver` to securely navigate Naukri's anti-bot protections.
- **Zero Local Compute:** Runs entirely in the cloud via GitHub Actions.

## Setup Instructions

1. **Add your Credentials to GitHub Secrets:**
   Go to your repository settings -> **Secrets and variables** -> **Actions** -> **New repository secret**.
   Add the following secrets:
   - `NAUKRI_EMAIL` : Your Naukri login email
   - `NAUKRI_PASSWORD` : Your Naukri login password
   
2. **Resume Location:**
   Ensure your base resume is located in the root of the repository and named `Resume.pdf`.

3. **Enable Actions:**
   Go to the **Actions** tab in your repository and enable workflows.

4. **Test it out:**
   In the Actions tab, select **Naukri Resume Update**, click **Run workflow**, and verify the logs!

## Schedule
The workflow is configured to run at **3:30 AM UTC** which translates to **9:00 AM IST** daily.
You can adjust this by editing the `.github/workflows/naukri-update.yml` file.
