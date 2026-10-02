# Reconstruct the frozen result

The manifest describes eight independently gzipped byte chunks of the original JSON. Their order is the array order in [manifest.json](manifest.json). The uncompressed stream contains 132,193,239 bytes and has SHA-256 `5e1a087288ee3d9f1978549a262aac802a970468e313bcb8878f0a56e24be6e6`. [Verification](verification.json) records a complete streamed reconstruction with that hash. The original remains local at `experiments/2026-10-02-six-hour/latent-forms/main-v1/results.json`.

From the repository root, verify the package without writing a reconstructed file:

```powershell
python src/six_hour/latent_forms_package.py verify
```

On a clone that lacks the local original, restore it to the analysis path:

```powershell
python src/six_hour/latent_forms_package.py reconstruct --destination experiments/2026-10-02-six-hour/latent-forms/main-v1/results.json
```

The helper refuses to overwrite an existing destination. It checks every compressed hash, every decompressed chunk hash and the complete reconstructed hash. Python's standard library is sufficient. The [frozen helper](code_snapshot.py) records the packaging implementation; the repository helper has the standard workspace path defaults.

Chunk creation used gzip level 6 with `mtime=0`, Python 3.13.5 and zlib 1.3.1, as recorded in the manifest. Each uncompressed chunk is at most 16 MiB, and each compressed file is well below GitHub's limit. Binary reconstruction preserves the original JSON whitespace, ordering and line endings.
