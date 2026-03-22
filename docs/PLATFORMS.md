# Platforms

Basic contributor setup notes for Android/Termux and a proot Debian fallback.

## Termux (native)
```bash
pkg update
pkg install python3 git
python -m pip install --upgrade pip
```

## Termux + proot Debian inside Debian (optional)
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

## Running directly against the local engine
`verify_fixtures.py` can invoke a local `blux-ca` command if you provide a command template. Available placeholders are `{fixture}`, `{goal}`, `{out_dir}`, `{model_version}`, `{policy_pack}`, and `{profile}`.

Example:
```bash
python scripts/verify_fixtures.py \
  --engine-cmd 'python -m blux_ca.run --goal {goal} --out-dir {out_dir} --policy-pack {policy_pack} --profile {profile}' \
  --policy-pack cA-pro
```

Use `python -m pip`, never raw `pip`.
