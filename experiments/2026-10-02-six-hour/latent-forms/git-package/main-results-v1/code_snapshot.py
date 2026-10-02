"""Losslessly package the oversized frozen JSON using deterministic gzip chunks."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import zlib

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-forms'
CHUNK = 16 * 1024 * 1024


def digest_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def reconstruction(manifest, destination=None):
    metadata = json.loads(manifest.read_text(encoding='utf-8'))
    hasher = hashlib.sha256()
    total = 0
    handle = None
    if destination is not None:
        if destination.exists():
            raise RuntimeError('Refuse to overwrite an existing file.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        handle = destination.open('xb')
    try:
        for item in metadata['chunks']:
            compressed = (manifest.parent / item['file']).read_bytes()
            assert digest_bytes(compressed) == item['compressed_sha256']
            payload = gzip.decompress(compressed)
            assert len(payload) == item['uncompressed_bytes'] and digest_bytes(payload) == item['uncompressed_sha256']
            hasher.update(payload)
            total += len(payload)
            if handle is not None:
                handle.write(payload)
        assert total == metadata['original_bytes'] and hasher.hexdigest() == metadata['original_sha256']
    finally:
        if handle is not None:
            handle.close()
    return dict(reconstructed_bytes=total, reconstructed_sha256=hasher.hexdigest(), source_match=True)


def pack():
    original = BASE / 'main-v1/results.json'
    package = BASE / 'git-package/main-results-v1'
    if package.exists():
        raise RuntimeError('Preserve prior package.')
    package.mkdir(parents=True)
    original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    chunks = []
    with original.open('rb') as stream:
        index = 0
        while payload := stream.read(CHUNK):
            compressed = gzip.compress(payload, compresslevel=6, mtime=0)
            name = f'chunk-{index:04d}.json.gz'
            (package / name).write_bytes(compressed)
            chunks.append(dict(file=name, uncompressed_bytes=len(payload), uncompressed_sha256=digest_bytes(payload),
                               compressed_bytes=len(compressed), compressed_sha256=digest_bytes(compressed)))
            index += 1
    metadata = dict(format='indus-research-gzip-byte-chunks-v1', original_path=original.relative_to(ROOT).as_posix(),
                    original_bytes=original.stat().st_size, original_sha256=original_hash, chunk_uncompressed_limit=CHUNK,
                    compression='gzip, level 6, mtime 0; each byte chunk compressed independently',
                    python_version=platform.python_version(), zlib_version=zlib.ZLIB_RUNTIME_VERSION, chunks=chunks)
    manifest = package / 'manifest.json'
    manifest.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    proof = reconstruction(manifest)
    proof['original_bytes_preserved'] = hashlib.sha256(original.read_bytes()).hexdigest() == original_hash
    proof['all_chunks_below_100_MB'] = all(item['compressed_bytes'] < 100_000_000 for item in chunks)
    proof['total_compressed_bytes'] = sum(item['compressed_bytes'] for item in chunks)
    (package / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    (package / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(chunks=len(chunks), **proof)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['pack', 'verify', 'reconstruct'])
    parser.add_argument('--manifest', default=str(BASE / 'git-package/main-results-v1/manifest.json'))
    parser.add_argument('--destination')
    args = parser.parse_args()
    if args.mode == 'pack':
        pack()
    else:
        if args.mode == 'reconstruct' and not args.destination:
            parser.error('Reconstruction needs an explicit new destination.')
        print(json.dumps(reconstruction(Path(args.manifest), Path(args.destination) if args.destination else None)))
