# 2Captcha API — Python Integration Documentation (Sourced via Strict Protocol)

## TL;DR
- **The service name is confirmed as "2Captcha" (2captcha.com).** Following the strict source-priority order, **Postman has NO official 2Captcha collection**; the request is resolved by **GitHub** (the verified official org `github.com/2captcha`, which publishes the official Python SDK `2captcha-python`) and, for the underlying raw HTTP endpoints/parameters/errors that the SDK README defers to, by the **Official Website** (`2captcha.com/api-docs` and `2captcha.com/2captcha-api`).
- 2Captcha solves image/normal captcha, reCAPTCHA v2/v3, and — per the official `2captcha-python` README — 32 named captcha types (Normal, Audio, Text, reCAPTCHA v2, reCAPTCHA v3, FunCaptcha, GeeTest, GeeTest v4, Yandex Smart, Lemin Cropped, Cloudflare Turnstile, Amazon WAF, KeyCaptcha, atbCAPTCHA, Capy, Grid, Canvas, ClickCaptcha, Rotate, MTCaptcha, Friendly Captcha, Cutcaptcha, Tencent, DataDome, VKImage, VKCaptcha, CaptchaFox, Prosopo, Temu, CyberSiARA, Altcha, Binance). Authentication is by a 32-character **API key** ("clientKey" in API v2, "key" in API v1). Two coexisting official APIs exist: **API v1** (`https://2captcha.com/in.php` + `https://2captcha.com/res.php`) [2captcha](https://2captcha.com/2captcha-api) and **API v2** (`https://api.2captcha.com/createTask` + `https://api.2captcha.com/getTaskResult`). [2captcha](https://2captcha.com/api-docs/create-task)
- The official Python SDK (`pip3 install 2captcha-python`, [pypi](https://pypi.org/project/2captcha-python) `from twocaptcha import TwoCaptcha`; latest release **v2.0.7, dated May 29, 2026**, 758 stars / 135 forks) wraps both submit-and-poll steps into single methods (`solver.normal`, `solver.recaptcha`, `solver.balance`, `solver.report`), and is the only literal Python code published by 2Captcha itself.

---

## Key Findings

**Source per finding is explicitly labelled [Postman] / [GitHub] / [Official Website].**

1. **[Step 1 — Service name] CONFIRMED.** The service is "2Captcha" at 2captcha.com. Not substituted with Anti-Captcha, CapMonster, etc.
2. **[Step 2 — Postman] NEGATIVE RESULT.** No official 2Captcha-published Postman collection or workspace could be found in the Postman Public API Network. All 2Captcha-related Postman assets found are third-party/community — e.g. "Manuel Valls's Public Workspace" (username `mvallsz`), a "Captcha" workspace by the auto-generated handle `spacecraft-astronaut-5476427`, and a generically-named `captcha-solver` handle with no verifiable tie to the company. None is a verified 2Captcha corporate account, and neither 2captcha.com nor github.com/2captcha links to any Postman workspace. The exclusion rule bars these, so they were NOT used.
3. **[Step 3 — GitHub] RESOLVED (primary).** The official org `github.com/2captcha` is GitHub-**Verified** — GitHub states it "verified that the organization 2captcha controls the domain: 2captcha.com". It publishes the official Python 3 SDK `2captcha/2captcha-python` (MIT license). [github](https://github.com/2captcha/2captcha-python) This provides Python installation, configuration, authentication, and per-captcha methods literally.
4. **[Official Website] Used only for items the SDK README defers to** — the underlying HTTP endpoints, base URLs, request/response parameters, error codes, and rate-limit guidance, which are not defined literally in the GitHub SDK README.

---

## Details

### A. What the 2Captcha API is used for
- **[GitHub]** 2Captcha is a captcha-solving / image-recognition service. The official `2captcha-python` README (github.com/2captcha/2captcha-python) enumerates 32 named solver methods, verbatim: "Normal Captcha, Audio Captcha, Text Captcha, reCAPTCHA v2, reCAPTCHA v3, FunCaptcha, GeeTest, GeeTest v4, Yandex Smart, Lemin Cropped Captcha, Cloudflare Turnstile, Amazon WAF, KeyCaptcha, atbCAPTCHA, Capy, Grid, Canvas, ClickCaptcha, Rotate, MTCaptcha, Friendly Captcha, Cutcaptcha, Tencent, DataDome, VKImage, VKCaptcha, CaptchaFox, Prosopo, Temu, CyberSiARA, Altcha Captcha, Binance."
- **Note on hCaptcha:** hCaptcha is **not among the 32 named methods** in the current official `2captcha-python` README method list. However, **[GitHub]** the SDK's own `twocaptcha/solver.py` module docstring does reference it: "This class provides methods for solving various types of CAPTCHAs, such as image CAPTCHAs, audio CAPTCHAs, reCAPTCHAs, hCAPTCHAs, and others." This is a source-level discrepancy reported as-is; no dedicated `solver.hcaptcha(...)` method appears in the README method list consulted.
- **[Official Website]** The API v1 intro states: "2Captcha is a human-powered image and captcha recognition service… You can convert to text any image that a human can recognize." [2Captcha](https://2captcha.com/2captcha-api) [2captcha](https://2captcha.com/2captcha-api) The 4-step flow: (1) send image/captcha, (2) get task ID, (3) poll to check if completed, (4) get the result. [2Captcha](https://2captcha.com/2captcha-api)

### B. Base URLs / API endpoints

**[Official Website] — API v1** (`https://2captcha.com/2captcha-api`):
- Submit a captcha: `https://2captcha.com/in.php` (HTTP POST) [2Captcha](https://2captcha.com/2captcha-api)
- Get the solution: `https://2captcha.com/res.php` (HTTP GET) [2Captcha](https://2captcha.com/2captcha-api)
- Verbatim: "Our API is based on HTTP requests and supports both HTTP and HTTPS protocols." [2Captcha](https://2captcha.com/2captcha-api)

**[Official Website] — API v2** (`https://2captcha.com/api-docs`):
- `https://api.2captcha.com/createTask` — Method: POST, Content-Type: application/json [2Captcha](https://2captcha.com/api-docs/create-task) [2captcha](https://2captcha.com/api-docs/create-task)
- `https://api.2captcha.com/getTaskResult` — Method: POST, Content-Type: application/json [2captcha](https://2captcha.com/api-docs/get-task-result)
- `https://api.2captcha.com/getBalance` — POST, application/json [2Captcha](https://2captcha.com/api-docs/get-balance)
- `https://api.2captcha.com/reportCorrect` — POST, application/json [2Captcha](https://2captcha.com/api-docs/report-correct)
- `https://api.2captcha.com/reportIncorrect` — POST, application/json [2Captcha](https://2captcha.com/api-docs/report-incorrect)
- `https://api.2captcha.com/test` — POST, application/json (debugging/sandbox) [2Captcha](https://2captcha.com/api-docs/debugging)

**[GitHub]** The Python SDK's default `server` config value is `2captcha.com` (can be set to `rucaptcha.com` if the account is registered there). [GitHub](https://github.com/2captcha/2captcha-python) The SDK README and code reference the `res.php` API endpoint for polling, indicating the SDK is built on the API v1 in.php/res.php transport.

### C. Authentication
- **[Official Website — API v2 Quick start]** "To use the API you need to obtain your API key from the Dashboard. The key is used to authenticate all your requests to the API endpoints." [2Captcha](https://2captcha.com/api-docs/quick-start)
- **[Official Website — API v1]** "Each user is given a unique authentication token, we call it API key. It's a 32-characters string [2Captcha](https://2captcha.com/2captcha-api) that looks like: `1abc234de56fab7c89012d34e56fa7b8`." [2Captcha](https://2captcha.com/2captcha-api) In API v1 it is passed as the `key` parameter; in API v2 as the `clientKey` JSON property.
- **[GitHub — Python SDK]** Authentication is supplied when constructing the client: `solver = TwoCaptcha('YOUR_API_KEY')`. [pypi +2](https://pypi.org/project/2captcha-python) There is no separate header-based auth; the API key is the credential.

### D. Python SDK — installation, configuration, methods (all [GitHub], literal)

Installation (verbatim):
```
pip3 install 2captcha-python
```

Configuration (verbatim):
```
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('YOUR_API_KEY')
```
Async (verbatim):
```
from twocaptcha import AsyncTwoCaptcha

solver = AsyncTwoCaptcha('YOUR_API_KEY')
```
Full options object (verbatim):
```
config = {
            'server':           '2captcha.com',
            'apiKey':           'YOUR_API_KEY',
            'softId':            123,
            'callback':         'https://your.site/result-receiver',
            'defaultTimeout':    120,
            'recaptchaTimeout':  600,
            'pollingInterval':   10,
            'extendedResponse':  False
        }
solver = TwoCaptcha(**config)
```

**[GitHub] TwoCaptcha instance options** (verbatim from README):
| Option | Default | Description |
|---|---|---|
| server | `2captcha.com` | API server. Can be set to `rucaptcha.com` if account registered there |
| softId | 4580 | software ID obtained after publishing in 2captcha software catalog |
| callback | - | URL of your web server that receives the captcha recognition result (must be registered in pingback settings) |
| defaultTimeout | 120 | Polling timeout (s) for all captcha types except reCAPTCHA [pypi](https://pypi.org/project/2captcha-python) (polls res.php) |
| recaptchaTimeout | 600 | Polling timeout (s) for reCAPTCHA [pypi](https://pypi.org/project/2captcha-python) (polls res.php) |
| pollingInterval | 10 | Interval (s) between requests to res.php; values below 5s not recommended [pypi](https://pypi.org/project/2captcha-python) |
| extendedResponse | None | Set `True` to enable JSON response from res.php; suitable for ClickCaptcha, Canvas |

**[GitHub]** Important behavior note (verbatim): "Once `callback` is defined for the `TwoCaptcha` instance, all methods return only the captcha ID and DO NOT poll the API to get the result. The result will be sent to the callback URL." [GitHub](https://github.com/2captcha/2captcha-python) [github](https://github.com/2captcha/2captcha-python)

**[GitHub] Main Python methods — literal method signatures from README:**
- Normal captcha: `result = solver.normal('path/to/captcha.jpg', param1=..., ...)` (also accepts a URL) [GitHub](https://github.com/2captcha/2captcha-python)
- Audio: `result = solver.audio('path/to/captcha.mp3', lang = 'lang', param1=..., ...)` — supported languages "en", "ru", "de", "el", "pt", "fr" [GitHub](https://github.com/2captcha/2captcha-python)
- Text: `result = solver.text('If tomorrow is Saturday, what day is today?', param1=..., ...)` [pypi](https://pypi.org/project/2captcha-python) [github](https://github.com/2captcha/2captcha-python)
- reCAPTCHA v2: `result = solver.recaptcha(sitekey='6Le-wvkSVVABCPBMRTvw0Q4Muexq1bi0DJwx_mJ-', url='https://mysite.com/page/with/recaptcha', param1=..., ...)`
- reCAPTCHA v3: `result = solver.recaptcha(sitekey='6Le-wvkSVVABCPBMRTvw0Q4Muexq1bi0DJwx_mJ-', url='...', version='v3', param1=..., ...)`
- FunCaptcha: `result = solver.funcaptcha(sitekey='...', url='...', param1=..., ...)` [github](https://github.com/2captcha/2captcha-python)
- GeeTest: `result = solver.geetest(gt='f1ab2cdefa3456789012345b6c78d90e', challenge='12345678abc90123d45678ef90123a456b', url='https://www.site.com/page/', param1=..., ...)`
- Cloudflare Turnstile: `result = solver.turnstile(sitekey='...', url='...', ...)` [github](https://github.com/2captcha/2captcha-python)
- Amazon WAF: `result = solver.amazon_waf(sitekey='...', iv='...', context='...', url='...', ...)` [github](https://github.com/2captcha/2captcha-python)
- Grid: `result = solver.grid('path/to/captcha.jpg', ...)` [github](https://github.com/2captcha/2captcha-python)
- Coordinates/ClickCaptcha: `result = solver.coordinates('path/to/captcha.jpg', ...)` [github](https://github.com/2captcha/2captcha-python)
- Balance: `balance = solver.balance()` [2Captcha](https://2captcha.com/lang/python) [github](https://github.com/2captcha/2captcha-python)
- Report: `solver.report(id, True)  # correct` / `solver.report(id, False)  # incorrect` [2Captcha](https://2captcha.com/lang/python) [github](https://github.com/2captcha/2captcha-python)
- Manual submit/poll: `id = solver.send(file='path/to/captcha.jpg')` then `code = solver.get_result(id)` [github](https://github.com/2captcha/2captcha-python)

**[GitHub] Image-captcha options** (verbatim table): numeric (0), minLen (0), maxLen (0), phrase (0), caseSensitive (0), calc (0), lang (-), hintImg (-), hintText (-). [github](https://github.com/2captcha/2captcha-python)

**[GitHub] Error handling** (verbatim): the SDK throws exceptions [2Captcha](https://2captcha.com/lang/python) `ValidationException`, `NetworkException`, `ApiException`, `TimeoutException`, recommended handled with try/except. [2Captcha](https://2captcha.com/lang/python) [github](https://github.com/2captcha/2captcha-python)

**[GitHub] Proxy format** (verbatim): `proxy={'type': 'HTTPS', 'uri': 'login:password@IP_address:PORT'}`. [github](https://github.com/2captcha/2captcha-python)

**[GitHub] Async example** (verbatim): replace `TwoCaptcha` with `AsyncTwoCaptcha`; supports the same methods; can run multiple captchas with `asyncio.gather`. [github](https://github.com/2captcha/2captcha-python)

### E. Official Python raw-HTTP example (no SDK) — [Official Website]
On the createTask docs page, an official Python (requests) example is present in the page source (inside an HTML comment block) using `https://api.2captcha.com/createTask`:
```python
import requests
import json

url = "https://api.2captcha.com/createTask"

payload = json.dumps({
  "clientKey": "1326ce1386fc2db6f75a1c69387645b8",
  "task": {
    "type": "RecaptchaV2TaskProxyless",
    "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
    "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
  }
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```
Additionally, per-captcha docs pages (e.g. reCAPTCHA v2/v3, Text) provide official Python examples that use the SDK, e.g. (verbatim):
```python
# https://github.com/2captcha/2captcha-python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from twocaptcha import TwoCaptcha
api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')
solver = TwoCaptcha(api_key)
try:
    result = solver.recaptcha(
        sitekey='6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
        url='https://2captcha.com/demo/recaptcha-v2')
except Exception as e:
    sys.exit(e)
else:
    sys.exit('solved: ' + str(result))
```

### F. API v2 request/response structure — [Official Website]

**createTask request properties** (verbatim table):
| Name | Type | Required | Description |
|---|---|---|---|
| clientKey | String | Yes | Your API key |
| task | Object | Yes | Task object (see Captcha task types) |
| languagePool | String | No | Worker language. Default `en`. `en`=English, `ru`=Russian |
| callbackUrl | String | No | URL of registered web server to receive result |
| softId | Integer | No | ID of your software in the Software catalog |

createTask request example (verbatim):
```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2TaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
    }
}
```
createTask response example (verbatim):
```json
{
    "errorId": 0,
    "taskId": 72345678901
}
```

**getTaskResult request properties** (verbatim): `clientKey` (String, Yes), `taskId` (Integer, Yes). [2captcha](https://2captcha.com/api-docs/get-task-result)
getTaskResult responses (verbatim):
- In progress: `{"errorId": 0, "status": "processing"}` [2Captcha](https://2captcha.com/api-docs/get-task-result) [2captcha](https://2captcha.com/api-docs/get-task-result)
- Failed: `{"errorId": 12, "errorCode": "ERROR_CAPTCHA_UNSOLVABLE", "errorDescription": "Workers could not solve the Captcha"}` [2Captcha](https://2captcha.com/api-docs/get-task-result) [2captcha](https://2captcha.com/api-docs/get-task-result)
- Completed:
```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {},
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```
Response spec (verbatim): errorId (Integer), status (String: ready | processing), solution (Object, format depends on task type), cost (String), ip (String), createTime (Integer), endTime (Integer), solveCount (Integer). [2captcha](https://2captcha.com/api-docs/get-task-result)

**Example task types [Official Website]:** `RecaptchaV2TaskProxyless`, `RecaptchaV2Task` (with userAgent/cookies/proxyType/proxyAddress/proxyPort/proxyLogin/proxyPassword), [2Captcha](https://2captcha.com/api-docs/recaptcha-v2) `RecaptchaV3TaskProxyless` (with minScore, pageAction, isEnterprise, apiDomain), [2Captcha](https://2captcha.com/api-docs/recaptcha-v3) `RecaptchaV2EnterpriseTask/Proxyless`, `TextCaptchaTask` (comment), [2Captcha](https://2captcha.com/api-docs/text) `ImageToTextTask` (body, phrase, case, numeric, math, minLength, maxLength, comment), [2Captcha](https://2captcha.com/api-docs/normal-captcha) `GridTask` (body, comment, rows, columns), [2Captcha](https://2captcha.com/api-docs/grid) `CoordinatesTask` (body, comment), [2Captcha](https://2captcha.com/api-docs/coordinates) `KeyCaptchaTask/Proxyless`, [2Captcha](https://2captcha.com/api-docs/keycaptcha) `AlibabaTask`. [2Captcha](https://2captcha.com/api-docs/alibaba-captcha)

- **getBalance** request/response (verbatim): request `{"clientKey": "YOUR_API_KEY"}` → `{"errorId": 0, "balance": 0.93958}`. [2Captcha](https://2captcha.com/api-docs/get-balance)
- **reportCorrect / reportIncorrect** request (verbatim): `{"clientKey": "YOUR_API_KEY", "taskId": 74455221488}` → `{"errorId": 0, "status": "success"}`. [2Captcha](https://2captcha.com/api-docs/report-correct) [2Captcha](https://2captcha.com/api-docs/report-incorrect)

Official raw-HTTP Python report example [Official Website, how-to guide]:
```python
import requests
API_KEY = "YOUR_API_KEY"
TASK_ID = "123456789"
# Report for an incorrect solution
requests.post("https://api.2captcha.com/reportIncorrect", json={"clientKey": API_KEY, "taskId": TASK_ID})
# Report for a correct solution
requests.post("https://api.2captcha.com/reportCorrect", json={"clientKey": API_KEY, "taskId": TASK_ID})
```

### G. API v1 request/response structure — [Official Website]
- Submit (`in.php`, POST): `key` (String, Yes), `method` (String, Yes — `post`=multipart image, `base64`=base64 image), `file` (File, required if method=post), `body` (String, required if method=base64), plus optional `phrase`, `regsense`, `numeric`, `calc`, `min_len`, `max_len`, `language`, `lang`, `textinstructions`, `imginstructions`, `header_acao`, `pingback`, `json`, `soft_id`. [2captcha](https://2captcha.com/2captcha-api)
- On success returns captcha ID as plain text `OK|2122988149` or JSON `{"status":1,"request":"2122988149"}` if `json=1`.
- Poll (`res.php`, GET): `key` (Yes), `action=get` (Yes), `id` (Yes), optional `json`, `header_acao`. [2captcha](https://2captcha.com/2captcha-api) Request example (verbatim): `https://2captcha.com/res.php?key=1abc234de56fab7c89012d34e56fa7b8&action=get&id=2122988149` [2captcha](https://2captcha.com/2captcha-api)
- If solved returns `OK|TEXT` (or JSON `{"status":1,"request":"TEXT"}`); if not ready returns `CAPCHA_NOT_READY` — "Repeat your request in 5 seconds." [2Captcha](https://2captcha.com/2captcha-api)
- reCAPTCHA v3 in v1 uses `method=userrecaptcha`, [2Captcha](https://2captcha.com/2captcha-api) `version=v3`, `min_score`, `googlekey`, `pageurl`, optional `action`. [2Captcha](https://2captcha.com/2captcha-api) Score range 0.1–0.9; "Our service is able to provide solutions which requires the score of 0.3." [2Captcha](https://2captcha.com/2captcha-api)

### H. Error codes — [Official Website] (API v2 error-codes reference, verbatim)
| Id | Code | Description |
|---|---|---|
| 0 | - | No errors |
| 1 | ERROR_KEY_DOES_NOT_EXIST | Your API key is incorrect |
| 2 | ERROR_NO_SLOT_AVAILABLE | Your bid is too low or your captcha queue is too long |
| 3 | ERROR_ZERO_CAPTCHA_FILESIZE | Image size < 100 bytes |
| 4 | ERROR_TOO_BIG_CAPTCHA_FILESIZE | Image > 100 kB or bigger than 600px on any side |
| 5 | ERROR_PAGEURL | `websiteURL` missing or malformed |
| 10 | ERROR_ZERO_BALANCE | No funds on account |
| 11 | ERROR_IP_NOT_ALLOWED | Request from an IP not on your trusted IP list |
| 12 | ERROR_CAPTCHA_UNSOLVABLE | Three workers could not solve; price auto-refunded |
| 13 | ERROR_BAD_DUPLICATES | 100% accuracy feature: max tries reached, min matches not found |
| 14 | ERROR_NO_SUCH_METHOD | Method does not exist |
| 15 | ERROR_IMAGE_TYPE_NOT_SUPPORTED | Image cannot be processed (format/size/corrupt) |
| 16 | ERROR_NO_SUCH_CAPCHA_ID | Incorrect captcha ID |
| 21 | ERROR_IP_BLOCKED | IP banned for improper API use |
| 22 | ERROR_TASK_ABSENT | `task` property missing in createTask |
| 23 | ERROR_TASK_NOT_SUPPORTED | task type not supported / error in `type` |
| 31 | ERROR_RECAPTCHA_INVALID_SITEKEY | sitekey not valid |
| 55 | ERROR_ACCOUNT_SUSPENDED | API access blocked for improper use |
| 110 | ERROR_BAD_PARAMETERS | Required captcha parameters missing/malformed |
| 115 | ERROR_BAD_IMGINSTRUCTIONS | imgInstructions unsupported/corrupt/over limit |
| 130 | ERROR_BAD_PROXY | Incorrect proxy parameters or connection failed |

**[Official Website]** HTTP response codes note (verbatim): "If our API is able to process your requests properly the response status code is always 200 OK… if it is not 200 OK then wait few seconds and repeat the request." [2Captcha](https://2captcha.com/api-docs/error-codes)

The API v1 page also documents a separate list of `in.php`/`res.php` plain-text errors (e.g. ERROR_WRONG_USER_KEY, ERROR_KEY_DOES_NOT_EXIST, [Blogger](https://2captchablogger.blogspot.com/2019/) ERROR_ZERO_BALANCE, ERROR_PAGEURL, ERROR_NO_SLOT_AVAILABLE, CAPCHA_NOT_READY).

### I. Rate limits — [Official Website] (Request limits page, verbatim)
"Please remember and understand that each of your requests to our API generates multiple requests to our databases." Guidance:
- If server returns ERROR_NO_SLOT_AVAILABLE → 5-second timeout before next request.
- If server returns ERROR_ZERO_BALANCE → 60-second timeout.
- After uploading a captcha, wait at least 1–2 seconds (API v1 page says 5s, 10–20s for reCAPTCHA) before trying to get the answer.
- If captcha not solved yet → retry in 5 seconds.
- "If your timeouts are configured incorrectly your account or IP address will be temporarily blocked and server will return an error."
No fixed requests-per-second numeric limit is stated in the official sources consulted.

---

## Recommendations

1. **Use the official GitHub Python SDK (`2captcha-python`, latest release v2.0.7 dated May 29, 2026) as the primary integration path.** It is the only Python code published by 2Captcha itself and wraps submit+poll into one call. Start: `pip3 install 2captcha-python`, then `from twocaptcha import TwoCaptcha; solver = TwoCaptcha('YOUR_API_KEY')`.
2. **If you need raw HTTP control, target API v2** (`createTask` + `getTaskResult` at `api.2captcha.com`, JSON POST). Poll `getTaskResult` no more often than every 5 seconds and treat `status: processing` as "retry".
3. **Implement the documented timeout/backoff rules** (5s on ERROR_NO_SLOT_AVAILABLE, 60s on ERROR_ZERO_BALANCE) to avoid IP/account blocks. Handle SDK exceptions (`ValidationException`, `NetworkException`, `ApiException`, `TimeoutException`).
4. **Report solutions back** with `solver.report(id, True/False)` (SDK) or `reportCorrect`/`reportIncorrect` (API v2) to get refunds on rejected tokens.
5. **Thresholds that would change the approach:** if you require hCaptcha specifically, note the source-level ambiguity — the `solver.py` docstring mentions "hCAPTCHAs" but the README exposes no dedicated `hcaptcha()` method in the 32-method list; verify current support directly on the official docs before committing. If you need a Postman collection specifically, note none exists officially — build requests manually from the API v2 JSON examples above.

## Caveats
- **Postman step returned a negative result.** No official 2Captcha Postman collection/workspace exists; only third-party/community ones (`mvallsz`, `spacecraft-astronaut-5476427`, `qweqd2q3e`, and an unverified `captcha-solver` handle) — all excluded by protocol. Limitation: Postman.com pages are JavaScript-rendered, so publisher bylines could not be read verbatim; ownership was inferred from Postman URL usernames and search-result titles, and none is a verified 2Captcha corporate account.
- **Two APIs coexist.** The website presents API v1 (in.php/res.php) and API v2 (createTask/getTaskResult) simultaneously; the official Python SDK's internal transport references res.php (v1-style), while the website's raw examples emphasize v2. This is a source-level coexistence, reported as-is, not resolved.
- **hCaptcha discrepancy (as-is):** hCaptcha is NOT in the official `2captcha-python` README's 32-method list, but the SDK's `twocaptcha/solver.py` module docstring does list "hCAPTCHAs" among supported types. Reported without resolution; no dedicated README method was found.
- **softId default discrepancy (as-is):** the SDK README config example shows `'softId': 123`, while both the SDK options table and the `TwoCaptcha.__init__` constructor in `twocaptcha/solver.py` set the default to `softId=4580`. Reported without resolution.
- Items not explicitly stated in the official sources consulted (e.g., a numeric requests-per-second cap) are reported as "not specified in the official documentation consulted."
- Placeholder values (`YOUR_API_KEY`, example site keys, `1.2.3.4`, timestamps, `1326ce1386fc2db6f75a1c69387645b8`) are reproduced exactly as they appear in the official sources; no example code was invented.