import time
import random
import re
import imaplib
import email
import subprocess

from appium import webdriver
from appium.options import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Rellenar como pavo
DEVICE_HOST = 
DEVICE_PORT = 
APPIUM_URL  = 

APP_PACKAGE = "com.amazon.mShop.android.shopping"
APP_ACTIVITY = ".main.MainActivity"

# Aquí también 
PROXY_HOST = 
PROXY_PORT = 

NOMBRE     = 
CORREO     = 
CONTRASENA = 

IMAP_HOST = 
IMAP_USER = 
IMAP_PASS = 

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; SM-S911B Build/TP1A.220624.014) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.6367.82 Mobile Safari/537.36"
)


def adb(cmd):
    r = subprocess.run(
        f"adb -s {DEVICE_HOST}:{DEVICE_PORT} {cmd}",
        shell=True, capture_output=True, text=True,
    )
    return r.stdout.strip()

def conectar_dispositivo():
    subprocess.run(f"adb connect {DEVICE_HOST}:{DEVICE_PORT}", shell=True)
    time.sleep(2)

def limpiar_app():
    adb(f"shell pm clear {APP_PACKAGE}")
    adb(f"shell rm -rf /sdcard/Android/data/{APP_PACKAGE}/cache/")
    adb("shell cmd package trim-caches 1000000000")
    time.sleep(1)

def resetear_google_ad_id():
    adb("shell am broadcast -a com.google.android.gms.ads.RESET_ADVERTISING_ID")
    time.sleep(1)

def limpiar_portapapeles():
    adb("shell am broadcast -a clipper.set --es text ''")

def set_proxy():
    adb(f"shell settings put global http_proxy {PROXY_HOST}:{PROXY_PORT}")
    time.sleep(1)

def quitar_proxy():
    adb("shell settings put global http_proxy :0")

def preparar_dispositivo():
    conectar_dispositivo()
    limpiar_app()
    resetear_google_ad_id()
    limpiar_portapapeles()
    set_proxy()


def crear_driver():
    opts = UiAutomator2Options()
    opts.platform_name           = "Android"
    opts.device_name             = f"{DEVICE_HOST}:{DEVICE_PORT}"
    opts.udid                    = f"{DEVICE_HOST}:{DEVICE_PORT}"
    opts.app_package             = APP_PACKAGE
    opts.app_activity            = APP_ACTIVITY
    opts.no_reset                = False
    opts.full_reset              = False
    opts.auto_grant_permissions  = True
    opts.new_command_timeout     = 120
    opts.set_capability("appium:chromeOptions", {"args": [f"--user-agent={USER_AGENT}"]})
    return webdriver.Remote(APPIUM_URL, options=opts)


def pausa(mn=0.8, mx=1.8):
    time.sleep(random.uniform(mn, mx))

def escribir(elemento, texto, delay=0.07):
    elemento.click()
    pausa(0.3, 0.6)
    for char in texto:
        elemento.send_keys(char)
        time.sleep(random.uniform(0.04, delay))

def scroll_hasta(driver, elemento):
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", elemento
    )
    pausa(0.5, 1.0)

def esperar_webview(driver, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        ctx = next((c for c in driver.contexts if "WEBVIEW" in c), None)
        if ctx:
            return ctx
        time.sleep(1)
    raise RuntimeError("WebView no apareció en el tiempo esperado")

def esperar_otp(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(IMAP_USER, IMAP_PASS)
            mail.select("INBOX")
            _, ids = mail.search(None, 'UNSEEN SUBJECT "Amazon"')
            for mid in ids[0].split()[::-1]:
                _, data = mail.fetch(mid, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                match = re.search(r"\b(\d{6})\b", body)
                if match:
                    mail.logout()
                    return match.group(1)
            mail.logout()
        except Exception:
            pass
        time.sleep(8)
    return None

def verificar_exito(driver):
    for sel in [
        "#ap_email_confirmed_notification",
        "[data-cel-widget='nav-logo-sprites']",
        "#nav-belt",
        ".nav-logo-link",
    ]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel)
            return True
        except Exception:
            pass
    try:
        url = driver.current_url
        if any(p in url for p in ["/gp/css/homepage", "/gp/yourstore", "/?ref=nav_logo"]):
            return True
    except Exception:
        pass
    return False


def flujo_registro(driver):
    wait = WebDriverWait(driver, 30)

    sign_in_btn = wait.until(EC.element_to_be_clickable(
        (By.ID, f"{APP_PACKAGE}:id/sign_in_button")
    ))
    pausa()
    sign_in_btn.click()

    ctx = esperar_webview(driver)
    driver.switch_to.context(ctx)
    pausa(1, 2)

    crear_link = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "#createAccountSubmit, a[href*='register'], [data-nav-target*='register']",
    )))
    scroll_hasta(driver, crear_link)
    pausa(0.5, 1.0)
    crear_link.click()
    pausa(2, 3.5)

    campo_nombre = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "input[name='customerName']")
    ))
    scroll_hasta(driver, campo_nombre)
    escribir(campo_nombre, NOMBRE)
    pausa()

    campo_email = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
    scroll_hasta(driver, campo_email)
    escribir(campo_email, CORREO)
    pausa()

    campo_pass = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    scroll_hasta(driver, campo_pass)
    escribir(campo_pass, CONTRASENA)
    pausa()

    try:
        campo_pass2 = driver.find_element(By.CSS_SELECTOR, "input[name='passwordCheck']")
        scroll_hasta(driver, campo_pass2)
        escribir(campo_pass2, CONTRASENA)
        pausa()
    except Exception:
        pass

    continuar_btn = driver.find_element(By.CSS_SELECTOR, "input[id='continue'], [type='submit']")
    scroll_hasta(driver, continuar_btn)
    pausa(0.5, 1.2)
    continuar_btn.click()
    pausa(2, 4)

    otp = esperar_otp(timeout=120)
    if otp is None:
        raise RuntimeError("OTP no recibido en 120 segundos")

    campo_otp = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        "input[name='code'], input[id='cvf-input-code'], input[autocomplete='one-time-code']",
    )))
    scroll_hasta(driver, campo_otp)
    escribir(campo_otp, otp, delay=0.12)
    pausa()

    verificar_btn = driver.find_element(By.CSS_SELECTOR, "input[id='continue'], [type='submit']")
    scroll_hasta(driver, verificar_btn)
    verificar_btn.click()
    pausa(4, 6)

    if verificar_exito(driver):
        print(f"[OK] Cuenta registrada: {CORREO}")
    else:
        print("[WARN] Flujo completado sin confirmación visual. Verificar manualmente.")


def main():
    preparar_dispositivo()
    driver = crear_driver()
    try:
        flujo_registro(driver)
    finally:
        driver.quit()
        quitar_proxy()

if __name__ == "__main__":
    main()
