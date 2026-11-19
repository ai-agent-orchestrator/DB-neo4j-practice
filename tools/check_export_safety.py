"""Check staged sources and built text assets without printing secret values."""
from pathlib import Path
import subprocess
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent


def main():
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    if any(Path(name).name.startswith('.env') for name in tracked if name):
        raise SystemExit('Tracked env file found')
    secrets = []
    for settings in ROOT.glob('.env*'):
        if settings.is_file():
            for key, value in dotenv_values(settings).items():
                if value and len(value) >= 8 and any(word in key.upper() for word in ['PASSWORD', 'KEY', 'TOKEN', 'SECRET']):
                    secrets.append(value.encode())
    files = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM', '-z'], cwd=ROOT).decode().split('\0')
    inspected = 0
    for name in files:
        if not name:
            continue
        content = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        if any(secret in content for secret in secrets):
            raise SystemExit('Credential value found in staged file: ' + name)
        inspected += 1
    for path in (ROOT / 'frontend/dist').rglob('*'):
        if path.is_file() and path.suffix in {'.js', '.json', '.html', '.css'}:
            if any(secret in path.read_bytes() for secret in secrets):
                raise SystemExit('Credential value found in built assets')
    print(f'PASS: no tracked env files; {inspected} staged files and built text assets checked')


if __name__ == '__main__':
    main()
