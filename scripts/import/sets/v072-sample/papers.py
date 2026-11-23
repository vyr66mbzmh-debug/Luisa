"""v0.72 reference set: the five Edexcel Sample Assessment Material papers (GitHub #124, #128).

qp/ms are paths relative to the private source folder (key pastPaperSource); qpsha/mssha are the owner copies' SHA-256
(also recorded in content/exams/pilot-metadata.json). ORDER is the metadata order of every imported paper.
"""
S = 'Sample Papers/'
def P(code, title, session, date, series, minutes, nq, total, qp, ms, qpsha, mssha, **kw):
    return dict(code=code, title=title, session=session, date=date, series=series, minutes=minutes, nq=nq, total=total, qp=qp, ms=ms,
                qpsha=qpsha, mssha=mssha, msstart=None, msend=None, **kw)
PAPERS = {
 'edexcel-9ma0-01-sample': P('9MA0/01', 'Pure Mathematics 1', 'Sample', None, None, 120, 15, 100, S + 'Sample QP (Pure 1).pdf', S + 'Sample MS (Pure 1).pdf',
   'dfb3d5e84c9642953847ff8d664c483246e84fa0c0600009d973a0923c3fc1b8', '0aea6a31199c29c177d292f11516d3e1640bebe1fa837863be646454f3dfdab3', ref='S54259A', msfoot=778),
 'edexcel-9ma0-02-sample': P('9MA0/02', 'Pure Mathematics 2', 'Sample', None, None, 120, 16, 100, S + 'Sample QP (Pure 2).pdf', S + 'Sample MS (Pure 2).pdf',
   '2bc25b62b1b821258e366a6298e3336d36d7d6dd2deecf0134f1bf220cad7e01', 'fc838ce639b8701c80f0e11294418c5d8d039aff492003454712300c251d63bb', ref='S54260A', msfoot=778),
 'edexcel-9ma0-03-sample': P('9MA0/03', 'Statistics and Mechanics', 'Sample', None, None, 120, 10, 100, S + 'Sample QP (Stats and Mech).pdf', S + 'Sample MS (Statis and Mech).pdf',
   'b22c0b36290c4043804684f5976ce7e752370f5e703bbe63f13efaafbf7915a1', '702bd8368771fbe442f550ce7a92309af63564a97a4c615a537d3b6f947b71e7', ref='S54261A', msfoot=778),
 'edexcel-9fm0-01-sample': P('9FM0/01', 'Core Pure Mathematics 1', 'Sample', None, None, 90, 9, 75, S + 'Sample QP (Core Pure 1).pdf', S + 'Sample MS (Core Pure 1).pdf',
   'c52ca71952d71189b1dae9e601d573333155168fb827bec9bda78eb610696d61', '75adbba38a00f67c753bc0580382d0dace43c91e8db07f7044c215f9fdd213c0', ref='S54438A', msfoot=778),
 'edexcel-9fm0-02-sample': P('9FM0/02', 'Core Pure Mathematics 2', 'Sample', None, None, 90, 7, 75, S + 'Sample QP (Core Pure 2).pdf', S + 'Sample MS (Core Pure 2).pdf',
   '912b1f5d5f9327a90b892e06fa8bd245799003d4ca7bdb535f991d9baf0a8c36', '8737ed77a9a8dbc1b8efe31f2b2a07b2e46366b429c71a480169b692eb09f1d7', ref='S54439A', msfoot=778),
}
PAPERS['edexcel-9ma0-01-sample'].update(msstart=[[1, 88], 2, 3, [3, 456], 4, 5, 6, 7, 8, 9, 11, 12, 14, 16, 18], msend=18)

_B = 'https://pmt.physicsandmathstutor.com/download/Maths/A-level/Papers/'
# 23 Nov 2026: PMT 'Sample' QPs are byte-identical to the owner files; each PMT MS has the same pages and text plus a 'PMT' page mark (both hashes kept).
_U = {
 'edexcel-9ma0-01-sample': ('Edexcel/Paper-1/QP/Sample%20QP.pdf', 'Edexcel/Paper-1/MS/Sample%20MS.pdf', 'dfb3d5e84c9642953847ff8d664c483246e84fa0c0600009d973a0923c3fc1b8', '7f3b6cf3783811e9d9a5073a7ce7447e62ee9cf87c504637f279b96d13b2cf40'),
 'edexcel-9ma0-02-sample': ('Edexcel/Paper-2/QP/Sample%20QP.pdf', 'Edexcel/Paper-2/MS/Sample%20MS.pdf', '2bc25b62b1b821258e366a6298e3336d36d7d6dd2deecf0134f1bf220cad7e01', 'e8050f2c4329d8efa98bb4e8153fff85427b8fd97d559d863dde874598c1e980'),
 'edexcel-9ma0-03-sample': ('Edexcel/Paper-3/QP/Sample%20QP.pdf', 'Edexcel/Paper-3/MS/Sample%20MS.pdf', 'b22c0b36290c4043804684f5976ce7e752370f5e703bbe63f13efaafbf7915a1', 'b61fcd32f02714e36f3284b238eb87862018f218220ce3dc02e137aad44b0088'),
 'edexcel-9fm0-01-sample': ('Edexcel-Further/Core-Pure-1/QP/Sample%20QP.pdf', 'Edexcel-Further/Core-Pure-1/MS/Sample%20MS.pdf', 'c52ca71952d71189b1dae9e601d573333155168fb827bec9bda78eb610696d61', 'c41ac1442448f07d12538911472eee972705b6b405ae43324727cfe88f3658e7'),
 'edexcel-9fm0-02-sample': ('Edexcel-Further/Core-Pure-2/QP/Sample%20QP.pdf', 'Edexcel-Further/Core-Pure-2/MS/Sample%20MS.pdf', '912b1f5d5f9327a90b892e06fa8bd245799003d4ca7bdb535f991d9baf0a8c36', '1ec14b4128b24719c93612ad1fc069d00f326b3f5952126114a924acacd6c33e'),
}
for _k, (_q, _m, _hq, _hm) in _U.items():
    PAPERS[_k].update(qpurl=_B + _q, msurl=_B + _m, idxqp=_hq, idxms=_hm)
PAPERS['edexcel-9ma0-02-sample'].update(msstart=[[1, 86], [1, 321], 2, 3, 4, 5, 6, 7, 8, [8, 481], 9, 10, 11, 12, 13, 15], msend=16)
PAPERS['edexcel-9ma0-03-sample'].update(msstart=[[1, 92], 3, 4, 6, 7, 8, 9, 10, 11, 13], msend=14)
PAPERS['edexcel-9fm0-01-sample'].update(msstart=[[1, 90], 3, 4, 5, 6, 7, 8, 9, 10], msend=11)
PAPERS['edexcel-9fm0-02-sample'].update(msstart=[[1, 104], 2, 3, 5, 6, 7, 10], msend=11)

# Metadata order: June sessions newest first in code order, then November/October, then the undated Sample papers.
_S = ('9ma0-01', '9ma0-02', '9ma0-32', '9ma0-31', '9fm0-01', '9fm0-02')
ORDER = ([f'edexcel-{c}-{y}-june' for y in (2025, 2024, 2023) for c in _S]
         + ['edexcel-9fm0-01-2021-november', 'edexcel-9fm0-02-2021-november']
         + [f'edexcel-{c}-2021-october' for c in _S[:4]] + [f'edexcel-{c}-2020-october' for c in _S]
         + [f'edexcel-{c}-2019-june' for c in _S] + ['edexcel-9ma0-01-2018-june', 'edexcel-9ma0-02-2018-june', 'edexcel-9ma0-03-2018-june']
         + ['edexcel-9fm0-01-sample', 'edexcel-9fm0-02-sample', 'edexcel-9ma0-01-sample', 'edexcel-9ma0-02-sample', 'edexcel-9ma0-03-sample'])
