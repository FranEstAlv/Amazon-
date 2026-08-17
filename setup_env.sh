#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }
info() { echo -e "      $*"; }

echo ""
echo "=== Setup entorno Amazon registro ==="
echo ""


# ── Python ────────────────────────────────────────────────────────────────────

PYTHON_BIN=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge "$PYTHON_MIN_MAJOR" ] && [ "$minor" -ge "$PYTHON_MIN_MINOR" ]; then
            PYTHON_BIN="$candidate"
            ok "Python $ver → $PYTHON_BIN"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    fail "Se requiere Python >= ${PYTHON_MIN_MAJOR}.${PYTHON_MIN_MINOR}. Instálalo y vuelve a ejecutar."
fi


# ── Entorno virtual ───────────────────────────────────────────────────────────

if [ -d "$VENV_DIR" ]; then
    warn "Entorno virtual ya existe en $VENV_DIR — se reutiliza."
else
    info "Creando entorno virtual en $VENV_DIR ..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    ok "Entorno virtual creado."
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

"$VENV_PIP" install --quiet --upgrade pip


# ── Dependencias ──────────────────────────────────────────────────────────────

info "Instalando dependencias base..."

"$VENV_PIP" install --quiet "selenium>=4.18.0"
ok "selenium"

"$VENV_PIP" install --quiet "Appium-Python-Client>=3.1.0"
ok "Appium-Python-Client"


# 2captcha — paquete oficial; fallback al antiguo nombre
if "$VENV_PIP" install --quiet "2captcha-python>=2.0.7" 2>/dev/null; then
    ok "2captcha-python"
else
    warn "2captcha-python falló — intentando nombre alternativo 'twocaptcha' ..."
    if "$VENV_PIP" install --quiet "twocaptcha" 2>/dev/null; then
        ok "twocaptcha (alternativo)"
    else
        warn "No se pudo instalar 2captcha. Si no lo necesitas, ignora este aviso."
    fi
fi

# capsolver
if "$VENV_PIP" install --quiet "capsolver>=1.0.7" 2>/dev/null; then
    ok "capsolver"
else
    warn "capsolver falló — intentando desde PyPI sin versión mínima ..."
    if "$VENV_PIP" install --quiet "capsolver" 2>/dev/null; then
        ok "capsolver (sin versión mínima)"
    else
        warn "No se pudo instalar capsolver. Si no lo necesitas, ignora este aviso."
    fi
fi


# ── Verificar imports ─────────────────────────────────────────────────────────

echo ""
info "Verificando imports ..."

check_import() {
    local module="$1"
    local label="$2"
    if "$VENV_PYTHON" -c "import $module" 2>/dev/null; then
        ok "import $label"
    else
        warn "import $label — no disponible"
    fi
}

check_import "appium"      "appium"
check_import "selenium"    "selenium"
check_import "twocaptcha"  "twocaptcha (2captcha)"
check_import "capsolver"   "capsolver"


# ── ADB ───────────────────────────────────────────────────────────────────────

echo ""
info "Verificando ADB ..."

if command -v adb &>/dev/null; then
    ADB_VER=$(adb version 2>/dev/null | head -1)
    ok "ADB encontrado — $ADB_VER"
else
    warn "ADB no encontrado en PATH."
    info "Instala Android SDK Platform Tools y agrega al PATH:"
    info "  https://developer.android.com/tools/releases/platform-tools"
fi


# ── Appium ────────────────────────────────────────────────────────────────────

echo ""
info "Verificando servidor Appium (localhost:4723) ..."

if command -v curl &>/dev/null; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://localhost:4723/status" 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        ok "Appium respondiendo en localhost:4723"
    else
        warn "Appium no responde (status: $HTTP_STATUS). Asegúrate de correr: appium"
    fi
else
    warn "curl no disponible — no se pudo verificar Appium."
fi


# ── Variables de entorno ──────────────────────────────────────────────────────

echo ""
info "Verificando variables de entorno ..."

check_env() {
    local var="$1"
    if [ -n "${!var:-}" ]; then
        masked="${!var:0:6}****"
        ok "$var = $masked"
    else
        warn "$var no definida"
    fi
}

check_env "CAPSOLVER_API_KEY"
check_env "TWOCAPTCHA_API_KEY"


# ── Resumen ───────────────────────────────────────────────────────────────────

echo ""
echo "=== Resumen ==="
echo ""
info "Activar entorno:  source $VENV_DIR/bin/activate"
info "Correr script:    python registro.py"
echo ""
ok "Setup completado."
echo ""
