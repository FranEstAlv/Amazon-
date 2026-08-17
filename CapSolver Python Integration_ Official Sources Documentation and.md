# Documentación de integración de CapSolver para Python (según fuentes oficiales)

## TL;DR
- **Postman NO resuelve la tarea como fuente oficial**: la única colección de Postman ("CapSolver API Docs", del publicador `lunar-module-explorer-32486427`) NO pudo confirmarse como publicación oficial verificada de CapSolver, y el sitio oficial no enlaza a ninguna colección de Postman; por tanto se pasó a GitHub y al sitio oficial según el orden de prioridad.
- **GitHub SÍ resuelve el SDK de Python**: existe un repositorio de la organización oficial `github.com/capsolver` llamado `capsolver-python`, cuyo README se autodenomina "Capsolver official python library" (paquete PyPI `capsolver`, versión publicada más reciente `1.0.7`, licencia MIT, instalable con `pip3 install --upgrade capsolver`), con ejemplos de código Python literales.
- **El sitio oficial `docs.capsolver.com` resuelve la API HTTP**: Base URLs `https://api.capsolver.com` y `https://api-stable.capsolver.com`, autenticación por `clientKey`, endpoints `createTask`, `getTaskResult`, `getBalance`, `getToken`, tabla de códigos de error y una extensión de navegador oficial documentada.

## Key Findings

**Paso 1 — Confirmación del servicio.** El servicio es CapSolver, dominio `capsolver.com`; documentación en `docs.capsolver.com`. (Fuente: Sitio oficial.)

**Paso 2 — Postman (prioridad 1): NO resuelto como oficial.** Existe en la Postman Public API Network un workspace "CapSolver API Docs" / "CapSolver" publicado por el usuario `lunar-module-explorer-32486427`. Sin embargo:
- El handle `lunar-module-explorer-32486427` es un nombre autogenerado por Postman (patrón de dos palabras + número), típico de una cuenta individual no verificada, no de una cuenta de equipo/organización de marca.
- No se pudo confirmar la presencia de una insignia "verified"/"official" de Postman (las páginas del workspace se renderizan por JavaScript y `web_fetch` devolvió solo un shell vacío).
- El sitio oficial (`capsolver.com` y `docs.capsolver.com`) NO enlaza a ninguna colección/workspace de Postman: no hay entrada "Postman" ni botón "Run in Postman" en la navegación superior ni en el pie de página. Los cinco enlaces del footer de `docs.capsolver.com` son `api.capsolver.com/invite/group/tg_global`, `/qq`, `/youtube`, `/twitter` y `/discord`; ninguno apunta a Postman.
- **Conclusión**: La colección de Postman debe tratarse como NO verificada / de comunidad, NO confirmada como oficial de CapSolver. Por la regla de exclusión y de prioridad, no se usa como fuente autoritativa. (Fuente: Postman + verificación cruzada con Sitio oficial.)

Requests/carpetas que sí se pudieron confirmar por título/URL dentro de esa colección de Postman (no confirmada como oficial): `RecaptchaV2EnterpriseTask`, `RecaptchaV2TaskProxyless`, carpeta `Akamai`, carpeta `Proxy`, y la página raíz "CapSolver API Docs | Get Started". El contenido interno completo (cuerpos de solicitud/respuesta exactos, cabeceras) no pudo extraerse porque las páginas se renderizan por JavaScript. (Fuente: Postman.)

**Paso 3 — GitHub (prioridad 2): resuelve el SDK oficial de Python.** La organización oficial es `github.com/capsolver` (verificada mediante el enlace `https://www.capsolver.com` en el perfil de la organización y su listado de repositorios). Repositorios de la organización relevantes:
- `capsolver/capsolver-python` — "Capsolver official python library" (biblioteca oficial de Python). [github](https://github.com/capsolver/capsolver-python)
- `capsolver/capsolver-go` — biblioteca oficial de Go. [github](https://github.com/capsolver/capsolver-go)
- `capsolver/capsolver-browser-extension` — extensión oficial de navegador.
- `capsolver/n8n-nodes-capsolver` — descrito oficialmente como "The official CapSolver community node for n8n. This node allows you to seamlessly integrate CapSolver's captcha solving capabilities directly into your n8n workflows".
- (Organización relacionada `capsolver-ai` con `capsolver-skills`, `capsolver-agent`, `capsolver-mcp`, `capsolver-core`.)
(Fuente: GitHub.)

**Paso 4 — Sitio oficial (prioridad 3): resuelve la API HTTP completa.** `docs.capsolver.com` documenta Base URLs, autenticación, endpoints, parámetros, respuestas y códigos de error. (Fuente: Sitio oficial.)

**DISCREPANCIA IMPORTANTE entre fuentes oficiales sobre "SDK de Python oficial":**
- En `github.com/capsolver/capsolver-python`, el propio README se describe verbatim como "Capsolver ... Capsolver official python library", con tipos soportados "Geetest · ReCaptchaV2 · ReCaptchav3 · MtCaptcha · Cloudflare · Amazon captcha(AWS WAF)" (paquete `capsolver` en PyPI). (Fuente: GitHub.)
- En cambio, la página oficial `docs.capsolver.com/en/guide/api-server/` (sección "SDK"), bajo un aviso "DANGER", afirma verbatim: "The following libraries are not officially produced by the CapSolver team, we cannot guarantee that the libraries is practical or safe. Please use with caution." Y para Python lista exactamente `https://github.com/AndreiDrang/python3-captchaai` y `https://github.com/Matthew17-21/Captcha-Tools` — es decir, NO lista `capsolver/capsolver-python`. (Fuente: Sitio oficial.)
- No obstante, otra página del sitio oficial (`docs.capsolver.com/en/guide/api-getbalance/`) SÍ incluye un ejemplo Python que usa `import capsolver` / `capsolver.balance()` y el comentario `#pip install --upgrade capsolver`, que corresponde al paquete del repo `capsolver/capsolver-python`. (Fuente: Sitio oficial.)
- Esta contradicción se reporta tal cual, sin resolverla por criterio propio.

## Details

### 1. Qué es CapSolver y para qué sirve (Fuente: Sitio oficial)
Según `docs.capsolver.com/en/guide/what-is-capsolver/` (literal): "CapSolver is the supplier in the market that supports the most types of CAPTCHA recognition services, including reCAPTCHA (v2/v3/Enterprise), (Normal/Enterprise), Cloudflare, ImageToText, DataDome, GeeTest V3/V4, AWS Captcha, and more. Our services can handle over 95% of CAPTCHA needs worldwide." [Capsolver](https://docs.capsolver.com/en/guide/what-is-capsolver/) Es un servicio 100% IA/machine learning para resolver CAPTCHAs, con API y extensiones de navegador para Chrome y Firefox.

**Tipos de captcha soportados** (Fuente: Sitio oficial — navegación de `docs.capsolver.com`, secciones Task(Recognition) y Task(Token)):
- Task (Recognition): `ImageToText`, `reCAPTCHA v2` (clasificación), `AWS WAF` (clasificación), `VisionEngine`. [capsolver](https://docs.capsolver.com/en/guide/getting-started/)
- Task (Token): `Geetest`, `reCAPTCHA v2`, `reCAPTCHA v3`, `MTCaptcha`, `DataDome`, `AWS WAF`, `Cloudflare Turnstile`, `Cloudflare Challenge`. [capsolver](https://docs.capsolver.com/en/guide/getting-started/)

(Fuente: GitHub — `capsolver/capsolver-browser-extension`) La extensión soporta el reconocimiento de: reCAPTCHA v2, v3, reCAPTCHA v2 invisible, enterprise, Geetest, AWS Waf Captcha, Amazon Captcha, Cloudflare v3 (Turnstile) Captcha e ImageToText. [GitHub](https://github.com/capsolver/capsolver-browser-extension)

### 2. Base URL(s) (Fuente: Sitio oficial — `api-server`)
CapSolver ofrece 2 puertos de servidor:
- Server-A: `https://api.capsolver.com` [capsolver](https://docs.capsolver.com/en/guide/api-server/)
- Server-B: `https://api-stable.capsolver.com` [capsolver](https://docs.capsolver.com/en/guide/api-server/)

Advertencia oficial (literal): "You can access it directly using your local ip. [Capsolver](https://docs.capsolver.com/en/guide/api-server/) Do not use proxies to access it, or you will be blocked by cloudflare's WAF and be disabled by the server's ip." [Capsolver](https://docs.capsolver.com/en/guide/api-server/)

### 3. Autenticación (Fuente: Sitio oficial)
La autenticación se realiza mediante una API key llamada `clientKey`, incluida en el cuerpo JSON de cada solicitud POST. Se obtiene tras registrarse, desde el panel del dashboard. [Capsolver](https://docs.capsolver.com/en/guide/getting-started/) [capsolver](https://docs.capsolver.com/en/guide/getting-started/) Parámetro opcional `appId` (para desarrolladores; se solicita en la sección de desarrollador del dashboard).
- En el SDK de Python (`capsolver/capsolver-python`) la clave se define con la variable de entorno `CAPSOLVER_API_KEY` o asignando `capsolver.api_key`. [github](https://github.com/capsolver/capsolver-python)

### 4. Endpoints principales (Fuente: Sitio oficial)

**createTask** — `POST https://api.capsolver.com/createTask`
Parámetros de solicitud (tabla oficial):
- `clientKey` (String, Sí): clave de cuenta del cliente, en el dashboard.
- `appId` (String, No): appId de desarrollador.
- `task` (Object, Sí): objeto de la tarea.
- `callbackUrl` (String, No): endpoint al que se enviará (POST) el token. [capsolver](https://docs.capsolver.com/en/guide/api-createtask/)

Ejemplo de solicitud (literal, Sitio oficial):
```
POST https://api.capsolver.com/createTask
Host: api.capsolver.com
Content-Type: application/json

{
    "clientKey":"YOUR_API_KEY",
    "appId": "APP_ID",
    "task": {
        "type":"ImageToTextTask",// Write below the type you need to identify
        "body":"BASE64 image"
    }
}
```
Respuesta asíncrona (literal): `{ "errorId": 0, "errorCode": "", "errorDescription": "", "taskId": "37223a89-06ed-442c-a0b8-22067b79c5b4" }`. [Capsolver](https://docs.capsolver.com/en/guide/api-createtask/)
Respuesta síncrona (literal): incluye `"status": "ready"` y `"solution": { "text": "44795sds" }`. [GitHub](https://github.com/ERIZOAT/solve-amazon-captcha-python)
Estructura de respuesta: `errorId` (0 sin error / 1 con error), `errorCode`, `errorDescription`, `status` (null o `ready`), `solution` (objeto), `taskId`. [capsolver](https://docs.capsolver.com/en/guide/api-createtask/)

**getTaskResult** — `POST https://api.capsolver.com/getTaskResult`
Ejemplo (literal): `{ "clientKey": "YOUR_API_KEY", "taskId": "37223a89-06ed-442c-a0b8-22067b79c5b4" }`.
Respuesta exitosa (literal): `{ "errorId": 0, "solution": { "userAgent": "xxx", "gRecaptchaResponse": "03AGdBq25..." }, "status": "ready" }`. [Capsolver](https://docs.capsolver.com/en/guide/getting-started/)
Reglas oficiales: éxito cuando `errorId == 0` y `status == ready`; en proceso cuando `errorId == 0` y `status == processing` (reintentar en ~3 s); error cuando `errorId > 0`. [Capsolver](https://docs.capsolver.com/en/guide/api-gettaskresult/) El número máximo de consultas por tarea es 120; cada tarea puede consultarse dentro de los 5 minutos posteriores a su creación, tras lo cual se pierde. [Capsolver](https://docs.capsolver.com/en/guide/api-gettaskresult/) Generalmente el resultado llega en 1–10 s. [Capsolver](https://docs.capsolver.com/en/guide/captcha/ReCaptchaV2/) [Capsolver](https://docs.capsolver.com/en/guide/getting-started/)

**getBalance** — `POST https://api.capsolver.com/getBalance`
Solicitud (literal): `{ "clientKey": "YOUR_API_KEY" }`. [Capsolver](https://docs.capsolver.com/en/guide/api-getbalance/)
Respuesta (literal): `{ "errorId": 0, "balance": 1234567, "packages": [ { "packageId": "12327bff7f703e135e7379kf", "type": 2, "title": "reCAPTCHA v2 500K", "numberOfCalls": 1234567, "status": 1, "token": "CAP-1234567C19044AF7351B31EC12345678", "expireTime": 1702896511 } ] }`.

**getToken** — `POST https://api.capsolver.com/getToken`
Solicitud (literal): `{ "clientKey":"YOUR_API_KEY", "appId": "APP_ID", "task": { "type":"ReCaptchaV3TaskProxyLess", "websiteURL": "https://demo.com/", "websiteKey": "6LcpsXsnAAAAAbbAcafeiCCr3xxx2UeZ8qef1Hbb" } }`. [Capsolver](https://docs.capsolver.com/en/guide/api-getToken/)
Respuesta (literal): `{ "errorId": 0, "taskId": "...", "solution": { "gRecaptchaResponse": "03AGdBq25..." }, "status": "ready" }`. [Capsolver](https://docs.capsolver.com/en/guide/api-getToken/)

**getstate** — listado en la lista de interfaces del sitio oficial (`api-getstate`); [capsolver](https://docs.capsolver.com/en/guide/api-server/) no se detalló su contenido completo en esta consulta más allá de que existe → **contenido completo no especificado en la documentación oficial consultada**.

### 5. Parámetros comunes / proxy (Fuente: Sitio oficial — `api-use-params`)
Ejemplo de parámetros con proxy (literal, extracto): campos `proxyType` (socks5|http|https), `proxyAddress`, `proxyPort`, `proxyLogin`, `proxyPassword`, o el formato compacto `"proxy": "socks5:192.191.100.10:4780:user:pwd"`. [Capsolver](https://docs.capsolver.com/en/guide/api-use-params/) Los tipos de tarea que llevan `ProxyLess` no requieren proxy. [Capsolver](https://docs.capsolver.com/en/guide/api-use-params/)

### 6. Códigos de error (Fuente: Sitio oficial — `api-error`)
Tabla de códigos de respuesta: 200/errorId 0 = SUCCESS; 400/errorId 1 = ERROR; 401/errorId 1 = Unauthorized (API key incorrecta). [capsolver](https://docs.capsolver.com/en/guide/api-error/)
Tabla de códigos de error (literal): `ERROR_SERVICE_UNAVALIABLE`, `ERROR_RATE_LIMIT`, `ERROR_INVALID_TASK_DATA`, `ERROR_BAD_REQUEST`, `ERROR_TASKID_INVALID`, `ERROR_TASK_TIMEOUT`, `ERROR_SETTLEMENT_FAILED`, `ERROR_KEY_DENIED_ACCESS`, `ERROR_ZERO_BALANCE`, `ERROR_TASK_NOT_SUPPORTED`, `ERROR_CAPTCHA_UNSOLVABLE`, `ERROR_UNKNOWN_QUESTION`, `ERROR_PROXY_BANNED`, `ERROR_INVALID_IMAGE`, `ERROR_PARSE_IMAGE_FAIL`, `ERROR_IP_BANNED`, `ERROR_KEY_TEMP_BLOCKED`.
Detalles relevantes de límites/bloqueos (literal): `ERROR_TASK_TIMEOUT` = si la resolución no tiene éxito en 120 s, error de timeout; `ERROR_IP_BANNED` = si ocurren muchos errores (hasta 1000) en poco tiempo (dentro de 1 minuto), el sistema bloquea automáticamente por 30 minutos; `ERROR_KEY_TEMP_BLOCKED` = bloqueo por demasiados errores, desbloqueo automático en 5 minutos. [capsolver](https://docs.capsolver.com/en/guide/api-error/)

### 7. Límites de tasa (Fuente: Sitio oficial)
Existe un código de error `ERROR_RATE_LIMIT` ("Service packages request rate limit... you have exceeded the rate limit"). [capsolver](https://docs.capsolver.com/en/guide/api-error/) El sitio oficial no especifica un número concreto de solicitudes por segundo permitidas en la documentación consultada → **no especificado en la documentación oficial consultada**. Límites relacionados sí especificados: máximo 120 consultas por tarea en `getTaskResult`; ventana de 5 minutos para consultar resultados. [Capsolver](https://docs.capsolver.com/en/guide/api-gettaskresult/)

### 8. SDK/librería oficial de Python (Fuente: GitHub `capsolver/capsolver-python`)
Descripción del repo (literal): "Capsolver official python library." [github](https://github.com/capsolver/capsolver-python)
Tipos de CAPTCHA soportados (según README): Geetest, ReCaptchaV2, ReCaptchaV3, MtCaptcha, Cloudflare, Amazon captcha (AWS WAF). [github](https://github.com/capsolver/capsolver-python)
Instalación (literal): `pip3 install --upgrade capsolver` (o `python setup.py install` desde el código fuente). [github](https://github.com/capsolver/capsolver-python) La versión publicada más reciente en PyPI es `capsolver 1.0.7` (licencia MIT), descrita en `pypi.org/project/capsolver` como "Capsolver official python library".
Configuración de la clave (literal): `export CAPSOLVER_API_KEY='...'` o `capsolver.api_key = "..."`. [github](https://github.com/capsolver/capsolver-python)

Ejemplo de código Python (literal del README oficial `capsolver/capsolver-python`):
```python
from pathlib import Path
import os
import base64
import capsolver

# tokenTask
print("api host",capsolver.api_base)
print("api key",capsolver.api_key)
# capsolver.api_key = "..."
solution = capsolver.solve({
        "type":"ReCaptchaV2TaskProxyLess",
        "websiteKey":"6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        "websiteURL":"https://www.google.com/recaptcha/api2/demo",
    })

print(solution)

# RecognitionTask
img_path = os.path.join(Path(__file__).resolve().parent,"queue-it.jpg")
with open(img_path,'rb') as f:
    solution = capsolver.solve({
        "type":"ImageToTextTask",
        "module":"queueit",
        "body":base64.b64encode(f.read()).decode("utf8")
    })
    print(solution)

# get current balance
balance = capsolver.balance()
# print the current balance
print(balance)
```
El sitio oficial también incluye, en la página `getBalance`, un ejemplo Python literal equivalente (pestaña "python"):
```python
#pip install --upgrade capsolver
#export CAPSOLVER_API_KEY='...'
import capsolver
# capsolver.api_key = "..."
balance = capsolver.balance()
```

Nota de discrepancia (ver Key Findings): la página `api-server` del sitio oficial declara que las bibliotecas de terceros listadas allí no son oficiales y NO incluye `capsolver/capsolver-python` en esa lista, mientras que el repositorio de la organización oficial `capsolver` sí se autodenomina biblioteca oficial. Se reporta tal cual, sin resolver.

### 9. SDK "CapSolver AI" para Python (Fuente: Sitio oficial — `guide/ai/...`)
El sitio oficial documenta una familia de SDKs para Python: `capsolver-core` (motor), `capsolver-agent` (herramientas para LLM) y `capsolver-mcp` (servicio MCP). [Capsolver](https://docs.capsolver.com/en/guide/ai/introduction-and-quick-start/) Según la página oficial "Introduction & Quick Start" (literal): "The three packages are currently hosted as open source on GitHub and are not yet published to PyPI, so install them via git." [Capsolver](https://docs.capsolver.com/en/guide/ai/introduction-and-quick-start/) Instalación (literal): `pip install git+https://github.com/capsolver-ai/capsolver-core.git`. [Capsolver](https://docs.capsolver.com/en/guide/ai/introduction-and-quick-start/) Entradas principales: `create_capsolver()` → `solve()` / `solve_on_page()`. [Capsolver](https://docs.capsolver.com/en/guide/ai/introduction-and-quick-start/) Estos repos están bajo la organización `capsolver-ai` en GitHub.

### 10. Extensión de navegador oficial (Fuente: Sitio oficial + GitHub)
(Sitio oficial — `guide/extension/introductions/`, literal) "Official CapSolver browser extension for Chrome and Firefox, which automatically solves any CAPTCHAs in the background using artificial intelligence algorithms." [Capsolver](https://docs.capsolver.com/en/guide/extension/introductions/) Permite pasar proxies propios en formatos HTTP, HTTPS, SOCKS4 y SOCKS5. [Capsolver](https://docs.capsolver.com/en/guide/extension/introductions/) Instalable desde Chrome Web Store, Firefox Add-ons o descargando el ZIP desde el GitHub oficial. [Capsolver](https://docs.capsolver.com/en/guide/extension/introductions/)

Sobre soporte de navegadores hay una diferencia menor de redacción entre fuentes oficiales:
- (GitHub — README `capsolver/capsolver-browser-extension`, literal): "Browser extension is supported in Chrome, with Firefox, Opera, and Edge planning support in the near future."
- (Sitio oficial — `extension/introductions/`, literal): "supported in Chrome and Firefox, Opera and Edge planning support in the near future."
Se reportan ambas versiones tal cual.

Integración con Python/Selenium (Sitio oficial — `extension/settings_for_developers`), ejemplo literal:
```python
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_extension("./capSolver_extension.zip") # Path to the zip file of the plugin
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://google.com/")
```

## Recommendations
1. **Para integración por API HTTP en Python**: usar directamente los endpoints REST del sitio oficial (`https://api.capsolver.com`) con la librería `requests`, siguiendo el flujo `createTask` → `getTaskResult` (o `getToken`/respuesta síncrona para tareas de reconocimiento). No existe ejemplo de código con `requests` puro en la documentación oficial consultada para este flujo → **no encontrado en fuentes oficiales**; los únicos ejemplos Python literales oficiales son los del SDK `capsolver` (mostrados arriba) y el fragmento de Selenium para la extensión.
2. **Para usar el SDK de Python**: instalar `pip3 install --upgrade capsolver` (versión actual `1.0.7`) y emplear el patrón `capsolver.solve({...})` / `capsolver.balance()` del repo oficial `capsolver/capsolver-python`. Tener presente la discrepancia entre fuentes oficiales sobre si este SDK es "oficial".
3. **Para flujos con navegador/agentes IA**: evaluar los SDK `capsolver-core`/`capsolver-agent`/`capsolver-mcp` (org `capsolver-ai`), instalables solo vía git según el sitio oficial.
4. **Manejo de errores y reintentos**: implementar comprobación de `errorId`/`status`, respetar el máximo de 120 consultas por tarea y la ventana de 5 minutos, y espaciar los sondeos para evitar `ERROR_RATE_LIMIT`/`ERROR_IP_BANNED`.
5. **No usar Postman como fuente autoritativa** hasta que CapSolver publique/enlace oficialmente una colección verificada.

**Umbrales que cambiarían estas recomendaciones**: si CapSolver enlazara una colección de Postman desde `docs.capsolver.com` o publicara con una cuenta verificada, Postman pasaría a ser fuente prioritaria; si el sitio oficial actualizara la sección "SDK" para incluir `capsolver/capsolver-python`, se resolvería la discrepancia sobre el SDK oficial.

## Caveats
- **Postman**: la colección existente NO se confirmó como oficial (publicador con handle autogenerado, sin insignia verificada confirmable, sin enlace desde el sitio oficial). Las páginas del workspace se renderizan por JavaScript, por lo que no se pudo extraer su contenido interno completo.
- **Discrepancia sobre SDK Python "oficial"**: reportada tal cual entre GitHub (`capsolver-python` = "official python library") y el sitio oficial (`api-server` lista solo terceros no oficiales y omite ese repo). No se resuelve por criterio propio.
- **Discrepancia menor sobre navegadores soportados por la extensión** entre README de GitHub y el sitio oficial: reportada tal cual.
- **Límite de tasa numérico**: no especificado en la documentación oficial consultada.
- **getstate**: existe en la lista de interfaces oficial pero su contenido completo no se detalló en esta investigación → no especificado en la documentación oficial consultada.
- **Regla de exclusión**: no se emplearon blogs, foros, tutoriales ni fuentes de terceros como base de los hechos reportados; toda afirmación se atribuye a Postman, GitHub o el Sitio oficial. (PyPI se usa únicamente como registro de distribución del paquete oficial `capsolver`, coherente con el repo oficial de GitHub.)
- **Ejemplos de código**: solo se reprodujeron ejemplos literales presentes en fuentes oficiales (GitHub `capsolver/capsolver-python` y `docs.capsolver.com`). No se inventó código.