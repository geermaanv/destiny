# 0007 — Hosting: máquina local del equipo + túnel, no PaaS

- **Estado**: aceptada.

## Contexto

Se necesita que Pablo pueda ver el MVP corriendo sin coordinar horarios ni estar en la misma red que German. El acceso tiene que ser solo para ellos dos — no hace falta un hosting público tipo Vercel/Render/Railway (evaluados y descartados por ahora, ver conversación de la sesión 2026-10-07).

Restricción real encontrada: las sesiones de Claude Code en la nube (como esta) no pueden exponer un puerto a internet — la plataforma bloquea explícitamente intentos de túnel de ingreso externo desde ese entorno. Cualquier túnel tiene que armarse desde una máquina real del equipo.

## Decisión

Hostear desde la MacBook Air de German, con un túnel (`ngrok`) para darle a Pablo una URL pública. Esto requiere una sesión de **Claude Code local** en esa máquina (no esta sesión cloud) para poder instalar `ngrok` y ejecutar el túnel con acceso real al filesystem/red de la Mac.

Para que un solo túnel alcance (en vez de uno por cada app), se agregó un proxy en `apps/web`:

- `apps/web/next.config.ts` tiene `rewrites()`: todo lo que el browser pide a `/api/*` lo reenvía, server-side, a `API_INTERNAL_URL` (default `http://localhost:8000`).
- `apps/web/src/lib/api.ts` usa `/api` como base en vez de una URL absoluta a la API.
- Así el browser (el de Pablo, afuera de la red de German) solo necesita llegar al origen de Next.js. El túnel se abre una sola vez, sobre el puerto 3000. La API nunca queda expuesta directamente, y no hace falta CORS para el caso de uso remoto.

## Runbook (correr en la Mac, con Claude Code local o a mano)

```bash
# 1. Postgres, API y web, como siempre (ver CLAUDE.md)
docker compose up -d

cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload &

cd ../web
npm install
cp .env.example .env.local   # no hace falta tocar nada, los defaults ya sirven
npm run dev &

# 2. Túnel (una sola vez para instalar)
brew install ngrok
ngrok config add-authtoken <token de https://dashboard.ngrok.com/get-started/your-authtoken>

# 3. Túnel, cada vez que se quiera compartir. Usar el dominio fijo gratis de
#    la cuenta (dashboard de ngrok > Domains) para que la URL no cambie: el
#    webhook de WhatsApp registrado en Meta (spec A3, ADR 0008) depende de ella.
ngrok http --url=<dominio-fijo>.ngrok-free.dev 3000
```

Webhook de WhatsApp para Meta: `https://<dominio-fijo>.ngrok-free.dev/api/webhooks/whatsapp` (pasa por el mismo proxy de Next). El dominio concreto no se commitea (el repo es público).

`ngrok` imprime una URL pública (`https://xxxx.ngrok-free.app`). Esa es la que se comparte con Pablo — apunta al proxy de Next, que a su vez habla con la API local. Si se quiere que el link de invitación de WhatsApp (`C8-invitacion-whatsapp.md`) también sea válido desde afuera, setear `WEB_BASE_URL` en `apps/api/.env` a esa misma URL de ngrok antes de generar invitaciones.

## Consecuencias

- Mientras la Mac de German esté prendida y el túnel activo, Pablo puede entrar. Si se apaga o se cierra la terminal del túnel, el link muere — hay que avisar cuando se corta.
- La URL de ngrok cambia cada vez que se reinicia el túnel (plan free, sin dominio fijo) — hay que volver a compartirla.
- No reemplaza una decisión de hosting real para cuando haya usuarios de verdad fuera del equipo — eso sigue abierto (ver `BACKLOG.md`).
