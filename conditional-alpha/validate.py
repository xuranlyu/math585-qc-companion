"""Run the notebook cells locally and verify the finite-space identities."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')

root = Path(__file__).parent
nb = json.loads((root / 'research.ipynb').read_text())
scope = {}
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        exec(compile(''.join(cell['source']), f'notebook-cell-{i}', 'exec'), scope)

np, cm = scope['np'], scope['conditional_mean']
assert np.allclose(scope['m'], [1, 1, 5, 5])
assert np.allclose(scope['alpha'], [-2, -2, 2, 2])
assert np.allclose(list(scope['errors'].values()), [5, 1, 0])
assert np.allclose(cm([0, 2, 4, 6], [.1, .4, .2, .3], ['A', 'A', 'B', 'B']), [1.6, 1.6, 5.2, 5.2])
rng = np.random.default_rng(585)
for _ in range(100):
    x, p = rng.normal(size=8), rng.dirichlet(np.ones(8))
    groups = np.repeat(['A', 'B'], 4)
    m = cm(x, p, groups)
    residual, b = x - m, rng.normal()
    assert np.allclose(cm(residual, p, groups), 0, atol=1e-12)
    assert np.isclose(np.dot(p, (x-b)**2), np.dot(p, (m-b)**2) + np.dot(p, residual**2))
for invalid in ([0, .25, .25, .5], [.1, .1, .1, .1]):
    try:
        cm([0, 2, 4, 6], invalid, ['A', 'A', 'B', 'B'])
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid probabilities accepted')
scope['fig'].savefig(root / 'preview.png', dpi=150, bbox_inches='tight')
print('PASS: default outputs, unequal weights, 100 parameter cases, invalid probabilities.')
