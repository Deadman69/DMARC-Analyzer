# 📡 DMARC Guardian

**DMARC Guardian** is an open-source tool that automates the retrieval, storage, and analysis of DMARC aggregate reports from email inboxes.  
It combines a lightweight web interface with an automated IMAP fetcher to centralize email domain security reporting.

---

## 🚀 Features

- 🔄 Periodic DMARC report fetching via IMAP
- 🧱 Report parsing and structured storage in MariaDB
- 🌐 Web interface to browse and inspect reports
- 🐳 Fully containerized with Docker
- ⚙️ Built-in configuration via environment variables

---

## 🧰 Stack

- Python (Flask, asyncio, threading)
- MariaDB (or MySQL-compatible)
- Docker / Docker Compose

---

## 📦 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/dmarc-guardian.git
cd dmarc-guardian
```

### 2. Configure environment variables (optional)

All configuration is handled via `docker-compose.yml`.  
You can adjust the IMAP credentials, database config, and internal app port there.

### 3. Launch with Docker Compose

```bash
docker compose up -d --build
```

This will start:
- `web`: the main Python application which runs the Flask web interface
- `worker`: the Python app that runs the DMARC email fetcher (IMAP & Feeder)
- `mariadb`: the relational database for parsed DMARC report data

### 4. Access the Web App

Visit [http://localhost:62154](http://localhost:62154) in your browser.

---

## ⚙️ Configuration

All options can be set via environment variables in `docker-compose.yml`.  
Here are the key ones:

| Variable         | Description                                      | Example                        |
|------------------|--------------------------------------------------|--------------------------------|
| `IMAP_SERVER`    | IMAP server address                              | `imap.ionos.fr`                |
| `IMAP_PORT`      | IMAP server port (usually 993 for SSL)           | `993`                          |
| `IMAP_EMAIL`     | Email address used to fetch reports              | `example@domain.com`           |
| `IMAP_PASSWORD`  | Password for the above email                     | `your_password`                |
| `IMAP_SSL`       | Whether to use SSL for IMAP                      | `true`                         |
| `DB_HOST`        | MariaDB service hostname                         | `dmarc-guardian_database`      |
| `DB_PORT`        | MariaDB port                                     | `3306`                         |
| `DB_NAME`        | Database name                                    | `dmarcdb`                      |
| `DB_USER`        | Database user                                    | `dmarcuser`                    |
| `DB_PASSWORD`    | Database password                                | `dmarcpass`                    |
| `DB_DRIVER`      | SQLAlchemy driver URL prefix                     | `mysql+pymysql`                |
| `DOWNLOAD_DIR`   | Where to store raw downloaded DMARC XML reports in the container | `data/dmarc_reports`           |
| `WEB_APP_PORT`   | Flask app internal port in the container         | `8000`                         |

---

## 🧪 Development Notes

- Flask is run via `waitress` inside the Python app for production safety.
- Reports are downloaded, parsed, and stored automatically.

---

## 🧼 Cleaning Up

To stop and remove all containers and volumes:

```bash
docker compose down -v
```

---

## 📁 Project Structure

```text
.
├── app/                   # Application code
│   ├── web/               # Flask web app (routes, frontend)
│   ├── dmarc/             # DMARC report processing logic
│   └── services/          # IMAP handling, utilities
├── config/                # Environment/DB config
├── data/                  # Downloaded DMARC reports (volume-mounted)
├── init/database/         # SQL init scripts for DB (optional)
├── main.py                # Entrypoint: runs Flask + fetcher thread
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🛡️ License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

You are free to use, modify, and distribute this software.  
However, if you modify the code and deploy it (e.g. as a service), you **must** make the source code of your modified version publicly available under the same license.

See the [LICENSE](./LICENSE) file for details.