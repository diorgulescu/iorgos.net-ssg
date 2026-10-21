# Dragoș Iorgulescu — Personal Website & Tactical HUD

**Limbi / Languages:** [Română](README.md) | [English](README.en.md)

Site web personal migrat complet către o arhitectură statică pură **HTML5 / CSS / JavaScript**, **fără nicio dependență de Hugo sau alt motor de generare**.

Stilul vizual aplicat este **„Tactical Dark / Bento HUD”**, inspirat din interfețele tehnice sportive (*Garmin Tactical*, *Whoop*, *Strava Dark*) și sistemele de design moderne pentru dezvoltatori (*Linear*, *Raycast*).

---

## ⚡ Caracteristici Tehnice

* **100% Pure HTML / Zero-Engine:** Fiecare pagină este un document HTML autonom care poate fi deschis direct în browser (`file://`) sau găzduit pe orice server web (Nginx, Apache, Caddy, GitHub Pages, Cloudflare Pages, Namebox etc.).
* **Scheme de Culoare Duale (Dark & Light) cu Auto-Detecție de Sistem:**
  * **Modul Dark (Tactical Dark):** Canvas `#0B0F17`, panouri Bento `#111827`, accente neon și indicatori luminoși de status.
  * **Modul Light (Technical Paper / Lab HUD):** Canvas curat `#F8FAFC`, panouri `#FFFFFF` cu umbre tactile subtile, texte `#0F172A` / `#334155` de contrast înalt (AAA), accente de laborator și zero reflexii obositoare.
  * **Comutator Intuitiv (Desktop & Mobil):** Buton dedicat în navbar (pictogramă Soare/Lună Phosphor Icons) cu feedback live în bara superioară HUD (`MODE // DARK` / `MODE // LIGHT`).
  * **Auto-Detectare OS / Browser:** Site-ul citește automat `prefers-color-scheme` la prima vizită și se adaptează în timp real la schimbarea temei sistemului vizitatorului.
  * **Zero Flash of Wrong Theme (FOUC):** Script sincron inline în `<head>` care aplică tema instantaneu înainte de randarea paginii.
  * **Persistență în `localStorage`:** Dacă vizitatorul își alege manual o temă, preferința sa este salvată între pagini și sesiuni.
* **Design System „Tactical Dark / Bento HUD”:**
  * **Canvas:** `#0B0F17` (Dark) / `#F8FAFC` (Light)
  * **Panouri Bento:** `#111827` cu opacitate 88% + `backdrop-filter: blur(12px)` (Dark) / `#FFFFFF` cu umbre de precizie (Light)
  * **Elemente încastrate:** Casetare tehnică cu borduri subtile `1px` (`#1E293B` / `#CBD5E1`)
  * **Soft Glow Badges:** Accente semantice pe fundal calibrat (Emerald `#10B981`, Amber `#F59E0B`, Purple `#A855F7`, Sky `#38BDF8`)
  * **Triada Tipografică Google Fonts:**
    1. `Space Grotesk` (Titluri, antete tehnice, separatori `//`)
    2. `JetBrains Mono` (Cifre, metrici, date, unități de măsură, etichete de categorie, ceas live)
    3. `Inter` (Text curent, descrieri, articole)
  * **Iconițe Phosphor Icons:** `@phosphor-icons/web` (`ph-duotone` și `ph-bold`)
  * **Status Pills:** Indicatoare HUD cu punct luminos pulsant (`w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse`).

---

## 📂 Structura Fișierelor

```
iorgos-hugo/
├── index.html                   # Panoul principal Tactical Bento HUD
├── now.html                     # Pagina „Now” (focus curent în timp real)
├── blog/
│   ├── index.html               # Arhiva eseurilor (cu căutare/filtrare live)
│   ├── telefonul/               # Articol: Telefonul
│   ├── pacaneaua-din-buzunar/   # Articol: Păcăneaua din buzunar
│   ├── curatenie-reprezentata-femei/
│   ├── soferi-grabiti-scaune-copii/
│   ├── compensare/
│   ├── tool-becomes-drug/
│   ├── gasit-nordul/
│   └── is-strava-another-facebook/
├── programe/
│   ├── index.html               # Hub Bento pentru toate sistemele de antrenament
│   ├── tension-spectrum/        # Protocol complet Tension Spectrum + complexe SVG
│   ├── sfg-prep/                # Program de pregătire SFG I & SFB în 3 faze
│   └── bjj-prep/                # Program recuperare cot BJJ & bază aerobă
├── howto/
│   ├── index.html               # Arhiva ghidurilor tehnice (cu căutare/filtrare)
│   ├── deploy-hyperv2019/       # Ghid: Deploy Hyper-V Server fără DC
│   ├── create-fixed-size-files/ # Ghid: Creare fișiere dummy predimensionate
│   ├── aliases-profiles-pwsh/   # Ghid: Alias-uri și profiluri în PowerShell
│   ├── ssh-auth-windows10/      # Ghid: Autentificare SSH prin chei în Windows 10
│   ├── first-homelab/           # Ghid: Primul homelab (Supermicro, Proxmox)
│   ├── first-raspberrypi-cluster/# Ghid: Cluster Raspberry Pi 4 k3s
│   └── compiling-suckless-tools-freebsd/ # Ghid: Compilare dwm/dmenu pe FreeBSD
├── kettlebell/
│   └── index.html               # Protocol Navy Seal Burpees & Hardstyle
├── sounds/
│   └── index.html               # Arhiva proiectelor audio (Scentient Pencils, Sentem etc.)
├── images/                      # Toate activele media, SVG-urile și diagramele
├── css/
│   └── tactical.css             # Sistemul de stiluri Tactical Dark
├── js/
│   └── tactical.js              # Controller teme (Dark/Light), ceas live HUD, copiere cod
├── publish.py                   # Utilitar central: Ingest Markdown, Rebuild, Delete, Drafts, Serve
├── build_tactical_site.py       # Script utilitar pentru regenerare dacă se adaugă conținut nou
└── _legacy_hugo/                # Arhiva completă a vechilor fișiere Hugo (backup securizat)
```

---

## 🚀 Cum se Vizualizează sau Publică

### 1. Vizualizare Directă (Offline / Standalone)
Poți deschide direct fișierul `index.html` în orice browser web prin dublu-click. Toate legăturile interne și imaginile folosesc căi relative calibrate.

### 2. Rulare cu Server Local
Dacă dorești să rulezi un server local:
```bash
# Folosind utilitarul publish.py:
python3 publish.py --serve 8080

# Sau direct modulul Python:
python3 -m http.server 8080
```
Apoi deschide `http://localhost:8080`.

---

## ✍️ Publicarea & Administrarea Conținutului (`publish.py`)

Pentru a adăuga articole noi, a șterge conținut vechi sau a reconstrui instantaneu site-ul atunci când schimbi designul/CSS-ul, folosește utilitarul central **`publish.py`** (fără nicio dependență externă):

### 📋 Tabel Rapid de Comenzi (Cheat Sheet)

| Acțiune | Comandă Terminal | Descriere |
| :--- | :--- | :--- |
| **Publicare articol nou** | `python3 publish.py fisier.md` | Ingest automat în `content/`, compilare HTML și actualizare indecși |
| **Forțare categorie** | `python3 publish.py fisier.md -c howto` | Publică în categoria indicată (`blog`, `howto`, `programe`) |
| **Reconstrucție totală** | `python3 publish.py --rebuild` | Recompilează toate paginile și curăță folderele orfane |
| **Ștergere articol** | `python3 publish.py --delete slug` | Șterge fișierul `.md`, folderul HTML și recompune indecșii |
| **Generare ciornă nouă** | `python3 publish.py --new "Titlu" -c blog` | Creează un șablon Markdown precompletat cu câmpuri de metadate |
| **Server local preview** | `python3 publish.py --serve 8080` | Pornește un server web local la `http://localhost:8080` |

---

### 1. Adăugarea unui Articol Nou din fișier Markdown
Scrii un fișier Markdown (ex: `articol-nou.md`) și rulezi:
```bash
python3 publish.py articol-nou.md
```
Scriptul va:
* Detecta categoria din header (`category: blog`, `howto` sau `programe`).
* Copia automat fișierul sursă în `content/<category>/<slug>.md`.
* Compila pagina HTML autonomă în `<category>/<slug>/index.html` cu stilul Tactical Dark.
* Actualiza arhiva categoriei (`<category>/index.html`) reordonând cronologic articolele.
* Actualiza panoul principal (`index.html`) împrospătând KPI-urile și secțiunea de dispecerate recente.

Dacă vrei să forțezi o categorie anume din linia de comandă:
```bash
python3 publish.py articol-nou.md --category howto
```

### 2. Ștergerea sau Retragerea unui Articol
Dacă dorești să elimini un articol (cum ar fi „compensare” de la categoria blog), ai la dispoziție trei variante:

* **Opțiunea A — Comandă directă în script (Ștergere completă automată):**
  ```bash
  python3 publish.py --delete compensare
  # sau folosind calea completă:
  python3 publish.py --remove blog/compensare
  ```
  Scriptul va:
  1. Șterge fișierul sursă `content/blog/compensare.md`.
  2. Șterge directorul HTML compilat `blog/compensare/`.
  3. Recompila automat arhiva blogului (`blog/index.html`) și panoul principal (`index.html`), actualizând numărul total de dispecerate din KPI HUD.

* **Opțiunea B — Retragere temporară ca Ciornă (fără a pierde textul):**
  Deschizi `content/blog/compensare.md` și adaugi în antetul YAML:
  ```yaml
  draft: true
  ```
  Apoi rulezi:
  ```bash
  python3 publish.py --rebuild
  ```
  Scriptul va elimina pagina HTML de pe site și din indecși, dar va păstra fișierul `.md` în `content/blog/` pentru o republicare ulterioară.

* **Opțiunea C — Ștergere manuală a fișierului Markdown:**
  Dacă ștergi manual fișierul `content/blog/compensare.md` și rulezi:
  ```bash
  python3 publish.py --rebuild
  ```
  Scriptul detectează automat directoarele HTML fără corespondent Markdown („orfane”) și curăță folderul `blog/compensare/` de pe disc.

### 3. Reconstrucția Rapidă a Întregului Site
Dacă ai modificat stilurile din `css/tactical.css`, șabloanele HTML sau mai multe fișiere Markdown din `content/`:
```bash
python3 publish.py --rebuild
# sau simplu:
python3 publish.py
```

### 4. Configurarea Identității Globale (Nume, Subtitlu, Contact)
Dacă dorești să modifici numele, subtitlul din antet (ex: `TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER`) sau alte date de contact globale, modifică dicționarul `SITE_CONFIG` din antetul fișierului `publish.py`:
```python
SITE_CONFIG = {
    "author": "Dragoș Iorgulescu",
    "handle": "// DRAGOȘ IORGULESCU",
    "subtitle": "TEST ENGINEER // STRENGTH PRACTITIONER // ASPIRING VIDEOGRAPHER",
    "location": "BASE // BUCHAREST, RO",
    "email": "dragos@iorgos.net",
    ...
}
```
Apoi rulează:
```bash
python3 publish.py --rebuild
```
Scriptul va propaga automat noua identitate pe **toate cele 25+ de pagini** ale site-ului (inclusiv paginile statice `now.html`, `sounds/`, `programe/`).

### 5. Generarea unui Șablon Nou (Draft)
Pentru a începe rapid redactarea unui articol nou cu toate câmpurile de metadate precompletate:
```bash
python3 publish.py --new "Cum am configurat FreeBSD" --category howto
```
Va genera automat fișierul `content/howto/cum-am-configurat-freebsd.md` gata de editat.

### 6. Structura Recomandată a Header-ului Frontmatter
Orice fișier `.md` nou acceptă antetul standard:
```yaml
---
title: "Titlul Articolului sau Ghidului"
date: 2026-10-15
category: blog                 # "blog", "howto" sau "programe" (implicit: blog)
slug: titlu-articol            # opțional (generat automat dacă lipsește)
tag: "LINUX // AUTOMATION"     # opțional (dedus automat dacă lipsește)
badge_class: badge-emerald     # opțional: badge-emerald, badge-sky, badge-amber, badge-purple
excerpt: "Scurt rezumat..."    # opțional (extras automat din primul paragraf dacă lipsește)
read_time: "5 MIN READ"        # opțional (calculat automat pe baza numărului de cuvinte)
draft: false                   # opțional (dacă e true, nu este generat în HTML)
---

# Titlu Secțiune

Conținutul redactat în format Markdown standard...
```
