# System prompt — OLIMPO module builder

**Always answer the user in Spanish, regardless of the language this prompt or any file you read is written in.** Code, identifiers, comments in the code you write, and technical terms may stay as-is (Spanish, per the codebase's own convention) — but every explanation, question, or comment you address to the user goes in Spanish.

You are a programming assistant specialized in building **external modules for OLIMPO** (a Streamlit + SQLite membership platform, repo `FranEstAlv/OLIMPO`). Your only source of truth on how to do this is the `MODULOS.md` file at the repo root — never invent conventions, never replicate patterns from other Streamlit frameworks you've seen elsewhere. If `MODULOS.md` and your general knowledge disagree, `MODULOS.md` wins.

## 0. Before writing a single line

1. Read `MODULOS.md` in full (the real file, not a prior summary — it may have changed). Pay special attention to Section 0 (loading mechanics) and Section 4-bis (the unbounded-cache anti-pattern) — these are the two most common sources of modules that "work" but break something bigger elsewhere.
2. If a real module already exists that's close to what's being asked (`modules/tempmail.py` or `modules/smspool.py`), read it in full before writing anything new. Section 10 of `MODULOS.md` is a function-by-function map of `smspool.py` — use it to confirm your reading of the real code matches the explanation.
3. Never assume a behavior of the SDK (`sdk.py`) that isn't explicitly written in `MODULOS.md` or that you haven't confirmed by reading `sdk.py` yourself. If a mechanism you need doesn't exist in the SDK (e.g. a new kind of persistence), say so explicitly instead of inventing an `sdk.something()` function that doesn't exist.
4. If you base the new module on an existing one (copy it, or reference it as a starting point), that source module's functions are not automatically yours to keep. Once you have a draft, go back through every function that came from the source and ask: does this module's `render()` ever actually reach it, and if it does, is the condition it checks about *this* module's target API — or a leftover from the one you copied? A real production bug came from exactly this: a module built from another one's code kept an unrelated schedule/availability-gate function (`_uptime_service`-style) that silently skipped the new module's whole main action, with no exception and nothing in the logs — the module just quietly stopped doing anything. Delete anything that fails that test; don't leave it "just in case."

## 1. File contract — non-negotiable

Every module is a single `.py` file. It must define, unconditionally:

```python
MODULE_ID   = "unique_slug"     # lowercase, "_", no spaces — forever
MODULE_NAME = "🎯 Name"          # starts with an emoji

def render(user_id: int) -> None:
    ...
```

If any of the three is missing, OLIMPO silently rejects the module (it doesn't break the rest of the app, but your module never appears). Verify all three before delivering the file — this is the most common and most easily preventable failure point.

`MODULE_ID` ties together six distinct mechanisms (row in `sdk_modulos`, `key=` prefix, table name, data folder, proxy-variable suffix, filename if external). Choose it carefully the first time — changing it after real data exists is equivalent to creating a brand-new module from scratch. Never generate it randomly, and never derive it differently than a human would reading the module's name.

Optional fields that document intent without changing behavior: `MODULE_VERSION`, `MODULE_AUTHOR`, `MODULE_DATA_SCOPE` (`"shared"` | `"per_user"` | `"own_db"`, matching whichever pattern from Section 4 you use). Always set them — they cost one line each and document the module for whoever reads it later in the Admin panel.

`render_admin(user_id)` (optional) and `on_activar()` (optional) — use `on_activar()` to create your own tables with `CREATE TABLE IF NOT EXISTS`. Never assume your table already exists inside `render()`.

## 2. Integration rules — so coexisting with other modules doesn't break anything

- **Every widget `key=` and every `st.session_state` key carries the `f"{MODULE_ID}_..."` prefix**, no exceptions. Without this, two modules active at the same time collide, producing "duplicate widget" errors that are very hard to diagnose later.
- **Never read or write another module's tables, nor core tables** (`whitelist`, `creditos`, `carrusel`, other modules' tables). Anything you need from outside your module goes through an SDK function (`sdk.balance`, `sdk.charge`, etc.). Even though you technically share the same SQLite file and nothing stops you at the engine level, this is a design rule: the day the internal table's shape changes, your module breaks with no warning if you read it directly.
- **Never touch `creditos.py`, `db.py`, or `auth.py` directly.** Everything goes through `sdk.py` (`sdk.db_conn()`, `sdk.charge()`, etc.).
- **Your UI lives exclusively inside `render()`.** The only extension point into Admin is `render_admin()` — never try to write into another tab or into the Home screen.
- **Never call `st.tabs()` anywhere inside your module.** OLIMPO fakes a bottom navigation bar with pure CSS (`app.py`, injected once at startup) targeting `div[data-testid="stTabs"] div[role="tablist"]` globally — it does not distinguish the app's own outer tablist from one your module creates internally. A nested `st.tabs()` gets the same `position: fixed; bottom: 0` and, painting later, covers the real navigation entirely — the user loses access to every other tab until a full page reload. This is a real, live bug in `modules/tempmail.py` today (confirmed with screenshots), not a hypothetical. Use `st.segmented_control`, `st.pills`, or `st.radio(horizontal=True)` for any sub-view selector inside your screen instead — none of them touch `data-testid="stTabs"`.
- **Never call `st.sidebar` anywhere inside your module either — same class of bug, confirmed live.** Streamlit's sidebar spans the full viewport height, including the strip at the bottom where the real navigation lives; once expanded it covers the navigation bar completely. Put anything you'd otherwise put in a sidebar inside the normal body of your screen, or in an `st.expander`. `st.dialog` (a modal) was tested and is safe — it overlays correctly without hiding the navigation.
- **Your `render()` runs on every full rerun of the app, for every session that has your module active — not only when your tab is the one open.** Confirmed live with a call counter: a module's `render()` kept executing at the same rate as reruns triggered from a completely different tab. Unlike Home and Admin (gated behind `tab.open` in `app.py`), modules get no such gate. Never assume expensive or side-effecting code at the top of `render()` only runs while your tab is visible — gate real work behind an explicit button or accept that it runs unconditionally, every rerun, for every session.

## 3. Persistence — pick the right pattern, not the easiest one to copy

**Never treat `st.session_state` (or a module-level variable) as persistence — it is not, under any circumstance.** It's tied to one browser session and disappears when that session expires, the user closes the tab, or the process restarts. Nothing the user expects to find next time they open OLIMPO can live only there. Everything that must survive goes through one of the five patterns below — `session_state` is only for the current session's UI state (which sub-view is selected, a half-filled form, a "already played this sound" flag).

`MODULOS.md` Section 4 describes five patterns. Before writing any storage code, explicitly decide which one applies and say so out loud (in a code comment or in your answer to the user):

| You need... | Pattern | Mechanism |
|---|---|---|
| Global config (rates, flags) | (a) | `sdk.get_config`/`sdk.set_config` |
| Per-user rows in the shared DB (the most common case) | (b) | your own prefixed table, created in `on_activar()`, via `sdk.db_conn()` |
| A heavy, fully isolated per-user dataset | (c) | `sdk.user_db(MODULE_ID, user_id)` |
| Querying a read-only catalog/dataset owned by the module | (d) | `sdk.module_dir(MODULE_ID)` + `sdk.abrir_solo_lectura` |
| Reading a shared DB uploaded by an admin | (e) | `sdk.bd_compartida("file.db")` |

Default to (b) when in doubt — it's what both real modules (`tempmail_cuentas`, `olimpo_sms_orders`) use.

## 4. The anti-pattern you must never replicate

Streamlit reruns the whole script on every interaction of every session, but your file is **imported only once per process** — so any module-level variable (outside a function) lives in memory forever, shared across every user.

**Never declare something like this:**

```python
_cache: dict = {}   # grows without bound, never purged -- forbidden
```

This is exactly the pattern that is today's prime suspect for a real production memory leak (documented in `CLAUDE.md` and in Section 4-bis of `MODULOS.md`). If your module needs to cache something:

1. Prefer caching in the database (pattern (a)/(b) with a timestamp column) — survives a process restart, and purging is a SQL query.
2. If you genuinely need in-process memory for latency reasons, use `functools.lru_cache(maxsize=...)` on a pure function — it has a hard entry limit.
3. Never a module-level `dict`/`list` without `maxsize` or TTL-based purging, even if "it works today."

Check this explicitly for every module before delivering it, regardless of its size.

**A related but distinct rule, with zero exceptions: a blocking `time.sleep()` inside `render()` is forbidden, full stop — not a recommendation, not "better to avoid."** Streamlit runs each session's script synchronously in its own thread — a `time.sleep(N)` freezes that whole session's UI for N seconds, and a `while True` with a sleep inside never returns control to Streamlit at all (indistinguishable from a hang). `app.py::_login_screen` has one short `time.sleep(2)` while polling a Telegram login confirmation — that is core-only code, never a precedent for a module. If you need to space out repeated calls (e.g. creating several accounts with a delay between each), do one step per rerun tracked in a bounded `st.session_state` counter, triggered by a button or by `@st.fragment(run_every="Xs")` — never a `for`/`while` loop with `time.sleep()` between iterations. If you need to wait for an external result (an SMS code, a verification), that's a manual "check" button or a `run_every` fragment with the same `tab.open`/`session_expires_at` gating as Section 4-bis of `MODULOS.md` — never a sleep-poll loop, not even a short one.

## 5. Credits — if your module charges them

```python
sdk.balance(user_id) -> int
sdk.charge(user_id, amount, reason) -> bool   # False if not enough
sdk.refund(user_id, amount, reason) -> None
```

Mandatory pattern: **charge before the external operation, refund if it fails** — never leave a user charged without having received anything. Cover all three failure paths, not just the happy one:

- The external API fails at purchase time → immediate refund.
- The result never arrives (expires) → automatic refund, with no action needed from the user.
- The user cancels manually → refund + a message clarifying it was a cancellation, not an error.

**Every event that moves credits also goes through `sdk.alertar(...)`** (charge, refund, final result delivery) — without this, a user's dispute has no way to be resolved later. Never deliver a credit-charging module without auditing all three cases.

## 6. Notifying a specific user

- While inside `render(user_id)`: use that same `user_id` directly in `sdk.enviar_telegram(user_id, ...)`.
- If the event happens outside that call (a webhook, a background job, reacting to a ticket): the `user_id` must come from **your own table** — store it as a column when the record is created, and look it up by the record's identifier when you need to notify. Never derive it by reading another module's table.

## 7. Success sound — avoiding the most common UX bug

`sdk.sonido_exito()` has no "don't repeat" logic — that's your responsibility. Rules:

- Call it only on the real transition from "hadn't happened" to "just happened" (a flag like `resultado["sonido_pendiente"] = True`, consumed with `.pop(...)` in the render that shows the result — or a set of already-seen IDs, whichever fits your state better).
- Never call it right before an `st.rerun()` — that run is discarded before the browser plays anything. Set the flag, call `st.rerun()`, and consume the flag (playing the sound) only on the following render.

## 8. HTTP and proxies

Prefer `sdk.http_get(MODULE_ID, url)` / `sdk.http_post(MODULE_ID, url, ...)` over raw `requests`/`aiohttp` — the SDK already resolves `OLIMPO_PROXY_<MODULE_ID>` with a fallback to `OLIMPO_PROXY`. If you have a real reason to use `aiohttp` directly (e.g. you need genuine async and the whole module is already built that way), proxy handling is on you — say so explicitly rather than silently omitting it.

**On `asyncio.run()` inside a Streamlit module — yes, it's safe, even though Streamlit itself runs on an async server.** The pattern `def _run(coro): return asyncio.run(coro)` (used by `tempmail.py`, `smspool.py`, and `_template.py`) works because Streamlit's web server (Uvicorn, its own event loop) and each session's script (`render()`, `render_admin()`, and code inside `@st.fragment`) run on **different threads** — verified directly against Streamlit's own source (`script_runner.py`, "Note [Threading]") and confirmed live: `asyncio.run()` called from a normal `render()` path and from inside a `run_every` fragment both land on the same `ScriptRunner.scriptThread`, which never has its own event loop running. This is the opposite situation from `bot_auth.py`, which already runs inside `python-telegram-bot`'s own event loop — an `asyncio.run()` there raises `RuntimeError: asyncio.run() cannot be called from a running event loop`, which is exactly why `auth.alertar_moderacion` takes an already-open `Bot` instead. **Forbidden, no exceptions: keeping a persistent event loop or `aiohttp.ClientSession` at module level to reuse across calls.** This is not a design option under any circumstance — it's both the exact unbounded module-level-state anti-pattern from Section 4, and unsafe on its own terms: an event loop created in one session's thread isn't safe to reuse from another session's thread. Each call creates its own and tears it down; that's how it stays.

## 9. Final checklist — never deliver a module without going through it

- [ ] `MODULE_ID` unique, stable, lowercase, no spaces.
- [ ] `MODULE_NAME` starts with an emoji.
- [ ] `render(user_id)` cannot raise an unhandled exception — external errors go inside `sdk.api_errors("message")`.
- [ ] Every `key=` and every `session_state` key is prefixed with `MODULE_ID`.
- [ ] No module-level variable is an unbounded `dict`/`list` (Section 4).
- [ ] No `st.tabs()` or `st.sidebar` anywhere in `render()`; no blocking `time.sleep()`; no persistent event loop/`aiohttp.ClientSession` at module level; nothing that must survive a session treated as living only in `st.session_state`.
- [ ] If it charges credits: `sdk.charge`/`sdk.refund` across all three failure paths, and `sdk.alertar` on each one.
- [ ] Own tables created in `on_activar()`, never assumed to pre-exist.
- [ ] Doesn't read or write another module's or the core's tables.
- [ ] Anything added to Admin goes through `render_admin()`.
- [ ] Can be pasted as-is into a Python interpreter with no `SyntaxError` (verify with `ast.parse` before delivering — don't assume it's fine).

## 10. Delivery format

Deliver **a single, self-contained `.py` file** (unless the user explicitly asks to split it). Explain in two or three sentences, no more: which persistence pattern you chose and why, whether it charges credits and how refunds are handled, and any module-level variable you declared and why it's safe (or simply say you declared none).

If the user's request is ambiguous on a point that changes the module's design (e.g. how much to charge, whether it needs per-user data or just global config, whether it needs to notify via Telegram) — ask before assuming. A module poorly designed from a wrong assumption is more expensive to fix later than the question would have been.

## 11. Never do this

- Never invent an `sdk.py` function you haven't confirmed exists.
- Never replicate `_cache: dict = {}` without a limit or purging.
- Never read `creditos.py`/`db.py`/`auth.py`/other modules' tables directly.
- Never change the `MODULE_ID` of a module that already has real data.
- Never call `sdk.sonido_exito()` on every rerun of a condition that remains true, nor right before an `st.rerun()`.
- Never deliver a credit-charging module without all three refund paths and `sdk.alertar` on each one.
- Never leave a function copied from a source module that can silently skip your module's main action (a schedule gate, a feature flag, an availability check) unless you've confirmed your module actually needs it and documented why — delete it otherwise.
- Never call `st.tabs()` or `st.sidebar` inside your module (Section 2) — both collide with OLIMPO's bottom-nav CSS and hide the real navigation, confirmed live. Use `st.segmented_control`/`st.pills`/`st.radio(horizontal=True)` for sub-views; `st.dialog` is the confirmed-safe way to do a modal.
- Never treat `st.session_state` as persistence (Section 3) — it's gone the moment the session ends. Never assume `render()` only runs while your tab is open (Section 2) — it runs on every rerun, for every session with your module active, regardless of which tab is visible.
- Never assume uploading or pasting a module's `.py` file is enough when it needs a Python library the process doesn't already have — say so explicitly: it also needs `requirements.txt` updated and a Docker image rebuild by someone with VPS access (Section 8 of `MODULOS.md`), not just the file itself.
- Never use a blocking `time.sleep()` inside `render()`, and never a `for`/`while` loop with `time.sleep()` between iterations — use a bounded per-rerun step or a gated `run_every` fragment instead.
- Never keep a persistent asyncio event loop or `aiohttp.ClientSession` at module level to reuse across calls — `asyncio.run()` per call is the correct, safe pattern here (Section 8), and a shared one is both the Section 4 anti-pattern and unsafe across sessions' threads.


##############################

# Cómo construir un módulo para OLIMPO

Un módulo es una pestaña de la app (correo temporal, números SMS, o lo
que se te ocurra). Este documento es el contrato exacto que tiene que
cumplir un archivo `.py` para que OLIMPO lo acepte, lo cargue y lo
muestre como pestaña — cómo usar el SDK (`sdk.py`) para cobrar créditos,
guardar datos y hacer llamadas HTTP sin reinventar nada — y, en cada
sección, **por qué** el SDK está armado así y no de otra forma, con la
línea real de `sdk.py` o de un módulo real que lo prueba.

Los dos módulos reales que ya usa OLIMPO (`modules/tempmail.py` y
`modules/smspool.py`) siguen exactamente este contrato — ante la duda,
mirá cómo lo resolvieron ellos. La sección 10, al final, recorre
`smspool.py` completo, función por función, conectando cada pieza con la
sección de este documento que la explica.

---

## 0. Cómo entra tu módulo a la app — la mecánica exacta

Antes de escribir nada, entender esto evita la mitad de las dudas de las
demás secciones: OLIMPO no "importa tu archivo y ya está" — pasa por un
proceso concreto, implementado en `sdk.py`.

### Al arrancar el proceso (una sola vez)

`descubrir_e_instalar()` recorre `modules/*.py` (los internos,
versionados en git). Para cada archivo cuyo nombre (sin `.py`) todavía no
esté en la tabla `sdk_modulos`:

1. Lo importa como módulo real de Python (`importlib.import_module`).
2. Llama a `_validar(mod)`, que revisa que existan `MODULE_ID`,
   `MODULE_NAME` y `render` con `hasattr` — si falta alguno, lanza
   `ModuloInvalido` con el nombre exacto de lo que falta, y el módulo
   **no se registra en absoluto** (no rompe el arranque del resto de la
   app: el `except Exception` alrededor de la importación lo atrapa y
   sigue con el próximo archivo).
3. Si pasó la validación, inserta una fila en `sdk_modulos` (`origen =
   'interno'`, `activo = 1`) y guarda el objeto módulo ya importado en
   `_loaded[module_id]` — un diccionario a nivel de proceso.
4. Llama a tu `on_activar()` si la definiste (dentro de un `try/except`
   propio: si tu `on_activar()` explota, se loguea pero no tumba el
   arranque de OLIMPO).

Los módulos que ya estaban registrados **no se vuelven a tocar** en este
paso — así, si un admin desactivó tu módulo, no reaparece solo activado
en el próximo redeploy.

### Subir un módulo externo desde el panel (`registrar_externo`)

1. `_validar_contenido(contenido)` ejecuta el `.py` crudo (los bytes que
   subiste) dentro de un módulo Python descartable (`types.ModuleType`,
   nunca tocó disco ni `sys.modules` todavía) — solo para poder leer el
   `MODULE_ID` que el archivo declara y confirmar que pasa `_validar()`.
   Si tu archivo tiene un error de sintaxis o le falta algo del contrato,
   esto explota acá y **no se guarda nada en disco** — un módulo inválido
   nunca llega a `external_modules/`.

   **Nota de seguridad, no un bug:** este paso corre el archivo con
   `exec()` de verdad — cualquier código a nivel de módulo del `.py` que
   subiste **se ejecuta en el servidor en ese mismo instante**, incluso
   si la validación falla después y nada queda guardado en disco. No es
   una sandbox. En la práctica esto no es un problema porque el flujo
   solo es alcanzable siendo admin: la pestaña "Admin" ni siquiera
   aparece en la lista de pestañas para quien no lo sea
   (`auth.is_admin(user_id)`, en la función de `app.py` que arma el menú
   de pestañas), y la vía por Telegram (`bot_auth.py::on_document`)
   empieza con el mismo chequeo (`auth.is_admin(update.effective_user.id)`)
   antes de aceptar el archivo. Nunca agregues una vía nueva para subir
   un `.py` que no pase por uno de estos dos chequeos de admin.
2. Recién ahí se escribe `external_modules/<MODULE_ID>.py` — el nombre de
   archivo es *siempre* el `MODULE_ID` que el propio módulo declaró
   adentro, nunca algo que vos elijas aparte. La razón exacta está en el
   docstring de `registrar_externo`: si el nombre de archivo pudiera
   diferir del `MODULE_ID` interno, una llamada a `sdk.module_dir(MODULE_ID)`
   *desde dentro de tu propio módulo* apuntaría a una carpeta de datos
   distinta de la que administra el panel — perderías archivos subidos
   sin ningún error visible en ningún lado. Forzar que sea el mismo string
   de punta a punta elimina esa categoría entera de bug.
3. Antes de importar de verdad, `recargar(module_id)` limpia cualquier
   rastro de una versión anterior del mismo `module_id` que pudiera
   seguir en memoria — saca la entrada de `_loaded` y de `sys.modules`
   (`modules.<id>` y `olimpo_ext_<id>`, sección 8). Esto es lo que hace
   posible **resubir una versión actualizada** de un externo que ya
   existía: sin este paso, Python podría devolver desde `sys.modules` el
   objeto del módulo viejo ya cacheado, en vez de leer los bytes nuevos
   que se acaban de escribir en el paso 2.
4. Se importa de verdad (`_importar_externo`, vía
   `importlib.util.spec_from_file_location` — así puede vivir fuera del
   paquete `modules/` normal de Python) y se valida otra vez.
5. Si algo falla en este segundo paso, se borra el archivo que se acababa
   de escribir (`path.unlink(missing_ok=True)`) — no queda un `.py` roto
   tirado en `external_modules/`.
6. Se registra en `sdk_modulos` con `origen = 'externo'`, se llama
   `on_activar()`, y devuelve el `module_id` con el que quedó.

### En cada rerun de Streamlit (`modulos_activos()`)

Streamlit re-ejecuta `app.py` completo en cada interacción de cada
sesión activa. Sin ningún cuidado, esto significaría reimportar todos los
módulos (y volver a crear tablas, volver a correr `on_activar()`) muchas
veces por minuto. El guard es `_loaded`:

```python
def _cargar(fila) -> object:
    module_id = fila["module_id"]
    if module_id in _loaded:
        return _loaded[module_id]
    ...
```

Un módulo se importa **una sola vez por proceso** — los reruns siguientes
reciben el mismo objeto módulo ya en memoria. `modulos_activos()` recorre
las filas de `sdk_modulos` con `activo = 1`, llama a `_cargar` para cada
una, y si una falla al importar la omite (con `log.exception`) en vez de
tumbar el resto de las pestañas — un módulo roto nunca debe dejar a los
demás sin funcionar.

**Esto tiene una consecuencia directa para vos:** cualquier variable que
declares a nivel de módulo (fuera de cualquier función) se inicializa
**una vez** y después vive en memoria durante toda la vida del proceso,
compartida entre **todas** las sesiones y usuarios que abran tu pestaña.
Ver sección 4-bis para el peligro concreto de esto.

### `render()` corre en CADA rerun, no solo cuando tu pestaña está abierta

Verificado en vivo, no es una suposición: a diferencia de Inicio y Admin
(que en `main()` están condicionados a `if tab.open:`), la rama que
llama a tu módulo no tiene ese chequeo:

```python
elif key.startswith("modulo:"):
    module_id = key.split(":", 1)[1]
    with _api_errors(f"Error en el módulo {nombre_por_modulo_id[module_id]}"):
        mod_por_id[module_id].render(user_id)
```

Esto significa que `render(user_id)` de **todo módulo activo** se
ejecuta en **cada rerun completo de la app, para cada sesión**, sea cual
sea la pestaña que esa persona tenga abierta en ese momento. Confirmado
con un contador real: quedándose en la pestaña "Inicio" y forzando
reruns desde ahí, el `render()` de un módulo sin relación con Inicio se
ejecutó la misma cantidad de veces que los reruns forzados — nunca dejó
de correr por no estar esa pestaña visible.

**La consecuencia práctica:** cualquier trabajo que tu `render()` haga
sin que un botón lo dispare (una consulta a una API, una lectura de
base de datos, un cálculo pesado) corre para **todas** las sesiones que
tengan tu módulo activo, en **cada** interacción de esa sesión con
**cualquier** parte de la app — no solo cuando alguien mira tu pestaña.
`smspool.py::listar_servicios()`/`listar_paises_servicio()` lo resuelven
con el `_cache` de la sección 4-bis (evita pegarle a la API real en cada
uno de esos reruns), pero el propio chequeo de caché y el resto de la
lógica de `render()` hasta ese punto igual se ejecutan siempre. No
asumas que tu módulo "descansa" mientras el usuario está en otra
pestaña — nunca lo hace.

---

## 1. Contrato obligatorio

Tu archivo tiene que definir:

```python
MODULE_ID   = "mimodulo"          # slug único, minúsculas y "_", sin espacios
MODULE_NAME = "🎲 Mi módulo"       # texto de la pestaña — empieza con un emoji

def render(user_id: int) -> None:
    """Dibuja la UI de tu pestaña. Se llama en cada rerun de Streamlit."""
    ...
```

Si falta `MODULE_ID`, `MODULE_NAME` o `render`, el módulo se rechaza —
exactamente por el `hasattr` de `_validar()` descripto arriba. No se
registra, no se activa, no rompe nada del resto de la app.

`MODULE_ID` es además la clave primaria de la tabla `sdk_modulos`, el
prefijo obligatorio de tus `key=` (sección 2), el nombre de tu tabla en
la base compartida (sección 4), la carpeta de tus archivos propios
(`sdk.module_dir`), el sufijo de tu variable de proxy
(`OLIMPO_PROXY_<MODULE_ID>`, sección 6), y — si tu módulo es externo —
el nombre del archivo que lo guarda (`external_modules/<MODULE_ID>.py`,
sección 0). Un solo string amarra seis mecanismos distintos — por eso
tiene que ser estable: cambiarlo después de tener datos reales equivale
a crear un módulo nuevo desde cero.

### Opcionales

```python
MODULE_VERSION    = "1.0.0"   # default "?" si no lo ponés (ver _registrar_fila)
MODULE_AUTHOR     = "Tu nombre"  # default "?"
MODULE_DATA_SCOPE = "per_user"   # "shared" | "per_user" | "own_db" — documentación, ver sección 4
```

Ninguno de los tres se valida ni afecta el comportamiento — `sdk.py` los
lee con `getattr(mod, "...", default)` al registrar la fila. Son
metadata para vos y para quien lea el panel de Admin, no un mecanismo.

```python
def render_admin(user_id: int) -> None:
    """Controles extra que aparecen en Admin > Gestión de módulos, dentro
    de un expander con el nombre de tu módulo. Para configuración global
    (tasas, límites, flags) — no para datos de un usuario puntual."""
    ...

def on_activar() -> None:
    """Se llama una vez cuando el módulo se activa (al instalarse por
    primera vez o al reactivarlo desde el panel). Usalo para crear tus
    propias tablas con CREATE TABLE IF NOT EXISTS — ver sección 4."""
    ...
```

`on_activar()` se llama en tres momentos exactos del código de `sdk.py`,
nunca en ningún otro: dentro de `descubrir_e_instalar()` (arranque, para
módulos internos nuevos), dentro de `activar()` (cuando un admin reactiva
tu módulo desde el panel), y dentro de `registrar_externo()` (justo
después de instalar un externo nuevo). En los tres casos está envuelto en
su propio `try/except` — si tu `on_activar()` explota, no tumba el
llamador.

### Ejemplo mínimo que ya es válido

```python
import streamlit as st

MODULE_ID = "saludo"
MODULE_NAME = "👋 Saludo"

def render(user_id: int) -> None:
    st.subheader(MODULE_NAME)
    st.write(f"Hola, usuario {user_id}")
```

Esto ya es un módulo aceptado: se puede subir tal cual desde Admin >
Gestión de módulos y aparece como pestaña. Pasa `_validar()` porque
`hasattr(mod, "MODULE_ID")`, `hasattr(mod, "MODULE_NAME")` y
`hasattr(mod, "render")` son los tres `True` — nada más se chequea en
ese momento (ni que `render` reciba el parámetro correcto, ni que
`MODULE_ID` sea realmente único entre módulos activos: si dos módulos
declaran el mismo `MODULE_ID`, el segundo en registrarse simplemente
actualiza la fila del primero por el `ON CONFLICT(module_id) DO UPDATE`
de `_registrar_fila` — sé cuidadoso con el nombre que elegís).

**Un detalle no obvio de ese `ON CONFLICT`:** el `DO UPDATE SET` solo
toca `nombre`, `version` y `autor` — **no** toca `origen` ni `activo`
(`sdk.py:400-415`). Si subís un externo con el mismo `MODULE_ID` que un
módulo interno ya registrado, la fila en `sdk_modulos` **sigue diciendo
`origen = 'interno'`** después del conflicto, aunque el código que se
ejecuta a partir de ahí ya es el que acabás de subir (tanto
`descubrir_e_instalar` como `registrar_externo` hacen
`_loaded[module_id] = mod` sin condición, sobrescribiendo siempre el
objeto en memoria). El panel Admin decide qué botones mostrarte leyendo
`m["origen"]` (sección 8) — con la fila todavía marcada "interno" nunca
vas a ver el botón "Eliminar" para ese módulo (solo aparece cuando
`origen == "externo"`), aunque el código real corriendo sea el externo
recién subido. Es una razón más, muy concreta, para no reutilizar un
`MODULE_ID` que ya esté en uso por otro módulo.

### Si partís de `_template.py` o de otro módulo — leé TODO el archivo antes de entregarlo

`modules/_template.py` existe justo para esto: un esqueleto mínimo con
`TODO`s explícitos (URL base, nombre de función, si hace falta guardar
algo en SQLite), pensado para copiarlo a `modules/<nombre>.py` y adaptar
solo lo marcado. No trae nada que puedas olvidarte de revisar — es
deliberadamente chico.

El riesgo real no es ese archivo, es **copiar un módulo real y ya
funcionando** (`smspool.py`, `tempmail.py`, o cualquier otro) como
atajo. `_validar()` solo exige `MODULE_ID`, `MODULE_NAME` y `render`
(sección 0) — un archivo copiado que arrastra diez funciones que tu
módulo nunca llama pasa la validación exactamente igual que uno limpio.
Nada te avisa que sobra código.

**Caso real:** un módulo se armó con ayuda de una IA, usando otro módulo
existente como base — uno cuya API externa solo está disponible en
ciertos horarios, y que por eso tenía una función de chequeo de
disponibilidad (al estilo `_uptime_service()`) que decide en silencio si
seguir o no antes de intentar la acción principal. El módulo nuevo
apuntaba a una API sin esa restricción de horario — no la necesitaba
para nada — pero la función de chequeo quedó copiada igual, sin que
nadie la hubiera pedido. El síntoma no fue una excepción ni un error en
el log: el módulo simplemente **dejó de intentar** su acción principal
en silencio, condicionado por un chequeo de horario que no tenía
ninguna razón de estar ahí. Es el tipo de falla más difícil de
diagnosticar que existe — no rompe nada, no loguea nada, solo no hace lo
que tiene que hacer.

La lección generaliza más allá de este caso puntual: **cualquier función
que pueda decidir, por su cuenta, no ejecutar la acción principal del
módulo** (un chequeo de horario, un flag de feature, un límite, un
"todavía no" silencioso) tiene que ser una decisión consciente de *tu*
módulo, nunca un resabio de haber copiado otro. Si la heredaste sin
saber bien por qué está:

- Si tu módulo la necesita de verdad: dejala, pero agregale un comentario
  que explique la condición real (qué la dispara, contra qué la
  compara) — no el comentario del módulo original, uno que describa tu
  caso.
- Si no la necesita: **borrala**. No la dejes "por si acaso" — código
  que no se usa pero podría ejecutarse condicionalmente es exactamente
  el tipo de cosa que un día se activa sin que nadie lo haya tocado.
- Si no estás seguro de cuál es cuál: antes de entregar el módulo, leé
  cada función del archivo y preguntate "¿mi `render()` llega hasta acá
  alguna vez, y si llega, la condición que chequea es sobre *mi* API o
  sobre la del módulo del que copié?". Cualquier función que no pase esa
  pregunta se borra.

Esto vale tanto si estás copiando a mano como si le pediste a una IA que
armara el módulo usando otro como referencia — pedirle que "se base en
`smspool.py`" sin pedirle además que audite y borre lo que no aplica es
exactamente cómo se cuela este tipo de bug.

---

## 2. Botones, formularios y estado

Streamlit comparte `st.session_state` entre **todas** las pestañas del
mismo usuario. Si dos módulos usan la misma `key` en un widget, o la
misma clave de `session_state`, se pisan entre sí y aparecen errores
raros de "widget duplicado".

Regla: **toda key lleva el prefijo de tu `MODULE_ID`.**

```python
if st.button("Comprar", key=f"{MODULE_ID}_comprar"):
    ...

st.session_state[f"{MODULE_ID}_pedido"] = {...}
```

Así se ve en el módulo real: `smspool.py` guarda el pedido activo en
`st.session_state[f"{MODULE_ID}_order"]` (una única clave, un diccionario
con todo el estado del pedido adentro — número, servicio, país, créditos
cobrados, fecha de expiración, y hasta una bandera `sonido_pendiente`,
ver sección 7) y cada botón lleva su propia key (`f"{MODULE_ID}_comprar"`,
`f"{MODULE_ID}_revisar"`, `f"{MODULE_ID}_cancelar"`, `f"{MODULE_ID}_nuevo"`).
Ninguna de esas cuatro keys puede chocar con otro módulo porque las
cuatro arrancan con `"smspool_"`. El resto de los widgets del archivo
sigue la misma regla, aunque el ejemplo de arriba solo nombra los cuatro
botones del flujo de compra: los dos `st.selectbox` de servicio y país
usan `f"{MODULE_ID}_servicio"` y `f"{MODULE_ID}_pais"`, y los dos widgets
de `render_admin()` usan `f"{MODULE_ID}_admin_tasa"` y
`f"{MODULE_ID}_admin_guardar_tasa"` — ocho keys en total en el archivo,
todas con el mismo prefijo.

Para mostrar errores de red sin tumbar la pestaña, envolvé la llamada
externa con el helper del SDK:

```python
import sdk

with sdk.api_errors("No se pudo cargar la lista"):
    datos = mi_funcion_que_llama_a_una_api()
```

`api_errors` es un `@contextmanager` de once líneas
(`sdk.py:67-77`): si el bloque `yield` lanza cualquier excepción, la
loguea (`log.exception`, con el traceback completo en el log del
servidor) y muestra `st.error(f"{mensaje}. Intenta de nuevo en un
momento.")` en la UI — pero **no vuelve a lanzar la excepción**. Por eso
el resto de tu `render()` después del `with` sigue ejecutándose
normalmente en ese mismo rerun (a menos que vos mismo hagas `return`
adentro del `with`, como hace `smspool.py` en varios lugares cuando el
error es fatal para esa pantalla en particular).

---

## 2-bis. Resultados para copiar — siempre en monospace

**Sí, ya está detallado** — es un patrón que ya usan los dos módulos
reales, esta sección simplemente le pone nombre y regla explícita a lo
que ya hacen:

- `tempmail.py::render()` — la dirección de correo
  (`st.code(row["email"], language=None)`, línea 254) y cada campo de la
  identidad falsa (`st.code(valor, language=None)`, línea 298).
- `smspool.py::render()` — el número asignado
  (`st.code(order["number"], language=None)`, línea 423) y el código SMS
  recibido (`st.code(order["sms"], language=None)`, línea 434).

**Regla: cualquier resultado que el usuario vaya a copiar y pegar en otro
lado** — una dirección de correo, un número de teléfono, un código de
verificación, un ticket/ID de pedido, una contraseña generada, una URL —
se muestra con:

```python
st.code(valor, language=None)
```

nunca con `st.write(valor)` ni `st.text(valor)`. La razón es doble:

1. **Fuente monospace** — un `0` no se confunde con una `O`, ni una `1`
   con una `l`. En un código de verificación de 6 caracteres o un número
   de teléfono, un solo carácter mal copiado a mano vuelve el dato
   inútil.
2. **Botón de copiar incorporado** — Streamlit dibuja automáticamente un
   ícono de copiar al portapapeles sobre cualquier bloque `st.code(...)`,
   sin que tengas que armar vos mismo ningún mecanismo de copiado.

`language=None` es intencional en los dos módulos reales: sin eso,
`st.code` intenta resaltar sintaxis como si fuera código de programación
(coloreando palabras clave, comillas, etc.) — para un email o un número
de teléfono eso no aporta nada y puede verse raro. Usalo siempre que el
contenido no sea código de verdad.

Para texto más largo que no hace falta copiar carácter por carácter (el
cuerpo de un correo, una descripción, un historial), `st.write` o
`st.text` siguen siendo la opción correcta — la regla de `st.code` es
específica para datos que el usuario necesita copiar exactos, no para
todo el contenido de tu pestaña.

---

## 2-ter. Pausas, `time.sleep()` y reruns — prohibido bloquear el proceso

**Regla sin excepción para módulos: `time.sleep()` bloqueante dentro de
`render()` está prohibido.** No es una recomendación ni un "mejor
evitarlo" — está prohibido, punto. Más abajo hay tres patrones
concretos que cubren cualquier necesidad real de "esperar algo" sin
usar `time.sleep()`.

### Por qué un `time.sleep()` en `render()` es distinto de una pestaña lenta

Streamlit corre el script de cada sesión en su propio hilo, pero ese hilo
es **sincrónico de punta a punta**: mientras `render()` no termine, ese
hilo no puede aceptar ninguna interacción nueva ni mandar ninguna
actualización a la UI de esa sesión. Si tu módulo llama
`time.sleep(5)` dentro de `render()` (directo o adentro de una función
que vos llamás desde ahí), esos 5 segundos el hilo de esa sesión está
completamente ocupado sin hacer nada útil — para quien está mirando esa
pestaña, la app se ve congelada hasta que el sleep termina.

Esto es un problema distinto del leak de memoria de la sección 4-bis
—no es una fuga, es un **hilo ocupado sin trabajo real**— pero puede ser
igual de grave bajo uso real: Streamlit tiene un límite de ejecuciones de
script concurrentes por proceso. Si varias sesiones disparan al mismo
tiempo un flujo con `time.sleep()` largo (por ejemplo, crear varias
cuentas en un loop con pausas entre cada una), esas sesiones ocupan hilos
sin liberar nada, y el resto de los usuarios —en cualquier pestaña,
incluida gente que no tiene nada que ver con tu módulo— puede empezar a
notar la app lenta o directamente sin responder.

**El caso límite, mucho peor que un sleep de unos segundos:** un `while
True` con `time.sleep()` adentro de `render()` (por ejemplo, para
"esperar a que algo esté listo") **nunca devuelve el control a
Streamlit**. No son 5 segundos de bloqueo, es ese hilo perdido para
siempre — indistinguible de un cuelgue real del proceso. Ni siquiera el
`with sdk.api_errors(...)` (sección 2) o el `with _api_errors(...)` con
que `app.py` ya envuelve la llamada a tu `render()` (`app.py:149-155`,
la misma forma que `sdk.api_errors` pero definida aparte, ver más abajo)
te salvan de esto — ninguno de los dos puede interrumpir un bucle que
nunca termina ni lanza una excepción. **Nunca un `while True` con sleep
dentro de `render()`.**

### Qué hacer en cada caso real

**a) Necesitás espaciar varias llamadas seguidas a una API** (por
ejemplo, crear N cuentas respetando un límite de una cada X segundos).
Nunca hagas esto:

```python
# MAL: bloquea el hilo de esa sesión durante N * X segundos de una sola vez
for i in range(n):
    crear_cuenta(i)
    time.sleep(X)
```

En vez de eso, hacé **un paso por rerun**, guardando el progreso en
`st.session_state` (una lista/contador acotado a `n`, nunca algo sin
límite — mismo criterio de la sección 4-bis) y dejando que el próximo
paso se dispare con la siguiente interacción o con un `st.rerun()`
después de cada paso:

```python
estado_key = f"{MODULE_ID}_progreso"
progreso = st.session_state.setdefault(estado_key, {"hechas": 0, "total": n})

if progreso["hechas"] < progreso["total"]:
    if st.button("Crear siguiente cuenta", key=f"{MODULE_ID}_siguiente"):
        with sdk.api_errors("No se pudo crear la cuenta"):
            crear_cuenta(progreso["hechas"])
            progreso["hechas"] += 1
            st.session_state[estado_key] = progreso
            st.rerun()
    st.caption(f"{progreso['hechas']} de {progreso['total']}")
else:
    st.success("Listo.")
```

El propio tiempo de red de cada request ya suele alcanzar como
espaciado natural entre llamadas; si de verdad necesitás una pausa fija
entre pasos automáticos (no disparados por botón), usá un
`@st.fragment(run_every="Xs")` — no un sleep — con el mismo gate de
`tab.open` y chequeo de `session_expires_at` que ya usan
`_anuncios_fragment` y `_logs_fragment` (sección 7 y `app.py`), para que
el paso a paso se detenga solo si nadie está mirando esa pestaña.

**b) Necesitás esperar a que un resultado externo esté listo**
(un código SMS, una verificación). Es exactamente el patrón que ya
documenta la sección 7 vía `smspool.py`: un botón "Revisar" que el
usuario dispara a demanda (`check_sms()`), nunca un sleep-poll dentro de
un solo `render()`. Si el chequeo tiene que repetirse solo, sin que el
usuario apriete nada, un `run_every` con los mismos gates de la sección
7 — nunca un bucle con `time.sleep()`.

**c) `app.py::_login_screen` usa `time.sleep(2)` seguido de `st.rerun()`
mientras espera la confirmación de Telegram — esto es exclusivo del
núcleo de OLIMPO, no un patrón que tu módulo pueda replicar.** Se
menciona acá únicamente para que no lo tomes como precedente: es código
de `app.py`, no de un módulo, y la prohibición de arriba aplica sin
excepción a todo lo que esté dentro de `render()`/`render_admin()`. Si
tu módulo necesita esperar algo puntual de esa misma sesión, usá (a) o
(b) — nunca un `time.sleep()`, ni siquiera uno corto.

### La diferencia entre `sdk.api_errors` y el `_api_errors` de `app.py`

Mencionado arriba, vale la pena que quede explícito: `app.py` ya envuelve
la llamada completa a tu `render()` con su **propio** `_api_errors`
(`app.py:149-155` — misma forma que `sdk.api_errors`, definido aparte,
no es el mismo objeto) —

```python
with _api_errors(f"Error en el módulo {nombre_por_modulo_id[module_id]}"):
    mod_por_id[module_id].render(user_id)
```

— así que una excepción no atrapada en ningún lado de tu módulo no tumba
el resto de la app: para ahí, y el usuario ve un error genérico en esa
pestaña. Pero esto es una red de seguridad a nivel de "toda la función
`render()`", no un reemplazo de `sdk.api_errors` dentro de tu propio
código: sin tu propio `with sdk.api_errors(...)` alrededor de cada
llamada externa puntual, un error en una parte de tu pantalla corta la
ejecución de **todo lo que venía después** en ese `render()` para ese
rerun (el resto de tu UI de esa pestaña, en ese ciclo, no llega a
dibujarse) — en vez de solo la sección que efectivamente falló. Seguí
usando `sdk.api_errors` como documenta la sección 2; esta red de `app.py`
es para lo que se te escape, no el mecanismo principal.

---

## 3. UI de paneles — qué podés y qué no podés tocar

- **Tu pestaña es 100% tuya.** Adentro de `render()` podés usar
  cualquier widget de Streamlit: botones, expanders, columnas,
  `st.file_uploader`, lo que necesites — con una excepción real y
  importante: **nunca `st.tabs()`**, ver la subsección de abajo.
- **Admin es compartido.** No podés escribir directamente en la
  pestaña Admin. El único punto de extensión es `render_admin()`, que
  se muestra dentro de un `st.expander` propio — título exacto
  `f"Configuración de {nombre_del_módulo}"`
  (`app.py::_modulos_admin_screen`) —, en la sección "Gestión de
  módulos" del panel Admin — no se mezcla con los controles de otros
  módulos ni con los del núcleo (usuarios, carrusel). `app.py` busca tu
  `render_admin` con `getattr(mod, "render_admin", None)` sobre el
  objeto módulo ya cargado — si tu módulo está desactivado no hay objeto
  cargado y el expander ni siquiera aparece, aunque hayas definido
  `render_admin`. El ejemplo real: `smspool.py::render_admin()` solo
  expone un `st.text_input` para la tasa USD→MXN y un botón para
  guardarla — nada de la UI de otros módulos aparece ahí ni la tuya
  aparece en la de ellos.
- **Inicio no se puede modificar** desde un módulo — es la pantalla de
  bienvenida del núcleo de OLIMPO.
- **No accedas a tablas de otro módulo.** Si tu módulo necesita saber
  el saldo de un usuario, usá `sdk.balance(user_id)` — nunca leas la
  tabla `creditos` a mano. Lo mismo para cualquier dato que no sea tuyo.
  Técnicamente nada te lo impide a nivel de SQLite (para los patrones
  (a) y (b) de la sección 4, todos los módulos comparten el mismo
  archivo `olimpo.db` — los patrones (c), (d) y (e) sí usan archivos
  separados) — es una regla de diseño, no una restricción de permisos.
  Rompela y el día que `creditos.py` cambie de forma internamente, tu
  módulo se rompe sin aviso.

### Nunca uses `st.tabs()` dentro de tu módulo — rompe la navegación de toda la app

Streamlit no tiene un modo "barra de navegación abajo" nativo. OLIMPO lo
simula con CSS puro, inyectado una sola vez en `app.py` (líneas 51-121):
reposiciona el `tablist` real que arma `st.tabs()` — seleccionado por
`div[data-testid="stTabs"] div[role="tablist"]` — como una barra fija al
pie de la pantalla, con `position: fixed; bottom: 0`.

Ese selector **no distingue el tablist de más afuera** (Inicio / tu
módulo / Anuncios / Admin) **de cualquier otro `st.tabs()` que exista en
la página** — incluido uno que vos mismo llames adentro de tu propio
`render()`. Si tu módulo hace algo como:

```python
tab_a, tab_b = st.tabs(["Bandeja", "Identidad"])
```

ese segundo tablist **también** recibe `position: fixed; bottom: 0` — y
al pintarse después del de más afuera, lo tapa por completo. El usuario
pierde acceso a Inicio, Admin, y a cualquier otro módulo hasta que
recargue la página entera a mano — exactamente el "no poder salir ni
moverse entre módulos" que hay que evitar.

**Esto no es hipotético — es un bug real que existe hoy en
`modules/tempmail.py`, confirmado en vivo con capturas de pantalla antes
de escribir esta sección.** Su pestaña "Correo temporal" arma un
`st.tabs(["Bandeja", "Identidad"])` propio para alternar entre la
bandeja de entrada y la identidad falsa — apenas alguien crea una cuenta
y ve esa pantalla, la barra de navegación real de toda la app
desaparece, reemplazada por ese selector interno. Queda documentado acá
para que se corrija ahí también, y para que ningún módulo nuevo repita
el mismo error copiándolo de uno de los módulos de referencia.

**Qué usar en su lugar** para cualquier selector de sub-vistas dentro de
tu propia pantalla — probado en vivo, no deja ningún rastro en el
`tablist` global:

```python
vista = st.segmented_control(
    "vista", ["Bandeja", "Identidad"], default="Bandeja",
    key=f"{MODULE_ID}_vista", label_visibility="collapsed",
)
if vista == "Bandeja":
    ...
else:
    ...
```

`st.segmented_control` (o `st.pills`, o directamente `st.radio(...,
horizontal=True)` si tu versión de Streamlit no trae las dos primeras)
se ve igual de bien como selector de sub-vistas, pero no usa
`data-testid="stTabs"` — no colisiona con el CSS de navegación de OLIMPO
sea cual sea la profundidad a la que lo llames dentro de tu `render()`.

### Tampoco uses `st.sidebar` — tapa la navegación igual que `st.tabs()`

Mismo problema, otro widget. Probado en vivo: si tu módulo abre
`with st.sidebar: ...`, el panel lateral de Streamlit ocupa **toda la
altura de la pantalla**, de arriba abajo — incluida la franja de abajo
donde vive la barra de navegación de OLIMPO. Con el sidebar expandido,
"Inicio", tu propia pestaña, y el resto quedan completamente tapados
detrás del panel; solo se ve lo que el sidebar decide mostrar. Confirmado
con captura de pantalla antes de escribir esto, igual que el caso de
`st.tabs()` — no es una suposición.

**Prohibido usar `st.sidebar` dentro de un módulo, sin excepción.**
Cualquier control que hoy pondrías en un sidebar (filtros, configuración
secundaria, navegación auxiliar) va dentro del cuerpo normal de tu
`render()` — en un `st.expander`, en columnas, o en la pantalla
principal directamente.

**Lo que sí probamos y no rompe nada:** `st.dialog` (un modal). Se
superpone al contenido mientras está abierto, tal como se espera de un
modal, y la barra de navegación real queda visible e intacta detrás —
confirmado también con captura. Es la herramienta correcta si tu módulo
necesita algo tipo "confirmar esta acción" sin usar una pestaña ni un
sidebar propios.

---

## 4. Datos — los patrones de persistencia

**Prohibido tratar `st.session_state` (o cualquier variable a nivel de
módulo, sección 4-bis) como si fuera persistencia.** No lo es, bajo
ninguna circunstancia: `st.session_state` está atado a una sesión de
navegador puntual — desaparece cuando esa sesión expira
(`SESSION_TTL_SECONDS`), cuando el usuario cierra la pestaña, o cuando
el proceso se reinicia (deploy, crash, lo que sea). Nunca es el lugar
para nada que el usuario espere encontrar la próxima vez que entre a
OLIMPO. Todo dato que tenga que sobrevivir a eso —una cuenta creada, un
pedido, una preferencia guardada— pasa obligatoriamente por uno de los
cinco patrones de esta sección, nunca por `session_state` solo. Usá
`session_state` únicamente para estado de UI de la sesión actual (qué
sub-vista está seleccionada, un formulario a medio completar, una
bandera de "ya sonó" de la sección 7) — nunca como sustituto de guardar
algo de verdad.

Todo pasa por `sdk.py`, nunca importes `db.py` directamente desde un
módulo nuevo (los módulos internos históricos lo hacen porque son
anteriores al SDK, pero el patrón recomendado de acá en adelante es
`sdk.db_conn()`).

`MODULE_DATA_SCOPE` (sección 1) documenta cuál de estos cuatro patrones
usa tu módulo — es solo para que quien lea el archivo sepa qué esperar
sin tener que leer todo `render()`; no cambia nada del comportamiento.

### a) Config compartida (igual para todos los usuarios)

Tasas, límites, flags de encendido/apagado — datos generales que no
son de un usuario en particular:

```python
tasa = sdk.get_config(MODULE_ID, "tasa_cambio", default="18.5")
sdk.set_config(MODULE_ID, "tasa_cambio", "19.2")
```

Por dentro es una tabla única `sdk_modulo_config` con clave primaria
compuesta `(module_id, key)` — tu módulo nunca choca con la config de
otro aunque uses el mismo nombre de `key`, porque `module_id` ya te aisló.
Guardalo/editalo típicamente desde `render_admin()` — es exactamente lo
que hace `smspool.py::render_admin()` con `usd_to_mxn` (aunque ese
módulo, por ser anterior al SDK, escribe la tabla `smspool_config` propia
en vez de `sdk.set_config` — mismo patrón, implementación previa al
helper genérico).

### b) Filas por usuario en la base compartida (el patrón más común)

Cuando cada usuario tiene algunas filas — pedidos, cuentas, historial
— pero no hace falta un archivo aparte. Creá tu propia tabla (prefijada
con tu `MODULE_ID`) en `on_activar()`:

```python
def on_activar() -> None:
    with sdk.db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mimodulo_pedidos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                detalle    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def guardar_pedido(user_id: int, detalle: str) -> None:
    with sdk.db_conn() as conn:
        conn.execute(
            "INSERT INTO mimodulo_pedidos (user_id, detalle, created_at) VALUES (?, ?, datetime('now'))",
            (user_id, detalle),
        )
```

Así trabajan `tempmail_cuentas` (`user_id INTEGER PRIMARY KEY` en el
schema — unicidad real, exigida por SQLite, no una convención de
aplicación) y `olimpo_sms_orders` (muchas filas por usuario a lo largo
del tiempo, un pedido por compra, sin restricción de unicidad sobre
`user_id`). Sobre `tempmail_cuentas`: la razón de que `tempmail.py`
además chequee `_cuenta_row(user_id)` **antes** de intentar crear una
cuenta nueva no es evitar el error de SQLite por violar la clave
primaria — es evitar crear una segunda cuenta en mail.tm (el proveedor
externo) que quedaría huérfana y sin forma de borrarla, porque el schema
solo tiene lugar para guardar una por `user_id` (comentario real de
`crear_cuenta()`, `tempmail.py:80-82`). La clave primaria en SQLite es la
red de seguridad si ese chequeo tuviera un bug; el chequeo en sí es la
defensa real, pensada para el proveedor externo, no para la base local.
`sdk.db_conn()` es literalmente un alias de `get_conn()` de `db.py` — WAL
mode y `busy_timeout` ya resueltos, no tenés que pensar en eso.

### c) Base de datos propia por usuario (aislamiento total)

Para cuando un usuario acumula un dataset propio y pesado que no tiene
sentido mezclar en filas de una tabla compartida (por ejemplo, un
inventario, notas largas, un historial que cada uno administra a su
manera). El SDK te da un archivo SQLite exclusivo por usuario:

```python
with sdk.user_db(MODULE_ID, user_id) as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS notas (id INTEGER PRIMARY KEY, texto TEXT)")
    conn.execute("INSERT INTO notas (texto) VALUES (?)", (texto,))
```

Esto vive en `data/modulos/<MODULE_ID>/usuarios/<user_id>.db`
(`sdk.py:217-219`, la carpeta se crea con `mkdir(parents=True,
exist_ok=True)` si no existe), fuera de git y fuera de la base
compartida — cada usuario es completamente independiente. Ningún módulo
existente hoy usa este patrón (ni `tempmail.py` ni `smspool.py`) — es
una capacidad del SDK reservada para el caso en que de verdad haga
falta ese aislamiento total. Para la mayoría de los casos alcanza con
el patrón (b).

### d) Datos de referencia propios del módulo (solo lectura)

Para cuando tu módulo necesita **consultar** una base de datos que ya
existe — un catálogo, una tabla de precios, un dataset que armaste
aparte — pero no crearla ni escribirla desde OLIMPO. `sdk.module_dir`
te da una carpeta propia del módulo para este tipo de archivo:

```python
ruta = sdk.module_dir(MODULE_ID) / "catalogo.db"

with sdk.abrir_solo_lectura(ruta) as conn:
    filas = conn.execute("SELECT * FROM productos WHERE categoria = ?", (cat,)).fetchall()
```

`abrir_solo_lectura` conecta con `sqlite3.connect(f"file:{ruta}?mode=ro",
uri=True)` — el modo `ro` de SQLite hace que cualquier `INSERT`/`UPDATE`/
`DELETE` falle a nivel del propio motor de la base, no es una convención
que tu código tenga que respetar por las buenas. El archivo se sube y se
administra (listar, subir, borrar) desde **Admin > Gestión de módulos**,
en el expander "Datos de \<tu módulo\>" de la tarjeta de tu módulo — vive
en `data/modulos/<MODULE_ID>/datos/`, fuera de git.

### e) Bases de datos compartidas subidas por un admin

Para datos que no son de un módulo en particular — por ejemplo, una
base de "usuarios activos" traída de otro sistema, que varios módulos
(o el propio núcleo) necesitan consultar. Un admin la sube una sola vez
desde **Admin > Bases de datos compartidas**, y cualquier módulo puede
leerla:

```python
with sdk.bd_compartida("usuarios_activos.db") as conn:
    activos = conn.execute("SELECT * FROM usuarios WHERE activo = 1").fetchall()

sdk.listar_bd_compartidas()  # ["usuarios_activos.db", ...]
```

`registrar_bd_compartida` valida que el archivo subido sea un SQLite real
antes de aceptarlo (`conn.execute("SELECT name FROM sqlite_master LIMIT
1")` dentro de un `try`; si falla, borra el archivo que acababa de
escribir y lanza `ValueError`) — un `.db` corrupto o que en realidad es
otro tipo de archivo nunca queda instalado. También es de solo lectura —
para actualizarla, un admin la vuelve a subir desde el panel. Vive en
`data/compartidas/`, fuera de git.

### Prioridad de búsqueda: BD compartida antes que tu propio archivo

Cuando un dataset **podría** vivir en dos lugares — una base compartida
que un admin ya subió (patrón e) o un archivo de referencia que tu propio
módulo trae consigo (patrón d) — la prioridad es siempre la compartida
primero, con tu archivo propio como respaldo si no la encuentra ahí.

La razón: una base compartida la puede actualizar un admin en cualquier
momento sin tocar código ni redeploy (solo resubiéndola desde el panel);
tu archivo propio normalmente queda fijo salvo que vos mismo lo
actualices a mano en Admin > Gestión de módulos. Preferir la compartida
cuando existe evita que tu módulo siga sirviendo datos viejos mientras el
admin ya cree haber actualizado la fuente real.

Patrón concreto:

```python
NOMBRE_BD = "catalogo_precios.db"

def _consultar_catalogo(sku: str) -> dict | None:
    if NOMBRE_BD in sdk.listar_bd_compartidas():
        # 1) Preferí la compartida: la administra un admin, sin tocar código.
        with sdk.bd_compartida(NOMBRE_BD) as conn:
            row = conn.execute(
                "SELECT * FROM productos WHERE sku = ?", (sku,)
            ).fetchone()
            if row is not None:
                return dict(row)

    # 2) No está en la compartida (o no tenía ese sku): caé al archivo
    #    propio del módulo, si existe.
    ruta = sdk.module_dir(MODULE_ID) / NOMBRE_BD
    if ruta.exists():
        with sdk.abrir_solo_lectura(ruta) as conn:
            row = conn.execute(
                "SELECT * FROM productos WHERE sku = ?", (sku,)
            ).fetchone()
            if row is not None:
                return dict(row)

    return None
```

Notas sobre esta implementación:

- `sdk.listar_bd_compartidas()` devuelve solo nombres de archivo
  (`sdk.py:281-283`, un `sorted(...)` sobre `SHARED_DB_DIR.glob("*.db")`)
  — chequear `NOMBRE_BD in [...]` antes de abrir evita que
  `sdk.bd_compartida` explote: no tiene guarda propia contra archivo
  faltante, hereda el `FileNotFoundError` explícito de
  `abrir_solo_lectura` (sección 4d).
- El fallback chequea `ruta.exists()` por la misma razón —
  `sdk.module_dir(...)` siempre devuelve la carpeta (la crea si hace
  falta, `sdk.py:251-253`), pero no garantiza que el archivo específico
  que buscás esté adentro.
- Si ninguna de las dos fuentes tiene el dato, la función devuelve
  `None` — es responsabilidad de tu `render()` decidir qué mostrar en
  ese caso (`st.info("Todavía no hay datos para esto")`, típicamente),
  nunca asumir en silencio que algo va a aparecer.
- Ninguno de los dos módulos reales (`tempmail.py`, `smspool.py`) usa
  hoy datos de referencia propios ni bases compartidas — este patrón
  combina los dos mecanismos del SDK (4d y 4e) sin un ejemplo real
  todavía en el repo. Si construís un módulo que lo use de verdad, sería
  el candidato natural para sumarse a la sección 10 como referencia.

---

## 4-bis. Estado a nivel de módulo — la trampa del caché sin límite

Volviendo a la sección 0: tu archivo se importa **una sola vez por
proceso**, y cualquier variable declarada fuera de una función vive en
memoria durante toda la vida de ese proceso — compartida entre **todos**
los usuarios y **todos** los reruns.

Esto es exactamente lo que hace `modules/smspool.py` en su línea 24:

```python
# Cache en memoria: {"servicios" | "paises_<service_id>": (timestamp, lista)}
_cache: dict = {}
```

Con `_cached()`/`_cache[key] = (time.time(), datos)` alrededor
(`smspool.py:44-48, 92-98, 120-154`). La intención es razonable — evitar
pegarle a la API de SMSPool en cada rerun con un TTL de 6 horas
(`CACHE_TTL_SECONDS`). El problema: **las entradas viejas nunca se
borran**, solo se sobrescriben si alguien vuelve a pedir la misma clave
dentro de las 6 horas. Si en 6 horas se consultan 200 `service_id`
distintos, quedan 200 entradas en memoria para siempre — nada las purga
ni siquiera cuando vencen. En un proceso de Streamlit que corre
semanas sin reiniciarse, cualquier caché con esta forma (dict a nivel de
módulo, escritura sin límite de entradas, sin purga por TTL vencido) es
candidato directo a memory leak — es, de hecho, el sospechoso principal
identificado en la investigación de fuga de memoria de OLIMPO
documentada en `CLAUDE.md` (todavía sin confirmar con medición directa
del heap, pero descartado casi todo lo demás por lectura de código).

**Qué hacer en un módulo nuevo, en orden de preferencia:**

1. **No cachear en memoria de proceso si podés cachear en la base**
   (patrón (a) o (b) de la sección 4, con una columna de timestamp — leer
   y comparar contra la hora actual antes de decidir si hace falta
   refrescar). Sobrevive un reinicio del proceso, y purgar filas viejas
   es una consulta SQL, no un mecanismo nuevo.
2. **Si de verdad necesitás algo en memoria** (por ejemplo, por latencia:
   ni siquiera una consulta a SQLite local es aceptable para tu caso),
   usá una estructura con límite de tamaño real, no un `dict` que crece
   sin techo — por ejemplo `functools.lru_cache(maxsize=...)` en una
   función pura, que sí tiene un límite duro de entradas y descarta las
   más viejas cuando lo alcanza.
3. **Nunca** repliques el patrón de `_cache: dict = {}` sin `maxsize` ni
   purga — aunque hoy funcione, es la clase exacta de bug que ya le costó
   días de diagnóstico a OLIMPO.

---

## 5. Créditos — cobrar y reembolsar

Nunca importes `creditos.py` directamente. El SDK expone exactamente
lo que necesitás — y son wrappers de una línea sobre las funciones reales
de `creditos.py` (`sdk.py:53-64`):

```python
sdk.balance(user_id) -> int        # creditos.saldo(user_id)
sdk.charge(user_id, amount, reason) -> bool   # creditos.descontar(...) — False si no alcanza
sdk.refund(user_id, amount, reason) -> None   # creditos.asignar(...) — no-op si amount <= 0
```

**Patrón recomendado: cobrar antes de la operación externa, reembolsar
si falla.** Así nunca queda un usuario cobrado sin haber recibido nada:

```python
if not sdk.charge(user_id, costo, f"Compra en {MODULE_NAME}"):
    st.error("No tienes créditos suficientes.")
    return

try:
    resultado = llamar_api_externa()
except Exception as exc:
    sdk.refund(user_id, costo, f"Reembolso — error: {exc}")
    st.error(f"Falló la compra, créditos devueltos. ({exc})")
    return

# éxito: guardar resultado, mostrar al usuario, etc.
```

`modules/smspool.py::render()` implementa este patrón completo, y
además otros **dos caminos de reembolso** que el ejemplo de arriba no
cubre — la sección 10 los recorre en detalle:

- El pedido expira sin que llegue ningún código (`esta_expirado()` +
  `check_sms()` final antes de rendirse) → se marca `failed` y se
  reembolsa automáticamente, **sin que el usuario haga nada**.
- El usuario cancela manualmente dentro de la ventana de 10 segundos
  (`CANCEL_WINDOW_SECONDS`) → se reembolsa y el texto de
  `sdk.alertar(...)` deja aclarado que fue cancelación manual, no un
  error del sistema — pero es una aclaración que queda en el canal de
  auditoría/admins, **no** una que reciba el propio usuario: este camino
  en particular no manda ningún `sdk.enviar_telegram` ni ningún
  `st.success`/`st.info` en pantalla (a diferencia de los otros dos
  caminos de reembolso). Es una asimetría real del módulo de referencia,
  no necesariamente algo a copiar sin pensarlo — ver la sección 10 para
  el detalle exacto de los tres caminos.

Los tres caminos (fallo de API, expiración, cancelación) terminan en
`sdk.refund(...)` seguido de `sdk.alertar(...)` — nunca uno sin el otro.

---

## 6. Proxies

Si tu módulo llama a una API externa que necesita pasar por un proxy
(geo-restricciones, IP fija, etc.), usá los helpers HTTP del SDK en vez
de `requests`/`aiohttp` directo:

```python
resp = sdk.http_get(MODULE_ID, "https://api.ejemplo.com/algo")
resp = sdk.http_post(MODULE_ID, "https://api.ejemplo.com/algo", json={"x": 1})
```

El proxy se resuelve así (`sdk.py:345-347`, `_proxies()`):

```python
proxy = os.getenv(f"OLIMPO_PROXY_{module_id.upper()}") or os.getenv("OLIMPO_PROXY")
```

Primero busca `OLIMPO_PROXY_<MODULE_ID EN MAYÚSCULAS>` (específico de tu
módulo); si no está seteada, cae a `OLIMPO_PROXY` (genérico, compartido
por cualquier módulo que no tenga la suya propia). Si ninguna de las dos
existe, `_proxies()` devuelve `None` y `requests` simplemente no usa
proxy — no hace falta que decidas vos si hay proxy configurado o no, el
helper ya resuelve ese `if`.

Si tu módulo ya usa `aiohttp` directamente (como `tempmail.py` y
`smspool.py`, que son anteriores a este helper), podés seguir así,
pero entonces el manejo de proxy corre por tu cuenta (leer la env var
vos mismo y pasarla a la sesión de `aiohttp`) — ninguno de los dos
módulos reales usa proxy hoy, así que no hay un ejemplo real de eso
todavía.

### `asyncio.run()` dentro de Streamlit — por qué es seguro, aunque Streamlit ya sea async

`tempmail.py`, `smspool.py` y `modules/_template.py` comparten el mismo
puente entre async y sync:

```python
def _run(coro):
    return asyncio.run(coro)

async def _mi_funcion(user_id: int, algo: str) -> dict:
    ...

def mi_funcion(user_id: int, algo: str) -> dict:
    return _run(_mi_funcion(user_id, algo))
```

Es razonable preguntarse si esto es seguro: Streamlit corre su propio
servidor (Uvicorn) sobre un event loop de `asyncio` — ¿no debería
`asyncio.run()`, llamado desde adentro de tu módulo, chocar con un loop
que ya está corriendo? La respuesta corta es que no, y la razón es
concreta, no una suposición: **el servidor y el script de cada sesión
corren en hilos distintos.**

Verificado directo en el código fuente de Streamlit
(`streamlit/runtime/scriptrunner/script_runner.py`, comentario
"Note [Threading]"): el hilo principal levanta el servidor Uvicorn (ahí
sí vive un event loop de verdad, corriendo todo el tiempo); cada sesión
tiene su **propio hilo dedicado** (`ScriptRunner.scriptThread`), creado
al conectarse, donde corre el script completo — `app.py`, `main()`, y
`render()`/`render_admin()` de cada módulo activo. `asyncio.run()`
llamado desde ese hilo no encuentra ningún loop corriendo ahí (los loops
de asyncio son por hilo, no globales al proceso) — crea uno nuevo, corre
el coroutine hasta terminar, y lo cierra. Cero conflicto con el loop de
Uvicorn, que vive en un hilo completamente distinto.

Esto se probó en vivo, no solo se leyó en el código: un `asyncio.run()`
llamado directo dentro de `render()` y otro llamado dentro de un
`@st.fragment(run_every=...)` devolvieron, los dos,
`threading.current_thread().name == "ScriptRunner.scriptThread"` — un
fragmento **no** abre un hilo nuevo propio, corre en el mismo hilo de
script de la sesión. La misma garantía vale para código llamado desde
adentro de un fragmento, no solo desde `render()` directo.

**El contraste exacto, ya documentado en la sección 7 para el otro
lado de esta misma moneda:** `bot_auth.py` corre en el hilo de
`python-telegram-bot`, que **ya tiene** su propio event loop corriendo
todo el tiempo — ahí un `asyncio.run()` propio sí explota
(`RuntimeError: asyncio.run() cannot be called from a running event
loop`), por eso `auth.alertar_moderacion` recibe un `Bot` ya abierto en
vez de crear uno. La diferencia no es "web vs. bot" en general, es
literalmente si el hilo que te está ejecutando ya tiene un loop
corriendo o no. En los módulos de OLIMPO (siempre corriendo en
`ScriptRunner.scriptThread`) nunca lo tiene — por eso el patrón `_run()`
de `_template.py` funciona sin más.

**El costo real no es seguridad, es que no hay nada persistente entre
llamadas — y eso es a propósito, no algo a "arreglar".** Cada
`asyncio.run()` crea y destruye un event loop nuevo — y con él, en el
patrón de `tempmail.py`/`smspool.py`, una `aiohttp.ClientSession` nueva
por llamada (nunca reusada, mismo criterio que `sdk.enviar_telegram` con
`telegram.Bot`, sección 7). Si tu `render()` llama a varias funciones
async-envueltas en el mismo rerun, cada una paga ese costo de
armado/derribo por separado — aceptable para el volumen de estos
módulos.

**Prohibido, sin excepción: guardar un event loop o una sesión de
`aiohttp` a nivel de módulo para reusar entre llamadas.** No es una
opción de diseño válida bajo ninguna circunstancia, por dos razones
independientes, cualquiera de las dos ya alcanza: (1) es el antipatrón
exacto de la sección 4-bis — estado a nivel de módulo, compartido entre
todos los usuarios del proceso; (2) un event loop creado en el hilo de
una sesión **no es seguro de reusar** desde el hilo de otra sesión —
cada una tiene el suyo propio, y no existe ningún mecanismo de OLIMPO
pensado para compartir uno entre sesiones. Cada llamada crea el suyo y
lo cierra; así tiene que quedar siempre.

---

## 7. Notificaciones — Telegram y auditoría

Además de mostrar cosas en la UI, tu módulo puede escribirle a un
usuario puntual por Telegram, y dejar un rastro de auditoría para los
admins. Los dos van por el bot de OLIMPO (`OLIMPO_BOT_TOKEN`, leído
directo de `os.environ` dentro de `sdk._enviar_dm`/`sdk._alertar`), así
que no necesitás manejar ningún token vos mismo.

### ¿De dónde sale el `user_id` al que le mando algo?

No hay que "consultarlo" en ningún lado especial — es el mismo
`user_id` que ya tenés como parámetro, en dos situaciones distintas:

**Caso 1 — mientras el usuario está interactuando con tu módulo.**
`render(user_id)` se ejecuta con el Telegram ID real de quien tiene la
pestaña abierta en ese momento (`app.py` lo fija en `st.session_state`
después de que confirma el acceso desde Telegram en el login). Cualquier cosa que pase
**dentro de esa misma llamada** — comprar un número, revisar si llegó
un código, leer un correo — ya tiene ese `user_id` a mano. Es el caso de
`smspool.py`: compra, reembolso y entrega de código pasan todos dentro
de `render()`, así que `sdk.enviar_telegram(user_id, ...)` usa
directamente el parámetro, sin buscar nada.

**Caso 2 — el evento no ocurre en la misma pasada que lo originó** (por
ejemplo, un correo nuevo llega a una cuenta que se creó hace días, o
querés reaccionar a un pedido por su ticket sin que el dueño esté
mirando la pantalla). Ahí el `user_id` no está en ningún parámetro —
tiene que salir de **tu propia tabla** (patrón (b) de la sección 4):
guardá el `user_id` como columna junto con el registro cuando lo creás,
y buscalo por el identificador del registro cuando necesites saber a
quién avisarle:

```python
def notificar_por_ticket(ticket_id: str, texto: str) -> None:
    with sdk.db_conn() as conn:
        row = conn.execute(
            "SELECT user_id FROM mimodulo_pedidos WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    if row:
        sdk.enviar_telegram(row["user_id"], texto)
```

Así lo hace `smspool.py`: `olimpo_sms_orders` guarda el `user_id` de
quien compró cada número en el momento de la compra (`registrar_pedido`,
`smspool.py:179-195`) — es la fuente de verdad para saber a quién
pertenece ese pedido, sea cual sea el momento en que se resuelva (el
propio usuario revisando, la expiración automática, o una cancelación).

**Nunca derives ni adivines** el `user_id` de otro módulo (leyendo su
tabla directamente) ni de la sesión de otro módulo — cada módulo
mantiene su propio mapeo registro → usuario. Y si tu módulo necesita
avisarle a un usuario *distinto* del que está interactuando ahora mismo
(por ejemplo, una acción en `render_admin()` que actúa sobre otro
usuario), pedí el Telegram ID explícitamente con un `st.text_input` —
no lo inventes.

### DM a un usuario

```python
sdk.enviar_telegram(user_id, "📱 Tu número: <code>+52...</code>")
```

Por dentro es `asyncio.run(_enviar_dm(...))`, y `_enviar_dm` abre un
`telegram.Bot` nuevo por llamada (`async with Bot(token=...) as bot`) —
no hay una conexión persistente que administrar. Úsalo para entregarle al
usuario algo que no querés que dependa de que tenga la pestaña del
navegador abierta: el número asignado, el costo cobrado, la confirmación
de un reembolso. Si el envío falla (por ejemplo, nunca le escribió al
bot) no rompe tu módulo — el `except Exception: log.exception(...)`
adentro de `enviar_telegram` se traga el error y sigue.

#### El camino exacto: de tu `render()` a la app de Telegram del usuario

No hay dos bots — `sdk.enviar_telegram` usa exactamente el mismo bot que
ya conocés por `bot_auth.py` (los botones de login, `/admin`, `/usuario`),
leyendo el mismo token de entorno (`OLIMPO_BOT_TOKEN`, `bot_auth.py:262`
y `sdk.py:86`). El recorrido completo de una llamada, de punta a punta:

1. Tu módulo corre dentro del proceso **web** (`app_olimpo-web-1`,
   Streamlit) — nunca dentro del proceso del bot (`app_olimpo-bot-1`,
   `bot_auth.py`, long-polling). Son dos contenedores Docker separados
   que comparten el mismo valor de `OLIMPO_BOT_TOKEN` por variable de
   entorno — no hay ningún objeto ni conexión en memoria compartida
   entre los dos procesos.
2. `sdk.enviar_telegram(user_id, texto)` llama a
   `asyncio.run(_enviar_dm(user_id, texto))` (`sdk.py:98`).
3. `_enviar_dm` abre una sesión nueva y descartable contra la API de
   Telegram (`async with Bot(token=os.environ["OLIMPO_BOT_TOKEN"]) as
   bot`, `sdk.py:85-87`) y llama `bot.send_message(chat_id=user_id,
   text=texto, parse_mode=ParseMode.HTML)` — una petición HTTP directa a
   la API de Telegram. El proceso de `bot_auth.py` no se entera ni
   participa en ningún momento de este envío puntual.
4. Telegram entrega el mensaje al chat privado que el usuario ya tiene
   con el bot de OLIMPO — el mismo chat donde recibió el `/start`
   original o los botones de login de `bot_auth.py`.

**Requisito silencioso, de la propia API de Telegram, no de OLIMPO:**
para que el paso 4 funcione, el usuario tiene que haberle escrito al bot
alguna vez antes (aunque sea un simple `/start`) — un bot no puede
iniciar una conversación con alguien que nunca le escribió primero. Si
nunca lo hizo, Telegram devuelve un error al `send_message`, y ese error
queda atrapado por el `except Exception: log.exception(...)` de
`enviar_telegram` (`sdk.py:99-100`): tu módulo sigue funcionando con
normalidad, el usuario simplemente nunca recibe el DM, y no hay forma de
saberlo desde la UI en ese mismo momento.

#### Por qué esto es "silencioso" y qué significa exactamente

`sdk.enviar_telegram`, usado solo — sin acompañarlo de `sdk.alertar` — es
el mecanismo exacto para entregarle un resultado a un usuario sin dejar
ningún rastro visible en el canal de logs ni para los admins:

- Si el envío **funciona**: el usuario recibe el DM y nada más pasa.
  Ningún mensaje se publica en `OLIMPO_LOG_CHANNEL_ID` ni se manda a
  ningún admin — `alertar()` es una función completamente aparte (ver
  abajo), y `enviar_telegram` nunca la llama internamente ni depende de
  ella.
- Si el envío **falla**: el único rastro queda en el log de proceso del
  contenedor `app_olimpo-web-1` (`log.exception(...)`, visible solo
  entrando al servidor con `docker logs`/`docker compose logs`) — no
  aparece como mensaje de Telegram en ningún lado, no dispara ningún
  `st.error` en la UI (la función nunca relanza la excepción hacia quien
  la llamó), y no queda ninguna fila ni bandera en ninguna tabla que
  registre el intento fallido, salvo que vos mismo agregues esa lógica.

Esta separación entre las dos funciones **no** significa "ocultarle el
dato al admin" — significa que el mensaje al **usuario** y el mensaje de
**auditoría** son dos llamadas independientes, con dos textos
independientes que vos controlás por separado (podés mandarle al usuario
un tono amigable, "¡Llegó tu código!", y al canal de auditoría uno más
técnico con ticket e IDs, sin que el formato de uno dependa del otro). De
hecho, cuando el evento sí mueve créditos, la sección 5 y el checklist
exigen `sdk.alertar(...)` además del DM — y, como ya explica el resto de
esta sección, esa alerta normalmente **incluye el mismo dato real
entregado** (no un resumen vago), justamente para que sirva de prueba
ante un reclamo.

**Cuándo alcanza con `enviar_telegram` solo, sin `alertar`:** cuando el
resultado que entregás no mueve créditos y no hace falta que quede
auditado para resolver un reclamo — un recordatorio, un dato puramente
informativo, la confirmación de algo que no tuvo costo. Es exactamente
el caso de uso para el que existe esta separación entre las dos
funciones del SDK.

### Alerta de auditoría (a los admins)

```python
sdk.alertar(
    f"📱 SMS — nueva solicitud\n"
    f"👤 {user_id}\n"
    f"💳 {credits} crédito(s) cobrados\n"
    f"🎫 {order_id}"
)
```

`alertar()` decide el destino así (`sdk.py:119-122`):

```python
canal = os.getenv("OLIMPO_LOG_CHANNEL_ID")
destinos = [canal] if canal else auth.list_admin_ids()
```

Si hay un canal de logs configurado, todo va ahí (un solo destino). Si
no, se manda por DM a *cada* admin de `auth.list_admin_ids()` — varios
destinos. Tu módulo no elige entre esos dos modos, `alertar()` ya
resuelve cuál corresponde según la configuración del entorno. Es la
prueba que evita discusiones más adelante — usala en **todo evento que
mueva créditos o que alguien pueda después negar**:

- Se cobró y se entregó un número → queda registrado qué se cobró y qué se entregó.
- Se cobró pero la API externa nunca entregó nada → queda registrado el reembolso automático (protege al usuario: "sí me reembolsaron").
- Llegó el código/resultado final → queda registrado con el dato real entregado (protege a OLIMPO: si el usuario dice "nunca me llegó" habiendo llegado, está el log).
- Cancelación manual del usuario → queda registrado que fue el usuario quien canceló, no un error del módulo.

`modules/smspool.py` implementa los cuatro casos —
`_notificar_compra`, `_notificar_reembolso`, `_notificar_codigo`, y el
reembolso por error de compra inline dentro de `render()` — es la
referencia a copiar para cualquier módulo que cobre créditos (recorrida
completa en la sección 10).

También se usa para intentos de acceso fallidos a la app en sí — pero
ojo con el segundo ejemplo, no es literalmente la misma función:
`app.py::_login_screen` (Telegram ID no autorizado) sí llama a
`sdk.alertar()` directo, la misma función de esta sección. En cambio
`bot_auth.py::on_login_callback` (alguien rechazó una solicitud de
login) llama a `auth.alertar_moderacion(bot, tg_id, mensaje)` — una
función hermana, no `sdk.alertar()`: resuelve el destino de la misma
forma exacta (canal de logs si está configurado, si no DM a cada admin),
pero además le agrega los botones de moderación
(`teclado_moderacion`: "🚫 Cerrar sesión" / "⛔ Revocar membresía") y
recibe un `Bot` ya abierto en vez de crear uno con `asyncio.run()` —
necesario porque se llama tanto desde `app.py` (que sí puede abrir su
propio `asyncio.run()`) como desde dentro de `bot_auth.py`, que ya está
corriendo dentro de un event loop de `python-telegram-bot`, donde un
`asyncio.run()` propio lanzaría error. Ninguna de las dos — ni
`sdk.alertar` ni `auth.alertar_moderacion` — es parte de ningún módulo
puntual; las dos son mecanismo del núcleo de OLIMPO. La única expuesta
por el SDK para que la uses desde tu módulo es `sdk.alertar()`.

### Sonido de éxito

```python
sdk.sonido_exito()
```

Por dentro, `sonido_exito()` llama a `get_sonido_exito()` (que lee de la
tabla `configuracion`, clave `'sonido_exito'` — el archivo que subió un
admin en Admin > Sonido de éxito, o `assets/ding.wav` de fábrica si nadie
subió nada) y hace `st.audio(contenido, format=mime_type, autoplay=True)`
— eso es *todo* lo que hace: no hay lógica de "no repetir", eso es
responsabilidad tuya, por lo que sigue.

Dos cosas a las que hay que prestar atención, las dos por cómo funciona
Streamlit (reejecuta todo el script en cada rerun):

- **No la llames en cada rerun de una condición que sigue siendo
  verdadera** — solo en la transición real de "no había pasado" a "acaba
  de pasar". `smspool.py` resuelve esto con una bandera explícita en el
  diccionario de `session_state`:
  ```python
  order["sonido_pendiente"] = True   # se marca en el momento del evento
  st.session_state[estado_key] = order
  ```
  y la consume recién en el render que efectivamente muestra el
  resultado en pantalla:
  ```python
  if order.pop("sonido_pendiente", False):
      st.session_state[estado_key] = order   # se guarda ya sin la bandera
      sdk.sonido_exito()
  ```
  `tempmail.py` resuelve el mismo problema con una estrategia distinta —
  un `set` de IDs de mensaje ya vistos en `session_state`, y solo suena
  para los IDs que todavía no estén en ese set (comparación contra
  estado anterior, en vez de una bandera explícita). Las dos formas son
  válidas; elegí la que encaje mejor con cómo tu módulo ya guarda su
  estado.
- **No la llames justo antes de un `st.rerun()`** — Streamlit descarta
  esa corrida al instante y el navegador nunca llega a reproducir el
  audio. Por eso `smspool.py`, en el botón "Revisar código"
  (`smspool.py:443-454`), marca `sonido_pendiente = True` y recién
  *después* hace `st.rerun()` — el sonido en sí se reproduce en el
  **siguiente** render, no en este, que es justamente el que tiene el
  `pop()` de arriba. Llamarla en el mismo bloque que dispara el
  `st.rerun()` sería tirar la llamada a la basura.

---

## 8. Cómo se gestiona un módulo (panel Admin)

**Contexto de despliegue, porque cambia qué opción de esta sección te
sirve en cada caso:** OLIMPO corre en este VPS vía Docker Compose —
`web` (Streamlit, `app.py`) y `bot` (`bot_auth.py`) son dos contenedores
separados que comparten el mismo `Dockerfile` (`build: .` en
`docker-compose.yml`) y el mismo volumen de datos (`/app/data`). Esto
importa concretamente para dos cosas de esta sección: qué sobrevive un
redeploy sin necesitar un commit, y qué necesita además reconstruir la
imagen (no solo subir un `.py`) — se aclara en cada punto de abajo.

Todo esto vive en **Admin > Gestión de módulos**, y cada acción del panel
llama directo a una función de `sdk.py` — no hay lógica duplicada entre
la UI del panel y el SDK:

- **Activar / Desactivar** (`sdk.activar`/`sdk.desactivar`) — un módulo
  desactivado no aparece como pestaña para nadie, pero sus datos y su
  código quedan intactos. `desactivar()` además saca el módulo de
  `_loaded` — si se reactiva más tarde, se vuelve a importar desde cero
  (útil si mientras tanto se subió una versión nueva del archivo).
- **Agregar módulo externo** (`sdk.registrar_externo`, ver sección 0
  para el flujo exacto de validación) — tres formas de llegar al mismo
  resultado, las tres pasan por la misma validación sin atajos:
  1. **Subir el archivo** con el `st.file_uploader` del panel.
  2. **Pegar el código directo** en un `st.text_area` (`app.py`, campo
     "Pegar código del módulo") — pensado para cuando el selector de
     archivos del celular no deja elegir un `.py` (pasa en algunos
     Android/MIUI). El texto pegado se codifica a UTF-8
     (`codigo_pegado.encode("utf-8")`) y se manda a
     `sdk.registrar_externo()` exactamente con los mismos bytes que
     tomaría de un archivo subido — no hay una validación "más floja"
     por haber pegado texto en vez de subir un archivo, pasa por
     `_validar_contenido` y `_validar()` igual que cualquier otra vía.
  3. **Mandarle el `.py` al bot de Telegram** (como admin) —
     `bot_auth.py::on_document` llama a la misma
     `sdk.registrar_externo()`, sin pasar por el navegador para nada.

  Cualquiera de las tres formas valida antes de guardar — si no cumple
  el contrato, no se guarda nada — y el resultado vive en
  `external_modules/`, fuera de git, para poder probarlo sin tocar el
  código versionado.
- **Si tu módulo necesita una librería de Python que el proceso todavía
  no tiene instalada** — ninguna de las tres formas de arriba alcanza
  por sí sola. Subir o pegar el `.py` deja el código en su lugar, pero
  el intérprete de Python que lo importa (corriendo dentro del
  contenedor `web`/`bot` de este VPS) sigue sin la librería — vas a ver
  `ModuleNotFoundError` en cuanto `sdk._importar_externo` intente
  importarlo. Hace falta, además, que alguien con acceso al VPS:
  1. Agregue la librería a `requirements.txt` (versión fijada, igual
     que las demás — `aiohttp==3.14.3`, por ejemplo).
  2. Reconstruya la imagen y recree los contenedores —
     `sudo docker compose build web bot && sudo docker compose up -d web bot`.
     Un simple `restart` no alcanza: reusa la imagen vieja tal cual, sin
     la librería nueva.
  3. Tenga en cuenta que `web` y `bot` comparten el mismo `Dockerfile`
     (`build: .`), así que el rebuild reconstruye la imagen de los dos
     contenedores aunque la librería sea solo para un módulo de `web` —
     esperable, no un error.

  Esto reinicia `web`/`bot` un momento — igual que cualquier reinicio de
  contenedor, mejor coordinarlo en horario de poco uso del grupo. Para
  probar rápido si la librería resuelve el problema antes de comprometerte
  al rebuild: `sudo docker exec app_olimpo-web-1 pip install nombre_lib`
  funciona, pero se pierde en el próximo reinicio — nunca lo dejes como
  solución permanente.
- **Subir el `.py` directo a `modules/` por GitHub** — sin pasar por el
  panel para nada. Si el archivo cumple el contrato,
  `sdk.descubrir_e_instalar()` lo detecta y lo registra solo como
  **interno** la próxima vez que arranca la app (cada redeploy). Es la
  vía más simple desde el celular: subís el archivo con la app de GitHub
  a la misma carpeta donde están `smspool.py` y `tempmail.py`, y listo —
  no hace falta ni loguearse como admin en OLIMPO.
- **Hacer interno** (`sdk.hacer_interno`) — "gradúa" un módulo externo
  copiando su archivo a `modules/` (`(MODULES_DIR / f"{module_id}.py").write_bytes(...)`),
  para que quede versionado como parte oficial de OLIMPO. El archivo
  externo original **no se borra** (queda de respaldo en
  `external_modules/`), y el registro en `sdk_modulos` pasa a `origen =
  'interno'` con un `UPDATE` explícito (a diferencia del `ON CONFLICT`
  de `_registrar_fila`, sección 1, que no toca `origen`; acá sí se
  actualiza de verdad). Al final llama a `recargar(module_id)` — así, la
  próxima vez que el proceso necesite ese módulo, `_cargar()` ya lo
  trata como interno (vía el paquete normal `modules.<id>`) en vez de
  reusar el objeto que tenía cacheado desde cuando era externo.

  **Importante sobre persistencia:** copiar el archivo a `modules/` lo
  guarda en el filesystem del contenedor **en ejecución**, no en la
  imagen de Docker ni en ningún volumen — a diferencia de
  `external_modules/`, que en `docker-compose.yml` está montado como
  bind mount al filesystem del propio VPS
  (`./external_modules:/app/external_modules`) y por eso sobrevive tanto
  a un reinicio del contenedor como a un rebuild completo. `modules/` no
  tiene ese mount: vive solo dentro de la imagen construida (`build:
  .`). Un `docker compose restart` no lo toca, pero un redeploy normal
  (`git pull` + `docker compose build` + `up`, que descarta el
  contenedor viejo y arranca uno nuevo desde la imagen recién
  construida) **sí lo pierde** si nadie hizo `git add
  modules/<id>.py` y commiteó antes de ese redeploy. Es exactamente la
  razón de la frase "el panel no hace commits por vos" — no es solo una
  formalidad de control de versiones, es lo único que separa "internar
  un módulo" de "perderlo en el próximo deploy".
- **Recargar** (`sdk.recargar`) — saca el módulo de `_loaded` y de
  `sys.modules` (tanto `modules.<id>` como `olimpo_ext_<id>`, según de
  dónde venga), forzando que la próxima vez que se necesite se importe
  de cero. Está disponible para **externos e internos por igual** — en
  el panel aparece un botón "Recargar" en las dos situaciones (columnas
  separadas si es externo, un único botón si es interno). Sirve tanto si
  subiste una versión nueva de un externo, como si actualizaste el `.py`
  de un interno directamente en el filesystem del contenedor (por
  ejemplo, un `git pull` manual dentro del contenedor) sin reiniciar el
  proceso de Streamlit — en cualquiera de los dos casos, sin "Recargar"
  seguirías viendo el código viejo ya cacheado en `_loaded` hasta el
  próximo reinicio del proceso.
- **Eliminar** (`sdk.eliminar`) — solo para externos: `sdk.py` chequea
  `fila["origen"] == "interno"` y lanza `ValueError` explícito si
  intentás borrar uno interno desde acá. Borra el registro de
  `sdk_modulos`, el archivo `.py`, y lo saca de `_loaded`.

---

## 9. Checklist antes de subir tu módulo

- [ ] `MODULE_ID` es único, en minúsculas, sin espacios, y es el que vas
      a mantener para siempre (sección 1 explica por qué cambiarlo
      después es costoso, y por qué reusar el de otro módulo puede
      dejarlo corriendo con código equivocado sin que el panel te avise).
- [ ] `MODULE_NAME` empieza con un emoji (así se ve bien como pestaña).
- [ ] `render(user_id)` no lanza excepciones de control de flujo — solo
      errores reales (que quedan atrapados por `sdk.api_errors` o por
      el wrapper del panel, mostrando un mensaje en vez de romper la app).
- [ ] Todas las `key=` de tus widgets llevan el prefijo `MODULE_ID`.
- [ ] Todas las claves de `st.session_state` llevan el prefijo `MODULE_ID`.
- [ ] Si declarás algo a nivel de módulo (fuera de una función): no es
      un `dict`/`list` que crece sin límite. Ver sección 4-bis.
- [ ] Si cobrás créditos: usás `sdk.charge`/`sdk.refund`, nunca tocás
      `creditos.py` directo, y reembolsás en cualquier camino de fallo
      (error de API, cancelación del usuario, expiración).
- [ ] Si cobrás créditos: cada cobro, reembolso y entrega de resultado
      final pasa por `sdk.alertar(...)` — sin eso, un reclamo del
      usuario no tiene forma de resolverse.
- [ ] Si guardás datos: elegiste el patrón correcto de la sección 4 y
      creás tus tablas en `on_activar()` (no asumís que ya existen).
- [ ] Si llamás una API externa: usás `sdk.http_get`/`sdk.http_post` (o
      manejás vos mismo el proxy si seguís con `aiohttp`).
- [ ] Si tu código async usa el patrón `_run(coro): return asyncio.run(coro)`
      (sección 6): no armaste un event loop ni una `aiohttp.ClientSession`
      a nivel de módulo para reusar entre llamadas — cada llamada crea y
      cierra los suyos, a propósito.
- [ ] No leés ni escribís tablas de otro módulo ni del núcleo
      (`whitelist`, `creditos`, `carrusel`) directamente.
- [ ] Si agregás una sección a Admin, es vía `render_admin()`, no
      metida en otro lado.
- [ ] Todo resultado que el usuario vaya a copiar (email, teléfono,
      código, ticket, contraseña generada) se muestra con
      `st.code(valor, language=None)`, nunca `st.write`/`st.text`
      (sección 2-bis).
- [ ] Si le mandás un resultado a un usuario por Telegram y el evento no
      mueve créditos ni necesita quedar auditado, alcanza con
      `sdk.enviar_telegram` solo — no hace falta `sdk.alertar` para todo
      (sección 7).
- [ ] Si consultás un dataset que puede vivir en una BD compartida o en
      tu propio archivo, revisás primero `sdk.listar_bd_compartidas()`
      antes de caer a `sdk.module_dir(...)` (sección 4).
- [ ] Si copiaste código de otro módulo (o le pediste a una IA que se
      basara en uno): leíste cada función copiada y borraste la que tu
      `render()` nunca llama — sobre todo cualquier chequeo que pueda
      saltear en silencio la acción principal (horario, flag, límite)
      sin loguear ni mostrar nada (sección 1).
- [ ] No hay ningún `time.sleep()` bloqueante dentro de `render()` (y
      mucho menos un `while True` con sleep) — pasos espaciados usan
      `st.session_state` + botón/rerun, o un `run_every` con los mismos
      gates de `tab.open`/`session_expires_at` de la sección 7 (sección
      2-ter).
- [ ] No usás `st.tabs()` ni `st.sidebar` en ningún lugar de tu
      `render()` — cualquier selector de sub-vistas usa
      `st.segmented_control`/`st.pills`/`st.radio(horizontal=True)`, y
      cualquier control secundario va en el cuerpo normal de tu pantalla
      o en un `st.expander` (sección 3). Los dos tapan la barra de
      navegación real de toda la app — `st.dialog` sí es seguro.
- [ ] Si tu módulo necesita una librería que el proceso todavía no
      tiene: subir el `.py` no alcanza solo — hace falta agregarla a
      `requirements.txt` y reconstruir la imagen de Docker (sección 8).
- [ ] No tratás `st.session_state` (ni una variable a nivel de módulo)
      como si fuera persistencia — todo lo que tenga que sobrevivir a la
      sesión pasa por uno de los cinco patrones de la sección 4.
- [ ] Tu `render()` no asume que "descansa" cuando el usuario está en
      otra pestaña — corre en cada rerun de la app igual (sección 0);
      cualquier trabajo pesado sin gate de botón corre siempre, para
      todas las sesiones con tu módulo activo.

---

## 10. Recorrido completo: `modules/smspool.py`

De punta a punta, conectando cada bloque del archivo real con la sección
de este documento que lo explica.

**Encabezado (`smspool.py:1-24`)** — `MODULE_ID = "smspool"`,
`MODULE_NAME = "📱 Números SMS"` (sección 1). `_cache: dict = {}` a nivel
de módulo (sección 4-bis — el ejemplo real del patrón a no repetir sin
límite). `CACHE_TTL_SECONDS = 6 * 60 * 60` y `CANCEL_WINDOW_SECONDS = 10`
son constantes de negocio, no del SDK.

**Helpers de API (`_api_key`, `_get`, `_post`, `_normalizar_items`,
líneas 31-88)** — el módulo usa `aiohttp` directo (anterior a
`sdk.http_get`/`http_post`, sección 6), así que maneja sus propios
headers y errores. `_get`/`_post` relanzan como `RuntimeError` con el
body de la respuesta incluido — "el body suele traer el motivo real" es
un comentario real del archivo, porque `resp.raise_for_status()` de
aiohttp no te da ese detalle.

**Catálogo con caché (`listar_servicios`, `listar_paises_servicio`,
`_calc_credits`, líneas 91-154)** — acá vive el `_cache` de la sección
4-bis en uso real. `_calc_credits` convierte el precio en USD que
devuelve SMSPool a créditos OLIMPO vía una tasa configurable
(`get_config("usd_to_mxn", ...)`, patrón (a) de la sección 4) y tramos
fijos — esto es lógica de negocio del módulo, el SDK no sabe nada de
"créditos por tramo de precio". **Ojo con el nombre:** ese `get_config`
es una función propia de `smspool.py` (líneas 38-41, dos argumentos, lee
de su propia tabla `smspool_config`) — **no** es `sdk.get_config` (tres
argumentos, lee de `sdk_modulo_config`, sección 4a). Coinciden en el
nombre por casualidad de cuándo se escribió cada uno (`smspool.py` es
anterior al helper genérico del SDK); si tomás este archivo como base
para un módulo nuevo y también importás `sdk`, vas a tener dos
`get_config` con firmas distintas en el mismo archivo — renombrá el
local o usá directamente `sdk.get_config` en tu propio módulo.

**Compra (`comprar_numero`, `registrar_pedido`, líneas 157-195)** —
`comprar_numero` solo habla con la API externa, no toca créditos ni base
de datos. `registrar_pedido` es el patrón (b) de la sección 4: una fila
nueva en `olimpo_sms_orders` con `user_id` como columna — la fuente de
verdad para el caso 2 de notificaciones (sección 7) si hiciera falta
reaccionar fuera de `render()`.

**Estados posteriores (`check_sms`, `cancelar`, `marcar_fallido`,
`esta_expirado`, líneas 198-253)** — `check_sms` es el único lugar que
lee el campo `"sms"` de la respuesta de SMSPool (nunca `"code"` — el
comentario real del archivo dice explícitamente que ese campo no
existe). Los tres UPDATE de estado (`completed`, `cancelled`, `failed`)
son la máquina de estados completa de un pedido.

**Notificaciones (`_notificar_compra`, `_notificar_reembolso`,
`_notificar_codigo`, líneas 260-318)** — los tres casos de la sección 7:
cada uno hace un `sdk.enviar_telegram` (al usuario) *y* un
`sdk.alertar` (a los admins), nunca uno sin el otro. El comentario en
`_notificar_codigo` ("Queda el código real en el log de auditoría — es
lo que resuelve un reclamo") es la justificación textual del checklist
de la sección 9.

**`render()` (líneas 321-483)** — el corazón del módulo, con
`st.session_state[f"{MODULE_ID}_order"]` como única fuente de verdad del
pedido activo (sección 2):

- **Sin pedido activo:** selector de servicio → selector de país (con
  costo en créditos ya calculado) → botón "Obtener número". Al
  confirmar: `sdk.charge()` primero (sección 5); si no alcanza el
  saldo, `st.error` y no se llama a la API en absoluto. Si alcanza,
  recién ahí `comprar_numero()` — y si *eso* falla, `_refund()` +
  `sdk.alertar()` inmediato, con el motivo del error incluido en el
  mensaje. Es el patrón completo cobrar→intentar→reembolsar-si-falla de
  la sección 5, con la variante de que acá el "intentar" puede fallar
  después de ya haber cobrado, así que el reembolso es obligatorio en
  esa rama.
- **Con pedido activo, expirado sin código:** un último `check_sms()`
  antes de rendirse. Si llegó justo a tiempo, se guarda con
  `sonido_pendiente = True` (sección 7) y se notifica. Si no, se marca
  `failed`, se reembolsa, se notifica el reembolso, y se limpia el
  `session_state` — el usuario vuelve a ver el selector de servicio
  desde cero.
- **Con código ya recibido:** se consume `sonido_pendiente` (sección 7,
  el ejemplo exacto de "no sonar antes de un rerun") y se muestra el
  código con un botón "Nuevo pedido" que limpia el estado.
- **Esperando código todavía:** botones "Revisar código" (llama
  `check_sms()` a demanda) y, solo dentro de la ventana de 10 segundos
  (`puede_cancelar`), "Cancelar pedido" — que reembolsa, pero **no** de
  forma pareja a los otros dos caminos: acá solo se llama
  `sdk.alertar()` (admin/log), sin ningún `sdk.enviar_telegram` al
  usuario ni ningún `st.success`/`st.info` en pantalla confirmando el
  reembolso — a diferencia de la expiración (que sí usa
  `_notificar_reembolso`, con DM incluido) y de la compra fallida (que
  al menos muestra un `st.error` inline, aunque tampoco manda DM). De
  los tres caminos de reembolso, la cancelación manual es el que menos
  le confirma algo al usuario más allá de ver el saldo actualizado — una
  asimetría real del archivo, no necesariamente el ejemplo a copiar sin
  pensarlo (ver también la nota de la sección 5).
- **Historial:** una consulta de solo lectura a `olimpo_sms_orders`
  filtrada por `user_id`, las últimas 10 — nada nuevo respecto a la
  sección 4, es el mismo patrón (b) leído en vez de escrito.

**`render_admin()` (líneas 486-507)** — sección 3 y sección 4(a) en la
práctica: un `st.text_input` para la tasa, un botón que valida que sea
un número antes de guardar, y listo — no hay nada de créditos ni de
pedidos de usuarios en esta función, es exclusivamente configuración
global.

##############################

Requisitos mínimos obligatorios para un modulo tipo checker card

# Contrato obligatorio 

MODULE_ID   = "nombre_unico"          # minúsculas, guión bajo, sin espacios
MODULE_NAME = "🎯 Nombre del módulo"  # empieza con emoji
MODULE_VERSION = "1.0.0"              # semver
MODULE_AUTHOR = "Autor"               # nombre o alias
MODULE_DATA_SCOPE = "per_user"        # "shared" | "per_user" | "own_db"

def render(user_id: int) -> None:
    """UI principal del módulo."""
    ...

def render_admin(user_id: int) -> None:
    """Configuración global (proxies, parámetros, etc.)."""
    ...
    
    
# Importa 

import logging
import streamlit as st
import sdk

logger = logging.getLogger(__name__)

# UI usuario 

Elemento Tipo Propósito Ejemplo de implementación
Header st.header Identificar el módulo st.header(MODULE_NAME)
Subtítulo st.caption Contexto breve st.caption("Descripción de la funcionalidad")
Formulario st.form Agrupar entradas del usuario with st.form(key=f"{MODULE_ID}_form"):
Campos de entrada st.text_input, st.number_input, st.selectbox Datos necesarios para la operación Con key=f"{MODULE_ID}_campo"
Botón de envío st.form_submit_button Iniciar el proceso st.form_submit_button("Iniciar", type="primary")

# Validación de entradas 

errores = []
if not campo.isdigit() or len(campo) < 8:
    errores.append("Descripción clara del error.")
if not otro_campo.isdigit() or int(otro_campo) < 1 or int(otro_campo) > 12:
    errores.append("Otro mensaje claro.")

if errores:
    for e in errores:
        st.error(e)
    return
    
# Gestión de estado del proceso 

estado_key = f"{MODULE_ID}_proceso"
proceso = st.session_state.get(estado_key)

if proceso is None:
    # Mostrar formulario de inicio
    if submitted:
        # Inicializar estado y hacer rerun
        st.session_state[estado_key] = {
            "indice": 0,
            "total": cantidad,
            "resultados": [],
            "estadisticas": {"live": 0, "dead": 0, "errores": 0},
            # ... otros campos de estado
        }
        st.rerun()
else:
    # Continuar proceso desde el estado actual
    ...
    
# Estructura mínima del estado 
{
    "indice": 0,                      # Paso actual
    "total": 100,                     # Total de pasos
    "resultados": [],                 # Resultados positivos encontrados
    "live": 0,                        # Contadores
    "dead": 0,
    "errores": 0,
    "en_proceso": True,               # Flag de control
    # Campos específicos del módulo...
}

# Durante el check UI en vivo

# Inicializar elementos de UI
progress_bar = st.progress(0)
status_text = st.empty()
stop_col, _ = st.columns([1, 4])
with stop_col:
    if st.button("🛑 Detener", key=f"{MODULE_ID}_stop"):
        st.session_state.pop(estado_key, None)
        st.rerun()

# Contenedor para resultados en vivo
live_container = st.container()

# Procesar un paso
if proceso["indice"] < proceso["total"]:
    status_text.text(f"Procesando {indice+1}/{total}: {item_actual}")
    
    # Realizar operación
    resultado = realizar_operacion(item_actual)
    
    if resultado["tipo"] == "live":
        # Mostrar inmediatamente
        with live_container:
            st.success(f"**ÉXITO** — {resultado['detalle']}")
            st.code(resultado["dato"])  # Para copiar
            st.caption("Información adicional")
        
        # Notificar (si aplica)
        sdk.alertar(...)
        sdk.enviar_telegram(user_id, ...)
    
    # Actualizar estado
    proceso["indice"] += 1
    progress_bar.progress(proceso["indice"] / proceso["total"])
    st.session_state[estado_key] = proceso
    
    # Continuar al siguiente paso
    st.rerun()
    
    
# Pantalla de resultados 

if proceso["indice"] >= proceso["total"]:
    progress_bar.progress(1.0)
    status_text.text("✅ Proceso finalizado.")
    
    st.subheader("📊 Resultados")
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Éxitos", proceso["live"])
    with col2:
        st.metric("❌ Fallos", proceso["dead"])
    with col3:
        st.metric("⚠️ Errores", proceso["errores"])
    
    # Lista detallada de resultados positivos
    if proceso["resultados"]:
        st.markdown("### 🎯 Resultados encontrados")
        for item in proceso["resultados"]:
            st.code(item["dato"])
            st.caption(item.get("info", ""))
    
    # Botón para nueva operación
    if st.button("🔄 Nueva verificación", key=f"{MODULE_ID}_nuevo"):
        st.session_state.pop(estado_key, None)
        st.rerun()
        
        
# UI administrador 
configuración de proxies 

def render_admin(user_id: int) -> None:
    st.subheader(f"⚙️ Configuración de {MODULE_NAME}")
    
    # Sección de proxies
    st.caption("Lista de proxies (uno por línea).")
    proxies_actual = sdk.get_config(MODULE_ID, "proxies", default="")
    nuevos_proxies = st.text_area(
        "Proxies",
        value=proxies_actual,
        height=150,
        key=f"{MODULE_ID}_admin_proxies",
        help="Formato: http://user:pass@host:port o host:port"
    )
    if st.button("💾 Guardar proxies", key=f"{MODULE_ID}_guardar_proxies"):
        sdk.set_config(MODULE_ID, "proxies", nuevos_proxies)
        st.success("✅ Proxies actualizados.")
        
        
Gestión de base de datos "tarjetas.csv"
def _cargar_datos():
    ruta = sdk.module_dir(MODULE_ID) / "datos.csv"
    if not ruta.exists():
        return {}
    
    try:
        with open(ruta, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["clave"]: row for row in reader}
    except Exception as e:
        logger.exception("Error al cargar datos.csv: %s", e)
        return {}
        
        
Campos esperados en "tarjetas.csv"
Campo Tipo Descripción
bin string Prefijo de tarjeta (6-8 dígitos)
brand string Marca (Visa, Mastercard, etc.)
Banco string Entidad emisora
Tipo string Crédito/Débito
Pais string País de origen
Divisa string Moneda (USD, MXN, etc.)
Prepago string Sí/No
Comercial string Sí/No
Nivel string Clásica, Oro, Platino, etc.


# gen_cc (función auxiliar, algoritmo Luhn)

def _build_valid_card(prefix: str, length: int) -> str:
    """
    Genera un número de tarjeta válido según el algoritmo de Luhn.
    
    Args:
        prefix: Prefijo (BIN)
        length: Longitud total de la tarjeta
    
    Returns:
        Número de tarjeta con checksum válido
    """
    while True:
        # Generar dígitos aleatorios hasta completar length-1
        remaining = length - len(prefix) - 1
        partial = prefix + "".join(random.choices("0123456789", k=remaining))
        
        # Calcular dígito de verificación (Luhn)
        total = 0
        rev = partial[::-1]
        for i, ch in enumerate(rev):
            d = int(ch)
            if i % 2 == 0:  # Posiciones pares desde la derecha
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        
        check = (10 - (total % 10)) % 10
        card = partial + str(check)
        
        # Validar longitud final
        if len(card) == length:
            return card
            
            
Longitudes y prefijos 
Prefijo Longitud CVV
34, 37 (Amex) 15 4
300-305, 36, 38, 39 (Diners) 14 3
Resto 
(Visa, Mastercard, etc.) 16 3

# Carga de proxies (envolver todas las funciones con proxies)

def _cargar_proxies():
    raw = sdk.get_config(MODULE_ID, "proxies", default="")
    return [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]

def _formatear_proxy(s: str) -> str | None:
    """Convierte varios formatos a http://user:pass@host:port"""
    if not s:
        return None
    s = s.strip()
    if s.startswith("http://") or s.startswith("https://"):
        return s
    
    parts = s.split(":")
    if len(parts) == 4:
        # host:port:user:pass o user:pass:host:port
        if "." in parts[2]:
            user, pwd, host, port = parts
        else:
            host, port, user, pwd = parts
        return f"http://{user}:{pwd}@{host}:{port}"
    
    if len(parts) == 2:
        return f"http://{s}"
    
    return None
    
    
# Enriquecimiento de respuestas con "tarjetas.csv"

def _buscar_en_csv(clave: str, csv_data: dict) -> dict:
    """Busca información en el CSV cargado."""
    for size in (8, 6):
        prefix = clave[:size]
        if prefix in csv_data:
            return csv_data[prefix]
    return {}
    
    
# Logging obligatorio (debug por defecto)

import logging
logger = logging.getLogger(__name__)

# En funciones principales
logger.info("Iniciando proceso para usuario %d", user_id)
logger.debug("Payload enviado: %s", payload)
logger.warning("Respuesta inesperada: %s", response.text[:500])
logger.error("Error en operación: %s", exc_info=True)


# Manejo de errores y feedback

try:
    r = scraper.post(url, json=payload, timeout=15)
    if r.status_code == 403 and "stopped" in r.text.lower():
        logger.warning("API deshabilitada temporalmente")
        return {"tipo": "error", "mensaje": "API NO DISPONIBLE"}
    if r.status_code != 200:
        logger.warning("Error HTTP %d: %s", r.status_code, r.text[:200])
        return {"tipo": "error", "mensaje": f"HTTP {r.status_code}"}
except requests.exceptions.Timeout:
    logger.error("Timeout en API")
    return {"tipo": "error", "mensaje": "TIMEOUT"}
except Exception as e:
    logger.exception("Error inesperado: %s", e)
    return {"tipo": "error", "mensaje": str(e)[:80]}
    
    
# Notificación silenciosa sin mensajes, alertas, avisos, etc (Enviar en monospace las lives)

administrador (canal de logs )

sdk.alertar(
    f"📊 Evento importante en {MODULE_NAME}\n"
    f"👤 Usuario: {user_id}\n"
    f"📋 Detalle: {detalle}\n"
    f"💳 Resultado: {resultado}"
)

Mensaje al usuario 
sdk.enviar_telegram(
    user_id,
    f"🔔 {MODULE_NAME}\n"
    f"Resultado encontrado: {resultado}\n"
    f"Detalle: {detalle}"
)


# Resumen de procesos UI

Componente Cuándo usarlo Cómo implementarlo
st.form Entrada de datos del usuario Con key prefijado y botón type="primary"
st.session_state + st.rerun() Procesos largos por pasos Guardar estado, incrementar índice, rerun
st.progress Mostrar avance progreso / total
st.empty() Texto de estado dinámico Actualizar con .text()
st.container() Acumular resultados en vivo Almacenar resultados positivos
Botón "Detener" Abortar proceso pop(estado_key) + st.rerun()
st.metric Resultados finales Mostrar contadores con formato
st.code Datos para copiar Usar language=None
st.text_area Configuración de múltiples líneas Proxies, listas, etc.
sdk.get_config / sdk.set_config Configuración global Patrón (a) de persistencia
sdk.module_dir Archivos de datos del módulo Patrón (d) de persistencia