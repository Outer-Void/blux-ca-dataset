# Platforms

Basic contributor setup notes for Android/Termux and a proot Debian fallback.

## Termux (native)
```bash
pkg update
pkg install -y git
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
apt-get install -y git
```
