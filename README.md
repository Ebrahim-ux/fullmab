# Scientific Calculator

A full-stack scientific calculator built with Flask, deployed to [Fly.io](https://fly.io) via GitHub Actions.

## Features

- Basic and scientific operations: `+ - * / ** sqrt sin cos tan asin acos atan sinh cosh tanh log ln exp abs factorial`, constants `pi` and `e`
- Expression history (click a past result to reuse it)
- Full keyboard input support (type expressions directly, Enter to evaluate, Esc to clear)
- Memory functions: `MC` / `MR` / `M+` / `M-`
- Expressions are evaluated server-side with a restricted AST walker (`src/sciCalc/evaluator.py`) — no `eval()`, no arbitrary code execution

## Project layout

```
src/sciCalc/
  app.py            Flask app factory + routes
  evaluator.py       Safe expression evaluator
  templates/          index.html
  static/css/         style.css
  static/js/          calculator.js
tests/                 pytest suite
```

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

export PYTHONPATH=src
flask --app sciCalc.app run --debug
```

Visit http://127.0.0.1:5000

## Quality checks

```bash
ruff check .
mypy src
pytest
```

## Deployment (Fly.io via GitHub Actions)

Every push to `master` runs lint/typecheck/test, then deploys to Fly.io if they pass.

### One-time setup

1. Install `flyctl` and run `fly auth login`.
2. From the project root: `fly launch --no-deploy` (it will detect `fly.toml`; keep the existing app name `sci-calc-fullmab` or update `fly.toml` if you choose a different one).
3. Generate a deploy token: `fly tokens create deploy -x 999999h`
4. In the GitHub repo, go to **Settings → Secrets and variables → Actions** and add a secret named `FLY_API_TOKEN` with that token's value.
5. Push to `master` — the `deploy` job in `.github/workflows/ci.yml` will build the Docker image and deploy it.

### Manual deploy (optional)

```bash
fly deploy
```
