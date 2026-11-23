<p align="center">
  <img src="assets/logo.png" width="128" height="128" alt="bpc-fetch logo">
</p>

<h1 align="center">bpc-fetch</h1>

<p align="center">
  Bypass paywall sites — search, discover, and batch fetch articles as Markdown.
</p>

<p align="center">
  <a href="README_CN.md">中文文档</a> •
  <a href="#supported-sites">936 Sites</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#credits">Credits</a>
</p>

<p align="center">
  <a href="https://linux.do"><img src="https://img.shields.io/badge/LINUX%20DO-Community-blue?style=flat-square" alt="LINUX DO Community"></a>
</p>

---

## What is this?

A command-line tool that fetches full-text articles from 936 paywalled news sites and saves them as clean Markdown with images. It replicates the bypass logic of the [Bypass Paywalls Clean](https://gitflic.ru/project/magnolia1234/bypass-paywalls-chrome-clean) browser extension, but runs headlessly — no browser extension needed.

## Supported Sites

**936 sites** across 40+ countries. Highlights:

| Category | Sites |
|----------|-------|
| Financial | The Economist, Financial Times, Bloomberg, WSJ, Reuters, Forbes, Business Insider |
| US News | New York Times, Washington Post, LA Times, Chicago Tribune, Politico |
| UK/EU | The Telegraph, The Times, Der Spiegel, Le Monde, El País, Corriere della Sera |
| Tech/Science | Wired, The Atlantic, Nature, Science, Scientific American, MIT Tech Review |
| Magazines | The New Yorker, Vanity Fair, Vogue, National Geographic, Esquire |
| German | 76 sites (FAZ, Handelsblatt, Süddeutsche Zeitung...) |
| French | 69 sites (Le Figaro, Libération, Les Echos...) |
| More | Netherlands 30, Italy 28, Spain 26, Belgium 22, Australia 39... |

Run `bpc-fetch sites` to see the full list.

## Features

- **Full bypass coverage** — Replicates all BPC extension strategies: custom User-Agent, Googlebot/Bingbot spoofing, referer manipulation, Playwright JS interception, archive.org fallback
- **Auto fallback chain** — Each URL tries the optimal strategy, degrades gracefully until content is retrieved
- **Article discovery** — Find recent articles via RSS, sitemap, or browser-rendered homepage
- **Cross-site crawl** — Search + time filter + batch download in one command
- **Agent-friendly** — JSON stdout, stderr progress, `next_command` hints in every response
- **Windows exe** — Single-file distribution via PyInstaller, auto-downloads Chromium on first run

## Installation

### pip (recommended)

```bash
pip install bpc-fetch
playwright install chromium
```

### From source

```bash
git clone https://github.com/user/bpc-fetch.git
cd bpc-fetch
pip install -e .
playwright install chromium
```

### Windows exe

Download `bpc-fetch.exe` from [Releases](https://github.com/user/bpc-fetch/releases), then:

```
bpc-fetch.exe install-browser
bpc-fetch.exe doctor
```

### Using Monid (optional)

Set `MONID_API_KEY` to use Search1API through Monid for keyword searches in
`bpc-fetch search` and in `bpc-fetch crawl` when no sites are specified.
See the [Monid docs](https://docs.monid.ai).

## Usage

```bash
# Check setup
bpc-fetch doctor

# List supported sites
bpc-fetch sites --filter economist

# Discover today's articles from a site
bpc-fetch discover economist.com --since today

# Fetch a single article
bpc-fetch fetch "https://www.economist.com/leaders/2024/01/01/example" --out-dir ./articles

# Batch fetch from URL list
bpc-fetch batch --file urls.txt --out-dir ./articles

# Cross-site crawl: keyword + time range
bpc-fetch crawl "AI regulation" --sites economist.com,ft.com --since 7d --out-dir ./ai-articles
```

### Output format

```
article-title/
├── article-title.md      # YAML frontmatter + full text + image refs
└── images/
    ├── img_000_abc1.jpg
    └── img_001_def2.png
```

### Agent integration

All commands output JSON. Use `--compact` for minimal output:

```bash
bpc-fetch discover ft.com --since today --compact
# → {"ok": true, "domain": "ft.com", "count": 15, "articles": [...], "next_command": "bpc-fetch batch ..."}
```

## Bypass Strategies

| Strategy | Sites | Method |
|----------|-------|--------|
| `ua:custom` | 7 | Custom User-Agent string (Liskov, Google-InspectionTool, etc.) |
| `ua:googlebot` | 85 | Googlebot User-Agent |
| `ua:facebookbot` | 5 | Facebook crawler UA |
| `referer:google` | 2 | Google referer header |
| `block_js` | 425 | Playwright blocks paywall scripts via `Page.route()` |
| `archive` | 274 | Fetch from archive.org/archive.is |
| `cookies` | 138 | Access without tracking cookies |

## Building Windows exe

```bash
pip install pyinstaller
python build/build_win.py
# Output: dist/bpc-fetch.exe
```

## Credits

This tool is built on top of the bypass logic from:

- **[Bypass Paywalls Clean](https://gitflic.ru/project/magnolia1234/bypass-paywalls-chrome-clean)** by [magnolia1234](https://gitflic.ru/user/magnolia1234) — the original browser extension that provides the site database and bypass strategies. All credit for the paywall bypass research goes to the BPC project maintainers.

## License

MIT — see [LICENSE](LICENSE).

The `data/sites.js` file is from the Bypass Paywalls Clean project (MIT License).

---

## 致谢

本项目的开发 agent 能力由 [GenericAgent](https://github.com/lsdefine/GenericAgent) 提供。

### 🚩 友情链接

[![GenericAgent](https://img.shields.io/badge/Agent_Framework-GenericAgent-orange?style=for-the-badge&logo=github)](https://github.com/lsdefine/GenericAgent)
[![LinuxDo](https://img.shields.io/badge/社区-LinuxDo-blue?style=for-the-badge)](https://linux.do/)
