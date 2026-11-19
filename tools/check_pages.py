"""Read/request a Pages build using existing Git authentication in memory."""
import argparse
import json
import subprocess
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    result = subprocess.run(['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True)
    values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    headers = {'Authorization': 'Bearer ' + values['password'],
               'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    endpoint = 'https://api.github.com/repos/ai-agent-orchestrator/explore-your-little-universe/pages/builds'
    request = urllib.request.Request(endpoint if args.build else endpoint + '/latest',
        method='POST' if args.build else 'GET', headers=headers,
        data=b'{}' if args.build else None)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
        print(json.dumps({key: data.get(key) for key in ['status', 'error', 'commit', 'created_at', 'updated_at']}, ensure_ascii=False))
    except urllib.error.HTTPError as exc:
        data = json.load(exc)
        raise SystemExit(f'Pages HTTP {exc.code}: {data.get("message")}') from None


if __name__ == '__main__':
    main()
