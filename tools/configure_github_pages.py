"""Configure GitHub Pages with existing Git credentials, never logging a token."""
import json
import subprocess
import urllib.error
import urllib.request

REPO = 'ai-agent-orchestrator/explore-your-little-universe'


def main():
    response = subprocess.run(['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n', text=True,
        capture_output=True, check=True)
    credential = dict(line.split('=', 1) for line in response.stdout.splitlines() if '=' in line)
    token = credential.get('password')
    if not token:
        raise SystemExit('No existing GitHub credential available')
    headers = {'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'}
    base = 'https://api.github.com/repos/' + REPO + '/pages'
    def request(method, payload=None):
        req = urllib.request.Request(base, method=method, headers=headers,
            data=json.dumps(payload).encode() if payload is not None else None)
        with urllib.request.urlopen(req, timeout=30) as result:
            return json.load(result) if result.status != 204 else {}
    try:
        current = request('GET')
        print('Existing Pages:', current.get('html_url'), current.get('source'))
        if current.get('source', {}).get('branch') != 'gh-pages':
            # Do not replace an existing site's unrelated publishing source.
            raise SystemExit('Existing Pages source differs; no changes made')
        return
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise SystemExit(f'GitHub Pages check failed: HTTP {exc.code}') from None
    try:
        result = request('POST', {'source': {'branch': 'gh-pages', 'path': '/'},
                                  'build_type': 'legacy'})
        print('Created GitHub Pages:', result.get('html_url'))
    except urllib.error.HTTPError as exc:
        # Print only GitHub's high-level message, never request headers.
        message = json.load(exc).get('message', 'Request rejected')
        raise SystemExit(f'GitHub Pages setup failed: HTTP {exc.code}: {message}') from None


if __name__ == '__main__':
    main()
