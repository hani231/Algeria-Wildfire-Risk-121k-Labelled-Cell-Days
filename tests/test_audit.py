"""Exercise audit CLI outputs and preservation of the raw input."""
import hashlib
import json
import subprocess
import sys


def test_audit_cli_is_reproducible_and_preserves_input(small_data, tmp_path):
    source = tmp_path / 'raw.csv'
    small_data.to_csv(source, index=False)
    original = source.read_bytes()
    output = tmp_path / 'audit'
    command = [sys.executable, '-m', 'src.audit_data', '--data', str(source),
               '--output', str(output)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    first = {p.name: p.read_bytes() for p in output.iterdir()}
    report = json.loads(first['qualite.json'])
    assert report['sha256_brut'] == hashlib.sha256(original).hexdigest()
    assert report['lignes_apres'] == len(small_data)
    assert report['effectifs_train'] == {
        str(k): int(v) for k, v in
        small_data.loc[small_data.split.eq('train'), 'label'].value_counts().items()
    }
    assert 'colonnes.csv' in first
    subprocess.run(command, check=True, capture_output=True, text=True)
    assert {p.name: p.read_bytes() for p in output.iterdir()} == first
    assert source.read_bytes() == original
