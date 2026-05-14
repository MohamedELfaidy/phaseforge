# PhaseForge — BASIC Language Compiler Web App

A Flask web application that visually walks every expression through all
compiler phases: Lexical Analysis → Tokenization → Parsing → AST → Interpretation.

**Live URL:** https://phaseforge.dpdns.org  
**VPS IP:** 35.207.153.112  
**University:** Minia University — Faculty of Computers & Information  
**Course:** Compiler Design 2025–2026  

---

## File Structure

```
phaseforge/
│
├── app.py                          ← Flask application (routes, API endpoints)
├── requirements.txt                ← Python dependencies (flask, gunicorn)
│
├── src/                            ← Compiler engine (pure Python, no external deps)
│   ├── __init__.py
│   ├── runner.py                   ← Main entry point; orchestrates all phases
│   │
│   ├── core/                       ← Shared primitives
│   │   ├── __init__.py
│   │   ├── constants.py            ← DIGITS, LETTERS, KEYWORDS
│   │   ├── tokens.py               ← Token class + all TT_* constants
│   │   ├── position.py             ← Source position tracker
│   │   └── errors.py               ← Error types (IllegalChar, InvalidSyntax, RTError)
│   │
│   ├── lexer/
│   │   ├── __init__.py
│   │   └── lexer.py                ← Lexical analyser (Phase 1 & 2)
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── nodes.py                ← AST node classes (with .to_dict() for JSON)
│   │   ├── parse_result.py         ← ParseResult helper
│   │   └── parser.py               ← Recursive descent parser (Phase 3 & 4)
│   │
│   ├── interpreter/
│   │   ├── __init__.py
│   │   ├── interpreter.py          ← AST interpreter (Phase 5)
│   │   ├── values.py               ← Number class + all math/bitwise/trig ops
│   │   ├── context.py              ← Context + SymbolTable
│   │   └── runtime_result.py       ← RTResult wrapper
│   │
│   ├── builtins/
│   │   ├── __init__.py
│   │   └── symbols.py              ← Global symbol table (PI, E, TAU, INF, NAN, null)
│   │
│   └── utils/
│       └── __init__.py
│
├── templates/
│   └── index.html                  ← Full single-page app (hero, playground, footer)
│
├── static/
│   ├── css/
│   │   └── style.css               ← Complete CSS design system (light theme)
│   ├── js/
│   │   └── main.js                 ← Interactive UI (tokens, parse tree, symbol table)
│   └── img/
│       ├── favicon.svg             ← Vector favicon (hexagon brand icon, indigo)
│       ├── favicon.ico             ← Multi-size ICO (16×16, 32×32, 48×48)
│       ├── favicon-32.png          ← 32×32 PNG favicon
│       ├── favicon-192.png         ← 192×192 PNG (Apple touch icon / PWA)
│       └── team/                   ← Drop team photos here (optional)
│           ├── mohamed_sayed.jpeg
│           ├── ammar_yasser.jpg
│           ├── beshoy_farouk.jpg
│           ├── hussien_mohamed.png
│           └── michael_hany.png
│
└── deploy/
    ├── nginx.conf                  ← Nginx site config (HTTP + commented HTTPS)
    ├── phaseforge.service          ← systemd unit file for Gunicorn
    └── deploy.sh                   ← One-shot deployment script for Ubuntu VPS
```

---

## Quick Deploy on Your VPS

```bash
# 1. Upload the project to your VPS
scp -r ./phaseforge user@35.207.153.112:/tmp/phaseforge

# 2. SSH in
ssh user@35.207.153.112

# 3. Run the deploy script
cd /tmp/phaseforge
sudo bash deploy/deploy.sh
```

### Manual step-by-step

```bash
# Install deps
sudo apt update && sudo apt install -y python3 python3-venv nginx certbot python3-certbot-nginx

# Copy files
sudo cp -r /tmp/phaseforge /var/www/phaseforge
sudo chown -R www-data:www-data /var/www/phaseforge
sudo mkdir -p /var/log/phaseforge && sudo chown www-data: /var/log/phaseforge

# Virtual env
sudo -u www-data python3 -m venv /var/www/phaseforge/venv
sudo -u www-data /var/www/phaseforge/venv/bin/pip install -r /var/www/phaseforge/requirements.txt

# Nginx
sudo cp /var/www/phaseforge/deploy/nginx.conf /etc/nginx/sites-available/phaseforge
sudo ln -sf /etc/nginx/sites-available/phaseforge /etc/nginx/sites-enabled/phaseforge
sudo nginx -t && sudo systemctl reload nginx

# Systemd
sudo cp /var/www/phaseforge/deploy/phaseforge.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now phaseforge

# SSL (after DNS is pointed to server)
sudo certbot --nginx -d phaseforge.dpdns.org -d www.phaseforge.dpdns.org
```

### Useful commands after deployment

| Action | Command |
|---|---|
| Check service | `sudo systemctl status phaseforge` |
| Restart service | `sudo systemctl restart phaseforge` |
| Live logs | `sudo journalctl -u phaseforge -f` |
| Reload Nginx | `sudo nginx -t && sudo systemctl reload nginx` |
| Renew SSL | `sudo certbot renew --dry-run` |

---

## API Endpoints

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/run` | `{ "code": "..." }` | result, tokens, parse tree, errors |
| POST | `/api/tokenize` | `{ "code": "..." }` | token list only |
| POST | `/api/parse` | `{ "code": "..." }` | parse tree only |
| POST | `/api/reset` | — | clears session variables |

---

## Team

| Name | LinkedIn |
|---|---|
| Mohamed Sayed | linkedin.com/in/mohamed-sayed-60ba8b264 |
| Ammar Yasser  | linkedin.com/in/ammar-yasser-83537a267  |
| Beshoy Farouk | linkedin.com/in/beshoy-farouk           |
| Hussien Mohamed | linkedin.com/in/hussien-mohammed-426947257 |
| Michael Hany  | linkedin.com/in/michael-hany-572034262  |

**Instructor:** Dr. Moussa Elkedr  
**Teaching Assistant:** Eng. Mina Essam
