# Any-API-Check

Any-API-Check is a Windows desktop workbench for relay and compatible API sites. It combines balance checks, sign-in automation, WAF cookie handling, model discovery, and API verification in one UI.

## Features

- Site management for URLs, API keys, cookies, tags, proxies, and advanced endpoint fields
- Provider management for login paths, sign-in paths, user info paths, and WAF cookie names
- Balance checks through bearer auth, URL key auth, and cookie-based account queries
- Browser login helper powered by Edge persistent sessions for Cloudflare and similar WAF flows
- Sign-in center for single-site sign-in, batch sign-in, log review, and cookie refresh
- Model catalog sync, streaming probes, non-streaming probes, and single-model checks
- API verification for connectivity, authenticity, and chat request testing
- Dashboard charts for balances, type distribution, sign-in activity, recharge trends, and action logs
- Tray support with minimize-to-tray behavior

## Project Layout

- `app.py` application entrypoint
- `relay_console/main.py` desktop bootstrap
- `relay_console/bridge.py` frontend/backend action bridge
- `relay_console/runtime/` API, database, chart, preset, and utility modules
- `relay_console/web/` frontend pages and static assets
- `config/templates/` bundled template files
- `config/presets/` bundled presets and CLI resources
- `scripts/build_windows.py` PyInstaller build script
- `scripts/build_installer.py` Inno Setup packaging script
- `build/installer/Any-API-Check.iss` installer definition

## Requirements

- Python 3.11
- Windows desktop environment
- Edge WebView2 runtime
- Optional, Playwright for browser-assisted flows
- Optional, Inno Setup 6 for installer generation

## Run from Source

Install dependencies first.

```bash
pip install -r requirements.txt
```

Run the desktop app.

```bash
python app.py
```

Debug mode.

```bash
python app.py --debug
```

## Packaging

Build the onedir application bundle.

```bash
python scripts/build_windows.py
```

Build the installer.

```bash
python scripts/build_installer.py
```

If you already have a built onedir folder and only want the installer.

```bash
python scripts/build_installer.py --skip-build --source-dir dist\Any-API-Check
```

## Data Storage

When running from source, runtime data is stored in the project directory.

- `config/app.db`
- `config/browser_profiles/`
- `debug/requests.log`

In the frozen Windows build, runtime data is moved out of `dist` and stored in the user profile.

- `%LOCALAPPDATA%\Any-API-Check\config\app.db`
- `%LOCALAPPDATA%\Any-API-Check\config\browser_profiles\`
- `%LOCALAPPDATA%\Any-API-Check\debug\requests.log`

Bundled templates and static resources are still read from the application directory.

- `config/templates/`
- `config/presets/cli_tools.json`
- `config/presets/cli_system.json`

Custom presets are stored in the runtime directory.

- `%LOCALAPPDATA%\Any-API-Check\config\presets\api_presets.json`

## Installer Notes

The installer is built with Inno Setup and installs per user by default.

- Install location `%LOCALAPPDATA%\Programs\Any-API-Check`
- Runtime data `%LOCALAPPDATA%\Any-API-Check`

This keeps upgrades from bloating the application folder with database files or browser profiles.

## Development Notes

These local artifacts should normally stay out of source control.

- `dist/`
- `dist_verify/`
- `dist_installer/`
- `build/pyinstaller*/`
- `build/spec*/`
- `config/app.db`
- `config/browser_profiles/`
- `config/browser_profiles/login_helper_cookies.json`
- `debug/`

## Known Notes

- The browser login helper depends on local Microsoft Edge
- The installer currently falls back to an English wizard when the local Inno Setup installation does not include a Chinese language pack
