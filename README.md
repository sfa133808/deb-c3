# C3 — Cloud Deployment: Projekt-Grundstruktur

Kurzprojekt-Skeleton für eine kleine Web-Anwendung (Backend) mit persistenter Datenablage, Docker- und Deploy-Vorlagen.

Ziel: eine Anwendung, die später auf einer Free-Tier-Plattform (z. B. Fly.io oder Render) betrieben werden kann — ohne kostenpflichtige Ressourcen.

Inhalt dieser Vorlage:
- `app/` — FastAPI-Beispiel (CRUD für `items`)
- `Dockerfile` — Container-Build
- `docker-compose.yml` — lokale Entwicklung mit persistentem Volume (`data`)
- `.env.example` — Environment-Variablen-Vorlage
- `.github/workflows/deploy.yml` — CI-Template (Platzhalter für Deploy-Token)

Nächste Schritte:
1. Lokales Ausprobieren: `docker compose up --build` (sehen, dass `http://localhost:8080/docs` erreichbar ist)
2. Account bei einer Free-Tier-Plattform erstellen (z. B. Fly.io oder Render). Kostenfrei nutzbare Optionen wählen.
3. Secrets (z. B. `DATABASE_URL`, Deploy-Token) in der Plattform setzen. CI-Workflow oder Platform-Auto-Deploy konfigurieren.

Weiterführende Dateien:
- [Dockerfile](Dockerfile)
- [.env.example](.env.example)
- [docker-compose.yml](docker-compose.yml)
- [app/main.py](app/main.py)

Begründung: Für die Vorstudie und das kostenfreie Deployment empfehle ich Fly.io (Free-Tier, einfache CLI-Integration, Volumes für Persistenz). Alternativ ist Render für einfache Web-Services möglich.

Deploy-Anleitung (Fly.io)
1) Voraussetzungen
	- Fly.io Account (kostenfrei tier möglich)
	- `flyctl` installiert: `curl -L https://fly.io/install.sh | sh`

2) Lokales Testen
	```bash
	docker compose up --build
	# Open http://localhost:8080/docs
	```

3) Erste Bereitstellung mit Fly
	```bash
	# melde dich an
	flyctl auth signup  # oder login
	cd /path/to/repo
	flyctl launch --no-deploy --name my-c3-app
	# Fly erzeugt fly.toml; anpassen falls nötig
	# Erstelle ein Volume für persistente Daten (optional, empfohlen)
	flyctl volumes create data --size 1 --region ord
	# Setze env vars
	flyctl secrets set DATABASE_URL="sqlite:///data/data.db"
	# Deploy
	flyctl deploy
	```

Hinweis: Fly kann SQLite in einem Volume verwenden; für produktive Szenarien ist eine Managed Postgres empfehlenswert (Fly bietet "postgresql" als Add-on).

CI / Auto-Deploy (GitHub Actions)
 - Setze `FLY_API_TOKEN` als GitHub Secret.
 - Beispiel-Workflow (ausgefüllter Job) könnte `flyctl deploy` auf `push` auslösen.

Secrets und Reproduzierbarkeit
 - Alle Secrets werden in der Plattform gesetzt (keine Hardcodierten Secrets im Repo).
 - In `.env.example` sind die benötigten Variablen beschreiben. Nutze `DATABASE_URL` zur Konfiguration.

Persistenz
 - Lokale Entwicklung: `docker-compose` nutzt ein named volume `data` (Ordner `/app/data`).
 - Fly.io: Volume `data` ermöglicht Persistenz über Deploys.

Logging
 - Die Anwendung schreibt strukturierte JSON-ähnliche Antworten und Uvicorn/Stdout-Logs werden von Fly/Platform erfasst.

Was als Nächstes
 - Optional: GitHub Actions Workflow zum Auto-Deploy ergänzen (benötigt `FLY_API_TOKEN`).
 - Optional: Managed DB (Postgres) konfigurieren, `DATABASE_URL` anpassen.

