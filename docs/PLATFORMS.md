# Platforms

Basic contributor setup notes for Android/Termux and a proot Debian fallback.

## Termux (native)
```bash
pkg update
pkg install python3 git
python -m pip install --upgrade pip
```

## Termux + proot Debian (optional)
```bash
pkg update
pkg install proot-distro
proot-distro install debian
proot-distro login debian
```

Inside Debian:
```bash
sudo apt update
sudo apt install python3 git
python -m pip install --upgrade pip
```

## Running checks
```bash
python scripts/validate_dataset.py
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-mini
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro --profile cpu
```
