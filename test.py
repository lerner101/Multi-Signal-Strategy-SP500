# 1) Are there any signals at all?
from VolatilityBreakoutStrategy import VolatilityBreakoutStrategy  # adjust import
vb = VolatilityBreakoutStrategy()
S = vb.compute_signals(P)                # Raw (unshifted)
print("Total nonzero signals:", S.ne(0).sum().sum())
print(S["UAL"].value_counts())           # any ±1s for UAL?

# 2) Inspect the inputs for UAL
rets  = P["UAL"].pct_change()
vol20 = rets.rolling(20, min_periods=20).std()

df_dbg = pd.DataFrame({
    "ret": rets,
    "vol20": vol20,
    "buy": (rets >  vol20).astype(int),
    "sell":(rets < -vol20).astype(int),
})
print(df_dbg.dropna().tail(25))
