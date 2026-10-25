# Platforms

Contributor setup notes for Android/Termux and a proot Debian fallback.

## Termux (native)
```bash
pkg update
pkg install python3 git
python -m pip install --upgrade pip
```

## Termux + proot Debian inside Debian shell (optional)
```bash
pkg update
pkg install proot-distro
proot-distro install debian
proot-distro login debian
```

Inside Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip git
python -m pip install --upgrade pip
```

## Running checks
```bash
python scripts/validate_dataset.py
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro
python scripts/export_jsonl.py --include-archives --write-sha256
```

## Running directly against the local engine
`verify_fixtures.py` can verify directly against a real local `blux-ca` checkout by pointing `--engine-root` at the repo. The verifier generates temporary engine-compatible fixture goals and then runs the supported CLI entrypoint: `python -m blux_ca accept --fixtures <generated-bridge-dir> --out <temp-run-dir> [--profile <id>]`.
When `--profile` is omitted, verification accepts an omitted acceptance-report `profile_id` or `"default"` to match live engine behavior.

Canonical command:
```bash
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro
```

Do not document or rely on unsupported engine flags such as `--policy-pack` on the engine CLI or `--out-dir`; the current engine uses `--out`.

Optional matrix extensions:
```bash
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-mini
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro --profile cpu
```

Fallback without a local engine checkout:
```bash
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro
```

Always use `python -m pip`, never raw `pip`.
