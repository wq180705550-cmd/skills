"""
Volatility Forecasting Module (arXiv:2607.05291)
"Forecasting Realized Volatility with Time Series Foundation Models: A Comparison
 with Econometric Benchmarks" — Brini (2026)

Key empirical findings embedded in this module:
- 9 zero-shot TSFMs vs 8 econometric benchmarks (HAR family) on the VOLARE
  dataset (50 assets across equities/FX/futures, 3 horizons).
- TSFMs do NOT uniformly beat HAR. Only Tiny Time Mixers (TTM) — a <1M-param
  model — beats the well-specified Log-HAR benchmark at every horizon, and only
  by a narrow margin.
- Short-horizon advantages come mostly from BETTER SCALE CALIBRATION
  (Mincer-Zarnowitz), not from better modelling of volatility dynamics.
- Most durable result: an equal-weight ensemble of TTM + Log-HAR enters the
  Model Confidence Set (MCS) for 98-100% of assets — more often than either
  component alone. A forecaster need NOT pick the best model per asset.

Practical takeaway for WQUANT's 5-factor 波动率 dimension:
  Do NOT chase large foundation models. Use the lightweight Log-HAR + TTM
  equal-weight ensemble. It is more robust and far cheaper to run.

Components:
  - LogHAR: log-Heterogeneous Autoregressive realized-volatility forecaster
  - TTMForecaster: IBM TinyTimeMixer, zero-shot, lightweight (optional dep)
  - EnsembleVolForecaster: 0.5 * LogHAR + 0.5 * TTM (with graceful fallback)
  - volatility_score_from_forecast: maps forecast -> 0-100 volatility dimension
"""

import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# --------------------------------------------------------------------------- #
# Realized variance
# --------------------------------------------------------------------------- #
def realized_variance(returns):
    """
    Compute daily realized variance from a return series.

    With intraday bars RV_t = sum_i r_{t,i}^2. With only daily closes we use the
    standard proxy RV_t = ret_t^2 (coarse but acceptable when intraday is absent).
    Feed log returns for the log-spec models.

    Args:
        returns: pd.Series of (log) returns, datetime-indexed.
    Returns:
        pd.Series of realized variance (>= 0).
    """
    rv = returns.pow(2.0)
    rv.name = 'rv'
    return rv


def _ols_predict(X, y):
    """OLS via lstsq with intercept. X may be 1D or 2D. Returns [intercept, ...]."""
    Xm = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)])
    coef, *_ = np.linalg.lstsq(Xm, np.asarray(y, dtype=float), rcond=None)
    return coef


# --------------------------------------------------------------------------- #
# Log-HAR / HAR (econometric benchmark)
# --------------------------------------------------------------------------- #
class LogHAR:
    """
    Log-Heterogeneous Autoregressive model (Corsi 2009, log specification).

        log(RV_t) = b0 + b_d*log(RV_{t-1})
                       + b_w*log(mean RV_{t-1..t-5})
                       + b_m*log(mean RV_{t-1..t-22}) + e_t

    Plain HAR is the same without the log transform (use_log=False).
    Multi-step (h-day) forecasts are produced by recursion.
    """

    def __init__(self, use_log=True, max_lag=22):
        self.use_log = use_log
        self.max_lag = max_lag
        self.coef_ = None
        self._insample_pred = None   # for Mincer-Zarnowitz recalibration
        self._insample_actual = None

    def fit(self, rv):
        rv = pd.Series(rv).dropna()
        rv = rv[rv > 0]
        if len(rv) < self.max_lag + 10:
            raise ValueError("Insufficient data to fit LogHAR (need > max_lag+10 points)")
        y = np.log(rv.values) if self.use_log else rv.values
        daily = rv.values
        n = len(daily)
        X, Y, Yhat = [], [], []
        for t in range(self.max_lag, n):
            d = np.log(daily[t - 1]) if self.use_log else daily[t - 1]
            w = np.log(daily[t - 5:t].mean()) if self.use_log else daily[t - 5:t].mean()
            m = np.log(daily[t - 22:t].mean()) if self.use_log else daily[t - 22:t].mean()
            X.append([d, w, m])
            Y.append(y[t])
        X = np.array(X)
        Y = np.array(Y)
        self.coef_ = _ols_predict(X, Y)
        # In-sample 1-step predictions (used for scale recalibration, no lookahead)
        self._insample_pred = self.coef_[0] + X @ self.coef_[1:]
        self._insample_actual = Y
        return self

    def _one_step(self, hist_rv):
        d = np.log(hist_rv[-1]) if self.use_log else hist_rv[-1]
        w = np.log(np.mean(hist_rv[-5:])) if self.use_log else np.mean(hist_rv[-5:])
        m = np.log(np.mean(hist_rv[-22:])) if self.use_log else np.mean(hist_rv[-22:])
        pred = self.coef_[0] + self.coef_[1] * d + self.coef_[2] * w + self.coef_[3] * m
        return float(np.exp(pred)) if self.use_log else float(pred)

    def forecast(self, rv, h=1):
        """Recursive h-step-ahead forecast of realized variance."""
        if self.coef_ is None:
            self.fit(rv)
        hist = list(pd.Series(rv).dropna().values)
        preds = []
        for _ in range(int(h)):
            p = self._one_step(hist)
            preds.append(p)
            hist.append(p)
        return np.array(preds)


# --------------------------------------------------------------------------- #
# Tiny Time Mixers (TTM) — lightweight zero-shot TSFM (optional dependency)
# --------------------------------------------------------------------------- #
class TTMForecaster:
    """
    IBM TinyTimeMixer zero-shot forecaster (Granite TSFM).

    Lightweight (<1M params), pretrained on public time-series corpora. Zero-shot:
    no fine-tuning required. Package: `pip install granite-tsfm` (provides tsfm_public).
    Model: `ibm/TTM`.

    The pipeline is built lazily and cached per prediction length, so repeated
    calls with the same horizon are cheap.
    """

    def __init__(self, context_length=64, prediction_length=22, model_id="ibm/TTM"):
        self.context_length = context_length
        self.prediction_length = prediction_length
        self.model_id = model_id
        self._pipelines = {}  # prediction_length -> pipeline

    def _build_pipeline(self, prediction_length):
        try:
            from tsfm_public import (
                TinyTimeMixerForPrediction,
                TimeSeriesPreprocessor,
                TimeSeriesForecastingPipeline,
            )
        except ImportError as e:
            raise ImportError(
                "TTMForecaster requires the IBM Granite TSFM package. Install with "
                "`pip install granite-tsfm` (or clone github.com/IBM/tsfm). "
                f"Original error: {e}"
            )
        model = TinyTimeMixerForPrediction.from_pretrained(
            self.model_id,
            revision="main",
            context_length=self.context_length,
            prediction_length=prediction_length,
        )
        tsp = TimeSeriesPreprocessor(
            timestamp_column="timestamp",
            target_columns=["rv"],
            id_columns=[],
            context_length=self.context_length,
            prediction_length=prediction_length,
            scaling=True,
            scaler_type="standard",
            freq="D",
        )
        return TimeSeriesForecastingPipeline(
            model, device="cpu", feature_extractor=tsp, batch_size=1
        )

    def forecast(self, rv, h=None):
        """
        Zero-shot forecast of length h (defaults to prediction_length).
        Returns np.ndarray of length h.
        """
        h = int(h) if h is not None else self.prediction_length
        if h not in self._pipelines:
            self._pipelines[h] = self._build_pipeline(h)
        pipe = self._pipelines[h]

        rv = pd.Series(rv).dropna()
        if len(rv) < self.context_length:
            raise ValueError(f"TTM needs >= {self.context_length} points, got {len(rv)}")
        ctx = rv.tail(self.context_length)
        df = pd.DataFrame({
            "timestamp": pd.date_range(end=datetime.today(), periods=len(ctx), freq="D"),
            "rv": ctx.values,
        })
        out = pipe(df)
        # Robust column extraction across tsfm_public versions
        if "rv_prediction" in out.columns:
            fc = out["rv_prediction"].values
        else:
            fc = out.select_dtypes(include=[np.number]).iloc[:, -1].values
        fc = np.asarray(fc, dtype=float)
        return fc[:h] if len(fc) >= h else np.pad(fc, (0, h - len(fc)), mode="edge")


# --------------------------------------------------------------------------- #
# Equal-weight ensemble (the durable result of the paper)
# --------------------------------------------------------------------------- #
class EnsembleVolForecaster:
    """
    Equal-weight ensemble of Log-HAR + TTM (arXiv:2607.05291).

        RV_forecast_h = 0.5 * LogHAR_h + 0.5 * TTM_h

    Enters the Model Confidence Set for 98-100% of assets — more robust than
    either component alone, and far cheaper than large foundation models.

    If TTM is unavailable (package missing or load fails), it degrades gracefully
    to Log-HAR only and sets `ttm_available = False`.
    """

    def __init__(self, use_ttm=True, context_length=64, ttm_model="ibm/TTM",
                 recalibrate=False):
        self.use_ttm = use_ttm
        self.recalibrate = recalibrate
        self.loghar = LogHAR(use_log=True)
        self.ttm = TTMForecaster(context_length=context_length, model_id=ttm_model) if use_ttm else None
        self.ttm_available = False
        self._mz = None  # (alpha, beta) for Mincer-Zarnowitz recalibration

    def _fit_mz(self):
        """Estimate Mincer-Zarnowitz (alpha, beta) from in-sample LogHAR errors."""
        if self.loghar._insample_pred is None:
            return
        X = self.loghar._insample_pred
        Y = self.loghar._insample_actual
        if len(X) < 10:
            return
        coef = _ols_predict(X, Y)  # [alpha, beta]
        self._mz = (float(coef[0]), float(coef[1]))

    def forecast(self, rv, h=1):
        rv = pd.Series(rv).dropna()
        if self.loghar.coef_ is None:
            self.loghar.fit(rv)
            if self.recalibrate:
                self._fit_mz()

        loghar_fc = self.loghar.forecast(rv, h=h)

        if not self.use_ttm:
            fc = loghar_fc
        else:
            try:
                ttm_fc = self.ttm.forecast(rv, h=h)
                if len(ttm_fc) >= h:
                    ttm_fc = ttm_fc[:h]
                else:
                    ttm_fc = np.pad(ttm_fc, (0, h - len(ttm_fc)), mode="edge")
                self.ttm_available = True
                fc = 0.5 * loghar_fc + 0.5 * ttm_fc
            except Exception as e:
                warnings.warn(f"TTM unavailable ({e}); falling back to Log-HAR only.")
                self.ttm_available = False
                fc = loghar_fc

        if self.recalibrate and self._mz is not None:
            alpha, beta = self._mz
            fc = alpha + beta * fc  # remove level/scale bias
        return np.asarray(fc, dtype=float)


# --------------------------------------------------------------------------- #
# Forecast -> 0-100 volatility-dimension score
# --------------------------------------------------------------------------- #
def volatility_score_from_forecast(forecast_rv, hist_rv, window=60):
    """
    Map a forecasted realized-variance path to a 0-100 volatility-dimension score.

    Semantics are consistent with the 4-Layer L1 ATR-percentile:
      a HIGHER future volatility (forecast sits in a high percentile of the
      trailing distribution) => HIGHER score (vol expansion = breakout opportunity).

    Args:
        forecast_rv: array-like of forecasted RV (uses mean across horizon as signal)
        hist_rv:     trailing realized-variance series
        window:      trailing window for the percentile reference
    Returns:
        float in [0, 100]
    """
    sig = float(np.mean(forecast_rv)) if hasattr(forecast_rv, "__len__") else float(forecast_rv)
    hist = pd.Series(hist_rv).dropna().tail(window)
    if len(hist) < 5:
        return 50.0
    percentile = (hist < sig).mean() * 100.0  # % of past days with RV below forecast
    return float(np.clip(percentile, 0, 100))


# --------------------------------------------------------------------------- #
# Convenience entry point
# --------------------------------------------------------------------------- #
def ensemble_vol_score(returns_or_rv, h=5, use_ttm=True, recalibrate=False,
                       window=60, as_rv=False):
    """
    One-call helper: from a return series (or RV series if as_rv=True) produce
    both the 0-100 volatility score and the raw forecast.

    Returns:
        (score, forecast_array, ttm_available)
    """
    rv = returns_or_rv if as_rv else realized_variance(pd.Series(returns_or_rv))
    ef = EnsembleVolForecaster(use_ttm=use_ttm, recalibrate=recalibrate)
    fc = ef.forecast(rv, h=h)
    score = volatility_score_from_forecast(fc, rv, window=window)
    return score, fc, ef.ttm_available


if __name__ == "__main__":
    # Smoke test with synthetic realized variance (no external deps).
    np.random.seed(0)
    n = 300
    # AR(1)-like daily realized variance in percent units
    base = np.abs(np.random.normal(1.0, 0.3, n))
    rv = pd.Series(base)
    ret = np.sqrt(rv) * np.random.normal(0, 1, n) / 100.0  # synthetic returns

    loghar = LogHAR(use_log=True).fit(rv)
    fc1 = loghar.forecast(rv, h=5)
    print("LogHAR 5-day forecast (RV):", np.round(fc1, 4))

    ef = EnsembleVolForecaster(use_ttm=False)  # TTM off -> Log-HAR only
    fc2 = ef.forecast(rv, h=5)
    score = volatility_score_from_forecast(fc2, rv, window=60)
    print("Ensemble (Log-HAR only) 5-day forecast:", np.round(fc2, 4))
    print("Volatility-dimension score (0-100):", score)
    print("TTM available:", ef.ttm_available)
    print("SMOKE TEST OK")
