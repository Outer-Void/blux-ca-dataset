# Platforms

Basic contributor setup notes for Android/Termux and a proot Debian fallback.

## Termux (native)
```bash
pkg update
pkg install -y git python
```

## Termux + proot Debian (optional)
```bash
pkg update
pkg install -y proot-distro
proot-distro install debian
proot-distro login debian
```

Inside Debian:
```bash
apt-get update
apt-get install -y git python3
```

## Running checks
```bash
./scripts/validate_dataset.py
./scripts/verify_fixtures.py --actual-root runs --policy-pack default
```
