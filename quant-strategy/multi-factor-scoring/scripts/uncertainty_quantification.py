"""
Distribution-Free Uncertainty Quantification for Time Series (arXiv:2607.06690)
"tsbootstrap: Distribution-Free Uncertainty Quantification and Conformal
 Prediction for Time Series" — Gilda (2026)

Why this module exists
----------------------
Point forecasts (factor returns, volatility, composite scores) are not enough for
risk control. You need CALIBRATED intervals around each signal so you can size
positions by confidence and set risk-control thresholds. But finance streams
violate the exchangeability / IID assumptions that split-conformal prediction and
the ordinary bootstrap rely on — and both UNDERCOVER on autoregressive data.

Key empirical findings embedded here (from the paper):
- The IID bootstrap undercovers SHARPLY under serial dependence.
- Dependence-aware resampling (block / sieve) restores coverage close to nominal;
  the sieve is nearest to nominal under short-memory linear dependence.
- Conformal calibration supplies a finite-sample coverage guarantee; the adaptive
  time-series variants (EnbPI / ACI / NexCP / AgACI) keep coverage on drifting
  streams.

Practical takeaway for WQUANT's multi-factor signals:
  NEVER quantify a serially-dependent signal with an IID bootstrap. Use a MOVING
  BLOCK bootstrap (dependence-aware) for confidence intervals and split/block
  conformal for prediction intervals. Then translate interval width into a
  position-confidence multiplier and a risk gate.

Design (matches the graceful-fallback pattern already used by volatility_forecaster):
  - PRIMARY path: `tsbootstrap` (MIT, v0.6.1) generates dependence-aware replicates
    (MovingBlock, block_length="auto" via Politis-White). We compute the statistic
    and percentile CI ourselves from `result.values()` — relying only on the stable
    documented API. Install with `pip install tsbootstrap`.
  - FALLBACK path: a self-contained pure-numpy moving-block bootstrap + split
    conformal quantile. Works with numpy alone; sets `backend="numpy-fallback"`.

Components:
  - moving_block_bootstrap : dependence-aware resampler (numpy fallback)
  - bootstrap_ci           : distribution-free CI for any statistic
  - conformal_halfwidth    : split-conformal prediction half-width (finite-sample)
  - signal_confidence_interval : CI on the mean of a signal series
  - position_confidence    : interval width -> [floor, 1] sizing multiplier
  - risk_gate              : significance / risk-threshold decision from the CI
  - quantify_signal        : one-call helper returning the full UQ bundle
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


# --------------------------------------------------------------------------- #
# Block-length selection (Politis-White style, simplified)
# --------------------------------------------------------------------------- #
def auto_block_length(x):
    """
    Pick a block length for block bootstrap on dependent data.

    Uses the first lag at which the sample autocorrelation drops below the
    2/sqrt(n) significance band, then applies the common n^(1/3) growth floor.
    A block that spans the memory of the series is what restores coverage that
    the IID bootstrap loses (arXiv:2607.06690).
    """
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = len(x)
    if n < 8:
        return 1
    x = x - x.mean()
    denom = np.dot(x, x)
    if denom <= 0:
        return max(1, int(round(n ** (1.0 / 3.0))))
    band = 2.0 / np.sqrt(n)
    first_insig = 1
    for lag in range(1, min(n // 2, 50)):
        ac = np.dot(x[:-lag], x[lag:]) / denom
        if abs(ac) < band:
            first_insig = lag
            break
        first_insig = lag + 1
    floor = int(round(n ** (1.0 / 3.0)))
    return int(max(1, min(n // 2, max(first_insig, floor))))


# --------------------------------------------------------------------------- #
# Moving-block bootstrap (dependence-aware) — pure-numpy fallback
# --------------------------------------------------------------------------- #
def moving_block_bootstrap(x, n_bootstraps=999, block_length=None, random_state=0):
    """
    Generate moving-block bootstrap replicates of a 1-D series.

    Overlapping blocks of contiguous observations are resampled with replacement
    and concatenated to length n. This preserves short-range dependence, unlike
    the IID bootstrap which shuffles it away and undercovers.

    Returns:
        np.ndarray of shape (n_bootstraps, n)
    """
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = len(x)
    if n == 0:
        return np.empty((0, 0))
    L = int(block_length) if block_length else auto_block_length(x)
    L = max(1, min(L, n))
    rng = np.random.default_rng(random_state)
    n_blocks = int(np.ceil(n / L))
    max_start = n - L  # inclusive
    out = np.empty((n_bootstraps, n), dtype=float)
    for b in range(n_bootstraps):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        rep = np.concatenate([x[s:s + L] for s in starts])[:n]
        out[b] = rep
    return out


def _tsbootstrap_replicates(x, n_bootstraps, random_state):
    """
    PRIMARY path: use tsbootstrap's dependence-aware MovingBlock resampler.
    Returns (replicates, backend_name) or (None, None) if unavailable.
    Only the stable documented API (`bootstrap` + `.values()`) is used.
    """
    try:
        from tsbootstrap import bootstrap, MovingBlock
    except Exception:
        return None, None
    try:
        res = bootstrap(
            np.asarray(x, dtype=float),
            method=MovingBlock(block_length="auto"),
            n_bootstraps=int(n_bootstraps),
            random_state=int(random_state),
        )
        vals = np.asarray(res.values(), dtype=float)
        if vals.ndim == 3:            # (B, n, 1) -> (B, n)
            vals = vals[:, :, 0]
        return vals, "tsbootstrap-movingblock"
    except Exception as e:
        warnings.warn(f"tsbootstrap path failed ({e}); using numpy moving-block fallback.")
        return None, None


# --------------------------------------------------------------------------- #
# Distribution-free confidence interval for a statistic
# --------------------------------------------------------------------------- #
def bootstrap_ci(x, statistic=np.mean, alpha=0.10, n_bootstraps=999,
                 block_length=None, random_state=0):
    """
    Dependence-aware bootstrap CI for `statistic` at level (1 - alpha).

    Tries tsbootstrap MovingBlock first, falls back to the numpy moving-block
    resampler. The statistic and percentile interval are always computed here,
    so the result is correct regardless of which backend produced the replicates.

    Returns:
        dict(point, lower, upper, width, rel_width, alpha, coverage, backend, n_boot)
    """
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = len(x)
    point = float(statistic(x)) if n else 0.0

    reps, backend = _tsbootstrap_replicates(x, n_bootstraps, random_state)
    if reps is None:
        reps = moving_block_bootstrap(x, n_bootstraps, block_length, random_state)
        backend = "numpy-fallback"

    if reps.size == 0:
        return dict(point=point, lower=point, upper=point, width=0.0,
                    rel_width=0.0, alpha=alpha, coverage=1 - alpha,
                    backend=backend, n_boot=0)

    stats = np.array([statistic(r) for r in reps], dtype=float)
    lo = float(np.percentile(stats, 100 * (alpha / 2)))
    hi = float(np.percentile(stats, 100 * (1 - alpha / 2)))
    width = hi - lo
    scale = abs(point) if abs(point) > 1e-12 else (np.std(x) + 1e-12)
    return dict(point=point, lower=lo, upper=hi, width=width,
                rel_width=float(width / scale), alpha=alpha,
                coverage=1 - alpha, backend=backend, n_boot=len(reps))


# --------------------------------------------------------------------------- #
# Split-conformal prediction half-width (finite-sample, distribution-free)
# --------------------------------------------------------------------------- #
def conformal_halfwidth(residuals, alpha=0.10):
    """
    Split-conformal half-width from calibration residuals.

    hw = Quantile_{ceil((n+1)(1-alpha))/n} ( |residuals| )

    Under exchangeability this yields >= (1 - alpha) marginal coverage in finite
    samples. On dependent streams coverage degrades gracefully; use block/adaptive
    conformal (EnbPI/ACI via tsbootstrap.uq) when strict coverage is needed.

    Returns:
        float half-width (>= 0). A forecast interval is [pred - hw, pred + hw].
    """
    r = np.abs(np.asarray(pd.Series(residuals).dropna(), dtype=float))
    n = len(r)
    if n == 0:
        return 0.0
    q_level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(r, q_level))


# --------------------------------------------------------------------------- #
# Signal-level UQ helpers
# --------------------------------------------------------------------------- #
def signal_confidence_interval(signal, alpha=0.10, statistic=np.mean,
                               n_bootstraps=999, random_state=0):
    """
    Confidence interval on a signal series (e.g. factor returns, forecasted RV).

    Thin wrapper over bootstrap_ci with the dependence-aware default.
    """
    return bootstrap_ci(signal, statistic=statistic, alpha=alpha,
                        n_bootstraps=n_bootstraps, random_state=random_state)


def position_confidence(rel_width, floor=0.30, k=2.0):
    """
    Map a relative CI width to a position-sizing confidence multiplier in [floor, 1].

        confidence = clip( 1 / (1 + k * rel_width), floor, 1 )

    Narrow interval (signal precise) -> confidence near 1 -> full size.
    Wide interval  (signal uncertain) -> confidence near `floor` -> shrink size.
    """
    rel_width = max(0.0, float(rel_width))
    conf = 1.0 / (1.0 + k * rel_width)
    return float(np.clip(conf, floor, 1.0))


def risk_gate(ci, direction="long", require_significant=True):
    """
    Risk-control decision from a confidence interval on an EXPECTED-RETURN signal.

    A signal whose CI straddles zero is statistically indistinguishable from no
    edge — the classic risk trap of trading a point estimate that is inside the
    noise band. This gate flags that and returns a scaling decision.

    Args:
        ci: dict from bootstrap_ci / signal_confidence_interval (return units)
        direction: 'long' (edge if lower > 0) or 'short' (edge if upper < 0)
        require_significant: if True, veto when the CI straddles zero

    Returns:
        dict(significant, veto, scale, reason)
          - significant: CI excludes zero in the trade direction
          - veto: True -> do not take/keep the position
          - scale: suggested position-size multiplier in [0, 1]
    """
    lo, hi = ci['lower'], ci['upper']
    if direction == "long":
        significant = lo > 0
    else:
        significant = hi < 0
    straddles_zero = (lo <= 0 <= hi)
    veto = require_significant and not significant
    scale = position_confidence(ci.get('rel_width', 0.0))
    if veto:
        scale = 0.0
    reason = ("edge confirmed (CI excludes 0)" if significant
              else "no edge: CI straddles 0" if straddles_zero
              else "edge against direction")
    return dict(significant=bool(significant), veto=bool(veto),
                scale=float(scale), reason=reason)


def quantify_signal(signal, alpha=0.10, direction="long", statistic=np.mean,
                    n_bootstraps=999, random_state=0, require_significant=False):
    """
    One-call UQ bundle for a signal series.

    Returns:
        dict with the CI, position-confidence multiplier, and risk gate.
    """
    ci = signal_confidence_interval(signal, alpha=alpha, statistic=statistic,
                                    n_bootstraps=n_bootstraps, random_state=random_state)
    conf = position_confidence(ci['rel_width'])
    gate = risk_gate(ci, direction=direction, require_significant=require_significant)
    return dict(ci=ci, confidence=conf, risk_gate=gate)


if __name__ == "__main__":
    # Smoke test with a serially-dependent AR(1) series (no external deps).
    rng = np.random.default_rng(0)
    n, phi = 250, 0.6
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + rng.standard_normal()
    daily_ret = 0.0004 + 0.01 * x  # small positive-drift return series

    print("auto_block_length:", auto_block_length(daily_ret))

    ci = signal_confidence_interval(daily_ret, alpha=0.10)
    print("Mean-return 90% CI:", round(ci['point'], 5),
          "[", round(ci['lower'], 5), ",", round(ci['upper'], 5), "]",
          "backend:", ci['backend'])

    conf = position_confidence(ci['rel_width'])
    gate = risk_gate(ci, direction="long", require_significant=True)
    print("Position confidence:", round(conf, 3))
    print("Risk gate:", gate)

    # Conformal half-width from synthetic calibration residuals
    resid = 0.01 * rng.standard_normal(200)
    hw = conformal_halfwidth(resid, alpha=0.10)
    print("Conformal 90% half-width:", round(hw, 5))

    bundle = quantify_signal(daily_ret, alpha=0.10, direction="long")
    print("quantify_signal confidence:", round(bundle['confidence'], 3),
          "veto:", bundle['risk_gate']['veto'])
    print("SMOKE TEST OK")
