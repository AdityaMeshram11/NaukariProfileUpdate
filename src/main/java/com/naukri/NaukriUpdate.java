package com.naukri;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.*;

import java.io.*;
import java.nio.file.*;
import java.time.Duration;
import java.util.Base64;

public class NaukriUpdate {

    // ── Environment variable names ──────────────────────────────────────────
    private static final String ENV_EMAIL      = "NAUKRI_EMAIL";
    private static final String ENV_PASSWORD   = "NAUKRI_PASSWORD";
    private static final String ENV_RESUME_B64 = "RESUME_PDF_BASE64";

    // ── Naukri URLs ─────────────────────────────────────────────────────────
    private static final String NAUKRI_LOGIN_URL   = "https://www.naukri.com/nlogin/login";
    private static final String NAUKRI_PROFILE_URL = "https://www.naukri.com/mnjuser/profile";

    public static void main(String[] args) throws Exception {
        String email    = requireEnv(ENV_EMAIL);
        String password = requireEnv(ENV_PASSWORD);
        String resumeB64 = requireEnv(ENV_RESUME_B64);

        // Decode Base64 resume → temp PDF file
        Path resumePath = decodePdf(resumeB64);
        System.out.println("[INFO] Resume decoded to: " + resumePath);

        WebDriver driver = buildDriver();

        try {
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(30));

            // ── Step 1: Login ────────────────────────────────────────────────
            System.out.println("[INFO] Navigating to login page...");
            driver.get(NAUKRI_LOGIN_URL);

            wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("usernameField")));
            driver.findElement(By.id("usernameField")).sendKeys(email);
            driver.findElement(By.id("passwordField")).sendKeys(password);
            driver.findElement(By.xpath("//button[contains(@class,'loginButton') or @type='submit']")).click();

            System.out.println("[INFO] Logging in...");
            // Wait until login completes (URL changes away from login page)
            wait.until(ExpectedConditions.not(
                ExpectedConditions.urlContains("nlogin")
            ));
            System.out.println("[INFO] Login successful.");

            // ── Step 2: Go to profile ────────────────────────────────────────
            System.out.println("[INFO] Navigating to profile page...");
            driver.get(NAUKRI_PROFILE_URL);
            Thread.sleep(3000); // Let the profile page fully load

            // ── Step 3: Delete existing resume ───────────────────────────────
            System.out.println("[INFO] Looking for existing resume delete button...");
            try {
                WebElement deleteBtn = wait.until(
                    ExpectedConditions.elementToBeClickable(
                        By.xpath("//span[contains(@class,'delete') and ancestor::*[contains(@class,'resumeupload') or contains(@class,'resume')]]")
                    )
                );
                deleteBtn.click();
                System.out.println("[INFO] Clicked delete button.");

                // Handle confirmation popup if present
                try {
                    WebElement confirmBtn = new WebDriverWait(driver, Duration.ofSeconds(5))
                        .until(ExpectedConditions.elementToBeClickable(
                            By.xpath("//button[contains(text(),'Delete') or contains(text(),'Yes') or contains(text(),'Confirm')]")
                        ));
                    confirmBtn.click();
                    System.out.println("[INFO] Confirmed deletion.");
                } catch (TimeoutException ignored) {
                    System.out.println("[INFO] No confirmation popup found, continuing.");
                }

                Thread.sleep(2000); // Wait for deletion to complete

            } catch (TimeoutException e) {
                System.out.println("[WARN] No existing resume found (or already deleted). Proceeding to upload.");
            }

            // ── Step 4: Upload new resume ────────────────────────────────────
            System.out.println("[INFO] Uploading new resume...");

            // Locate the file input (may be hidden; use JS to make it visible if needed)
            WebElement fileInput = wait.until(
                ExpectedConditions.presenceOfElementLocated(
                    By.xpath("//input[@type='file' and (contains(@id,'resume') or contains(@name,'resume') or contains(@class,'resume'))]")
                )
            );

            // Make it interactable in case it's hidden
            ((JavascriptExecutor) driver).executeScript("arguments[0].style.display='block';", fileInput);
            fileInput.sendKeys(resumePath.toAbsolutePath().toString());
            System.out.println("[INFO] Resume file path sent to input.");

            // Wait for upload to complete (success message or header update)
            try {
                wait.until(ExpectedConditions.or(
                    ExpectedConditions.visibilityOfElementLocated(
                        By.xpath("//*[contains(text(),'successfully') or contains(text(),'uploaded') or contains(text(),'Updated')]")
                    ),
                    ExpectedConditions.visibilityOfElementLocated(
                        By.xpath("//*[contains(@class,'success') or contains(@class,'successMsg')]")
                    )
                ));
                System.out.println("[SUCCESS] Resume uploaded successfully!");
            } catch (TimeoutException e) {
                System.out.println("[WARN] Could not confirm upload via success message. Please check manually.");
            }

        } finally {
            driver.quit();
            System.out.println("[INFO] Browser closed.");
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    private static String requireEnv(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(
                "Required environment variable not set: " + name
            );
        }
        return value;
    }

    private static Path decodePdf(String base64) throws IOException {
        byte[] pdfBytes = Base64.getDecoder().decode(base64.trim());
        Path tempFile = Files.createTempFile("naukri_resume_", ".pdf");
        Files.write(tempFile, pdfBytes);
        return tempFile;
    }

    private static WebDriver buildDriver() {
        // Auto-setup ChromeDriver matching installed Chrome
        WebDriverManager.chromedriver().setup();

        ChromeOptions options = new ChromeOptions();
        options.addArguments(
            "--headless=new",        // No display (server/CI environment)
            "--no-sandbox",          // Required in CI
            "--disable-dev-shm-usage", // Overcome limited resource errors
            "--disable-gpu",
            "--window-size=1920,1080",
            "--disable-blink-features=AutomationControlled" // Reduce bot detection
        );

        // Mask webdriver flag to reduce bot detection
        options.setExperimentalOption("excludeSwitches", new String[]{"enable-automation"});
        options.setExperimentalOption("useAutomationExtension", false);

        WebDriver driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        return driver;
    }
}
