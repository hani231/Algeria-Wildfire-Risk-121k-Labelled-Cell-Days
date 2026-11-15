import json
import pytest
from src.siad03_extensions.data import ROOT, load_development, new_output


def test_development_and_leakage(tmp_path):
    tr, va, features, report = load_development()
    assert len(tr) == 104979 and len(va) == 8423
    assert tr.year.max() < va.year.min() and report['test_evaluated'] is False
    config = json.loads((ROOT / 'results/protocole_propose.json').read_text())
    config['features'].append('n_detections')
    p = tmp_path / 'bad.json'; p.write_text(json.dumps(config))
    with pytest.raises(ValueError, match='fuite'):
        load_development(protocol=p)


def test_output_never_overwrites(tmp_path):
    path = new_output(tmp_path / 'run')
    (path / 'precious.txt').write_text('keep')
    with pytest.raises(FileExistsError):
        new_output(path)
    assert (path / 'precious.txt').read_text() == 'keep'
