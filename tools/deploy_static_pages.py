"""Publish only built public assets to a new generated GitHub Pages branch."""
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parent.parent
REMOTE = 'https://github.com/ai-agent-orchestrator/explore-your-little-universe.git'


def main():
    source = ROOT / 'frontend' / 'dist'
    if not (source / 'index.html').is_file():
        raise SystemExit('Run npm run build in frontend first')
    target = ROOT.parent / 'tmp' / ('universe-pages-' + uuid.uuid4().hex[:10])
    target.mkdir(parents=True)
    subprocess.run(['git', 'init', '--initial-branch=gh-pages', str(target)], check=True)
    subprocess.run(['git', '-C', str(target), 'remote', 'add', 'origin', REMOTE], check=True)
    # Refuse an accidental overwrite. Updates can use the regular gh-pages checkout.
    existing = subprocess.run(['git', '-C', str(target), 'ls-remote', '--heads', 'origin', 'gh-pages'],
                              check=True, text=True, capture_output=True)
    if existing.stdout.strip():
        raise SystemExit('gh-pages already exists; refused to replace it')
    shutil.copytree(source, target, dirs_exist_ok=True)
    (target / '.nojekyll').touch()
    (target / '.playground-generated').write_text('Explore Your Little Universe\n', encoding='utf-8')
    subprocess.run(['git', '-C', str(target), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(target), 'commit', '-m', 'Publish Explore Your Little Universe static app'], check=True)
    subprocess.run(['git', '-C', str(target), 'push', '-u', 'origin', 'gh-pages'], check=True)
    print('Published generated static assets to gh-pages')


if __name__ == '__main__':
    main()
