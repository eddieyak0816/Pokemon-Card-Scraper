# Project Status — Pokemon Card CSVs & Site Automation

Date: 2026-04-01

## Overview
- Purpose: generate per-set CSVs (image URLs + metadata) from the public PokemonTCG JSON repo, automate generation in GitHub Actions, and (planned) create per-card product pages on the user's WordPress site.

## What’s Done
- Scripts: CSV generator implemented and run locally: [scripts/generate_csvs_from_repo.py](scripts/generate_csvs_from_repo.py)
- Output: many per-set CSVs generated under [csv_new/](csv_new/) (e.g., `Perfect Order.csv`, `Lost Origin.csv`).
- Repo & CI: repository created and pushed; workflow added at `.github/workflows/generate_csvs.yml` to run daily and on-demand.
- Notifications: Telegram bot configured; `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` saved as repo secrets; workflow sends a minimal Telegram message on run completion.

## Problems Encountered & Solutions
- Pushing from Actions to `main` failed (exit code 128): solved by using branch+PR flow (manual git+REST in workflow).
- SDK approach failed due to missing package: switched to reading raw JSON from the public repo to avoid SDK dependency.
- Some Actions default Node version warnings: added opt-in for Node 24 where needed.

## Remaining Work (short-term priorities)
1. Detect newly-created/changed CSVs during a run and record the set names (artifact or stdout). This will let notifications include which sets were added/updated.
2. Include CSV links (raw GitHub blob or repo URL) in the Telegram notification when new CSVs are created.
3. Implement a script to POST cards to the WordPress REST API and create `card` posts (see `scripts/push_cards_to_wp.py` — planned).

## Remaining Work (longer-term)
- Create a `card` custom post type and template on the WordPress site to receive product pages.
- Add a secure authentication method for WP calls (Application Passwords or JWT) and store credentials as repo secrets.
- Have the WP push return created page URLs and include them in notifications.

## Suggested Next Steps (concrete)
1. Add CSV-detection to the generator: write `artifacts/new_csvs.json` listing newly created/updated CSV filenames and human-friendly set names.
2. Update `.github/workflows/generate_csvs.yml` to read `artifacts/new_csvs.json` and, when non-empty, include blob/raw links to the CSVs in the Telegram notification.
3. Scaffold `scripts/push_cards_to_wp.py` that reads one CSV and demonstrates creating one `card` post (dry-run + verbose output). Test locally with a staging WP site.

## Where to Look
- CSVs: [csv_new/](csv_new/)
- Generator: [scripts/generate_csvs_from_repo.py](scripts/generate_csvs_from_repo.py)
- Workflow: [.github/workflows/generate_csvs.yml](.github/workflows/generate_csvs.yml)

If you want, I can implement step 1 now (have the generator produce `artifacts/new_csvs.json`) and then update the workflow to include CSV links in the Telegram message.
