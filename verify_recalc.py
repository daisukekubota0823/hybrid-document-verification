# Independent recalculation: pandas-based, no shared code with evaluate.py
import pandas as pd
r = pd.read_csv('results_raw.csv')
assert len(r) == 300 and r['pred'].isin(['UP','DOWN','NO_CHANGE']).all()
def kappa(df):
    labs = ['UP','DOWN','NO_CHANGE']
    po = (df['pred'] == df['truth']).mean()
    pe = sum((df['truth']==l).mean() * (df['pred']==l).mean() for l in labs)
    return po, (po-pe)/(1-pe)
po, k = kappa(r); print(f"ALL: agree={po:.4f} kappa={k:.4f}")
auto = r[r['band'] != 'borderline']
po2, k2 = kappa(auto); print(f"AUTO: agree={po2:.4f} kappa={k2:.4f} n={len(auto)}")
pos = r[r['truth'].isin(['UP','DOWN'])]
print(f"miss={ (pos['pred']!=pos['truth']).mean():.4f}")
neg_clear = r[(r['truth']=='NO_CHANGE') & (r['band']=='clear')]
print(f"FD clear={ neg_clear['pred'].isin(['UP','DOWN']).mean():.4f} (n={len(neg_clear)})")
bord = r[r['band']=='borderline']
print(f"borderline agree={ (bord['pred']==bord['truth']).mean():.4f} FD={ bord['pred'].isin(['UP','DOWN']).mean():.4f}")
