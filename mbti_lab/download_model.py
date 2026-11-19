"""Download a pinned public model; verify its Hugging Face LFS SHA-256."""
import json
import urllib.request
from .embedding import MODEL_REPO, MODEL_REVISION, MODEL_FILE, MODEL_PATH, sha256


def main():
    metadata_url = f'https://huggingface.co/api/models/{MODEL_REPO}/revision/{MODEL_REVISION}?blobs=true'
    with urllib.request.urlopen(metadata_url, timeout=60) as response:
        metadata = json.load(response)
    item = next(x for x in metadata['siblings'] if x['rfilename'] == MODEL_FILE)
    expected = item['lfs']['sha256']
    if MODEL_PATH.is_file() and sha256(MODEL_PATH) == expected:
        print('Model already downloaded and verified')
        return
    MODEL_PATH.parent.mkdir(exist_ok=True)
    temporary = MODEL_PATH.with_suffix('.download')
    url = f'https://huggingface.co/{MODEL_REPO}/resolve/{MODEL_REVISION}/{MODEL_FILE}'
    print('Downloading pinned EmbeddingGemma 2 text model...', flush=True)
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as output:
        for block in iter(lambda: response.read(1024 * 1024), b''):
            output.write(block)
    if sha256(temporary) != expected:
        raise ValueError('Model checksum mismatch; not activating the download')
    temporary.replace(MODEL_PATH)
    print('PASS: model SHA-256 verified')


if __name__ == '__main__':
    main()
