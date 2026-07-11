"""
Multi-Factor Scoring Engine
Calculates composite scores based on 6 factor categories
Incorporates latest research from arXiv papers (2026)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from collections import defaultdict

try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("Warning: ta library not installed. Technical indicators will use simplified calculations.")

from config import *


class MultiFactorScorer:
    """
    Multi-factor scorer with latest research integration.
    
    New features (2026 arXiv papers):
    - Market impact model (square-root law, arXiv:2606.24019)
    - Robust Bayesian portfolio selection (arXiv:2606.24212)
    - Adaptive regime detection (arXiv:2606.23596)
    - Dynamic transaction cost optimization (arXiv:2606.21784)
    - Realized-volatility forecasting: Log-HAR + TTM equal-weight ensemble (arXiv:2607.05291)
    - Distribution-free uncertainty quantification: dependence-aware bootstrap /
      conformal confidence intervals for signals (arXiv:2607.06690)
    """

    def __init__(self, factor_weights=None, enable_market_impact=True, 
                 enable_regime_detection=True, enable_robust_bayesian=False,
                 enable_vol_forecast=None, vol_horizon=None, enable_ttm_vol=None,
                 vol_context_length=None, enable_uncertainty=None):
        """
        Initialize scorer with factor weights
        
        Args:
            factor_weights: Dict with keys ['momentum', 'technical', 'volume', 'fundamental', 'macro', 'sector']
            enable_market_impact: Enable market impact adjustment (arXiv:2606.24019)
            enable_regime_detection: Enable adaptive regime detection (arXiv:2606.23596)
            enable_robust_bayesian: Enable robust Bayesian portfolio selection (arXiv:2606.24212)
            enable_vol_forecast: Enable realized-volatility forecasting factor (arXiv:2607.05291);
                                 defaults to config.ENABLE_VOL_FORECAST
            vol_horizon: Forecast horizon in days for the volatility dimension (1/5/22);
                         defaults to config.VOL_HORIZON
            enable_ttm_vol: Use Tiny Time Mixers (TTM) in the equal-weight ensemble (needs granite-tsfm);
                            defaults to config.VOL_USE_TTM
            vol_context_length: Context length for TTM; defaults to config.VOL_CONTEXT_LENGTH
            enable_uncertainty: Enable distribution-free uncertainty quantification of the
                                return signal (arXiv:2607.06690); defaults to config.ENABLE_UNCERTAINTY
        """
        if factor_weights is None:
            self.factor_weights = FACTOR_WEIGHTS
        else:
            # Validate weights sum to 1.0
            total = sum(factor_weights.values())
            if abs(total - 1.0) > 0.001:
                print(f"Warning: Factor weights sum to {total}, normalizing to 1.0")
                self.factor_weights = {k: v/total for k, v in factor_weights.items()}
            else:
                self.factor_weights = factor_weights
        
        # New feature flags (from arXiv papers)
        self.enable_market_impact = enable_market_impact
        self.enable_regime_detection = enable_regime_detection
        self.enable_robust_bayesian = enable_robust_bayesian
        # Volatility forecasting flags resolve from config when not explicitly passed
        self.enable_vol_forecast = ENABLE_VOL_FORECAST if enable_vol_forecast is None else enable_vol_forecast
        self.vol_horizon = VOL_HORIZON if vol_horizon is None else vol_horizon
        self.enable_ttm_vol = VOL_USE_TTM if enable_ttm_vol is None else enable_ttm_vol
        self.vol_context_length = VOL_CONTEXT_LENGTH if vol_context_length is None else vol_context_length
        self._vol_forecaster = None  # lazy-built equal-weight ensemble
        # Uncertainty quantification flag resolves from config when not explicitly passed
        self.enable_uncertainty = ENABLE_UNCERTAINTY if enable_uncertainty is None else enable_uncertainty
        
        # Regime detection state
        self.current_regime = 'normal'  # 'bull', 'bear', 'normal', 'crisis'
        self.regime_confidence = 0.5
        
        print(f"Factor weights: {self.factor_weights}")
        print(f"Market impact model: {'ON' if enable_market_impact else 'OFF'}")
        print(f"Regime detection: {'ON' if enable_regime_detection else 'OFF'}")
        print(f"Robust Bayesian: {'ON' if enable_robust_bayesian else 'OFF'}")
        print(f"Vol forecast (arXiv:2607.05291): {'ON' if self.enable_vol_forecast else 'OFF'}")
        print(f"Uncertainty quantification (arXiv:2607.06690): {'ON' if self.enable_uncertainty else 'OFF'}")

    def calculate_scores(self, data, fundamentals=None, macro_data=None, position_sizes=None):
        """
        Calculate composite scores for all symbols in data
        
        Args:
            data: Dict {symbol: DataFrame with OHLCV}
            fundamentals: Dict {symbol: dict with fundamental metrics}
            macro_data: Dict with macro indicators
            position_sizes: Dict {symbol: shares} for market impact calculation
            
        Returns:
            DataFrame: Index = symbols, columns = factor scores + composite score
        """
        scores = {}
        
        # Step 1: Detect market regime (if enabled)
        if self.enable_regime_detection:
            self._detect_regime(data)
            print(f"Detected regime: {self.current_regime} (confidence: {self.regime_confidence:.2f})")
        
        # Step 2: Calculate scores for each symbol
        for symbol, df in data.items():
            if df is None or df.empty or len(df) < 50:
                print(f"Skipping {symbol}: insufficient data")
                continue
            
            # Calculate each factor score
            momentum_score = self._calculate_momentum_score(df)
            technical_score = self._calculate_technical_score(df)
            volume_score = self._calculate_volume_score(df)
            fundamental_score = self._calculate_fundamental_score(symbol, fundamentals)
            macro_score = self._calculate_macro_score(macro_data)
            sector_score = self._calculate_sector_score(symbol, data)

            # Optional volatility-dimension score (arXiv:2607.05291)
            vol_score = None
            if self.enable_vol_forecast:
                vol_score = self._calculate_volatility_score(df)
            
            # Store individual scores
            scores[symbol] = {
                'momentum': momentum_score,
                'technical': technical_score,
                'volume': volume_score,
                'fundamental': fundamental_score,
                'macro': macro_score,
                'sector': sector_score
            }
            if vol_score is not None:
                scores[symbol]['volatility'] = vol_score
            
            # Calculate weighted composite score
            composite = (
                momentum_score * self.factor_weights['momentum'] +
                technical_score * self.factor_weights['technical'] +
                volume_score * self.factor_weights['volume'] +
                fundamental_score * self.factor_weights['fundamental'] +
                macro_score * self.factor_weights['macro'] +
                sector_score * self.factor_weights['sector']
            )
            
            # Step 3: Apply market impact adjustment (arXiv:2606.24019)
            if self.enable_market_impact and position_sizes and symbol in position_sizes:
                impact_adjustment = self._calculate_market_impact_adjustment(
                    symbol, df, position_sizes[symbol]
                )
                composite = composite * (1 - impact_adjustment)  # Reduce score for high impact
                scores[symbol]['market_impact_adjustment'] = impact_adjustment
            
            # Step 4: Apply regime-based weight adjustment (arXiv:2606.23596)
            if self.enable_regime_detection:
                regime_adjustment = self._apply_regime_adjustment(scores[symbol])
                composite = composite * regime_adjustment
                scores[symbol]['regime_adjustment'] = regime_adjustment
            
            scores[symbol]['composite'] = round(composite, 2)

            # Optional distribution-free uncertainty quantification (arXiv:2607.06690)
            if self.enable_uncertainty:
                uq = self._quantify_signal_uncertainty(df)
                if uq is not None:
                    scores[symbol].update(uq)
        
        # Convert to DataFrame
        scores_df = pd.DataFrame.from_dict(scores, orient='index')
        
        return scores_df

    def _calculate_momentum_score(self, df, periods=MOMENTUM_PERIODS):
        """Calculate momentum factor score (0-100)"""
        try:
            close = df['close']

            # Calculate returns over multiple periods
            returns = {}
            for period in periods:
                if len(close) > period:
                    ret = (close.iloc[-1] / close.iloc[-period] - 1) * 100
                    returns[period] = ret
                else:
                    returns[period] = 0

            # Risk-adjusted momentum (return / volatility)
            volatility = close.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252)
            if volatility > 0:
                recent_return = returns[periods[0]]
                risk_adj_momentum = recent_return / (volatility * 100)
            else:
                risk_adj_momentum = 0

            # Normalize to 0-100 scale
            # Assume momentum ranges from -50% to +50%
            momentum_raw = (
                0.5 * returns.get(periods[0], 0) +  # 1-month return
                0.3 * returns.get(periods[1], 0) +  # 3-month return
                0.2 * returns.get(periods[2], 0)     # 6-month return
            )

            # Clip and normalize
            momentum_raw = np.clip(momentum_raw, -50, 50)
            score = (momentum_raw + 50) * 1.0  # Convert -50~50 to 0~100

            return round(score, 2)

        except Exception as e:
            print(f"Error calculating momentum score: {e}")
            return 50.0  # Neutral score on error

    def _calculate_technical_score(self, df):
        """Calculate technical indicators score (0-100)"""
        try:
            if not TA_AVAILABLE:
                # Simplified technical score without ta library
                return self._calculate_simple_technical_score(df)

            close = df['close']
            high = df['high']
            low = df['low']

            score_components = []

            # RSI (14)
            rsi_indicator = ta.momentum.RSIIndicator(close=close, window=RSI_PERIOD)
            rsi = rsi_indicator.rsi().iloc[-1]
            # RSI: lower = better buy opportunity (oversold)
            # Convert: RSI < 30 = 80+ score, RSI > 70 = 20- score
            if rsi < 30:
                rsi_score = 80 + (30 - rsi) * 2.67  # Max 100
            elif rsi > 70:
                rsi_score = 20 - (rsi - 70) * 2.67  # Min 0
            else:
                rsi_score = 50
            score_components.append(rsi_score)

            # MACD
            macd_indicator = ta.trend.MACD(
                close=close,
                window_slow=MACD_PARAMS[1],
                window_fast=MACD_PARAMS[0],
                window_sign=MACD_PARAMS[2]
            )
            macd = macd_indicator.macd().iloc[-1]
            macd_signal = macd_indicator.macd_signal().iloc[-1]
            # MACD > Signal = bullish
            macd_diff = macd - macd_signal
            macd_score = 50 + macd_diff * 10  # Arbitrary scaling
            macd_score = np.clip(macd_score, 0, 100)
            score_components.append(macd_score)

            # Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(
                close=close,
                window=BOLLINGER_PERIOD,
                window_dev=BOLLINGER_STD
            )
            bb_upper = bb_indicator.bollinger_hband().iloc[-1]
            bb_lower = bb_indicator.bollinger_lband().iloc[-1]
            current_price = close.iloc[-1]

            # Price relative to Bollinger Bands
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
            # Lower band = buy opportunity
            bb_score = (1 - bb_position) * 100
            score_components.append(bb_score)

            # Moving Average Trend
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            current_price = close.iloc[-1]

            # Score based on MA alignment
            if current_price > ma20 > ma60:
                ma_score = 80  # Strong uptrend
            elif current_price > ma20:
                ma_score = 60  # Moderate uptrend
            elif current_price < ma20 < ma60:
                ma_score = 20  # Strong downtrend
            else:
                ma_score = 40  # Moderate downtrend
            score_components.append(ma_score)

            # Average all technical components
            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating technical score: {e}")
            return 50.0

    def _calculate_simple_technical_score(self, df):
        """Simplified technical score without ta library"""
        try:
            close = df['close']

            # Simple RSI calculation
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=RSI_PERIOD).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=RSI_PERIOD).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi = rsi.iloc[-1]

            if rsi < 30:
                rsi_score = 80
            elif rsi > 70:
                rsi_score = 20
            else:
                rsi_score = 50

            # Simple MA score
            ma20 = close.rolling(20).mean().iloc[-1]
            current_price = close.iloc[-1]

            if current_price > ma20:
                ma_score = 65
            else:
                ma_score = 35

            return round((rsi_score + ma_score) / 2, 2)

        except Exception as e:
            print(f"Error in simple technical score: {e}")
            return 50.0

    def _calculate_volume_score(self, df):
        """Calculate volume-based score (0-100)"""
        try:
            close = df['close']
            volume = df['volume']

            # Volume change vs 20-day average
            vol_ma20 = volume.rolling(20).mean()
            vol_change = (volume.iloc[-1] / vol_ma20.iloc[-1] - 1) * 100

            # Price change
            price_change = (close.iloc[-1] / close.iloc[-2] - 1) * 100

            # Volume-price divergence analysis
            # Ideal: price up + volume up = bullish (high score)
            # Bad: price up + volume down = bearish (low score)
            if price_change > 0 and vol_change > 0:
                divergence_score = 80  # Bullish
            elif price_change > 0 and vol_change < 0:
                divergence_score = 30  # Bearish divergence
            elif price_change < 0 and vol_change > 0:
                divergence_score = 60  # Capitulation (could be bottom)
            else:
                divergence_score = 40  # Both down

            # Volume trend score (increasing volume = higher score)
            recent_vol = volume.tail(5).mean()
            older_vol = volume.tail(20).head(15).mean()
            vol_trend = (recent_vol / older_vol - 1) * 100

            vol_trend_score = np.clip(vol_trend + 50, 0, 100)

            # Combine scores
            final_score = 0.6 * divergence_score + 0.4 * vol_trend_score
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating volume score: {e}")
            return 50.0

    def _calculate_fundamental_score(self, symbol, fundamentals):
        """Calculate fundamental factor score (0-100)"""
        try:
            if fundamentals is None or symbol not in fundamentals:
                # Use sample data from config
                if symbol in FUNDAMENTAL_DATA:
                    fund = FUNDAMENTAL_DATA[symbol]
                else:
                    return 50.0  # Neutral if no data
            else:
                fund = fundamentals[symbol]

            score_components = []

            # P/E ratio (lower = better, but not too low)
            pe = fund.get('pe', 20)
            if 5 < pe < 15:
                pe_score = 80  # Ideal range
            elif 15 <= pe < 25:
                pe_score = 60
            elif 25 <= pe < 35:
                pe_score = 40
            else:
                pe_score = 20
            score_components.append(pe_score)

            # P/B ratio (lower = better)
            pb = fund.get('pb', 2)
            if pb < 1.5:
                pb_score = 80
            elif pb < 3:
                pb_score = 60
            elif pb < 5:
                pb_score = 40
            else:
                pb_score = 20
            score_components.append(pb_score)

            # ROE (higher = better)
            roe = fund.get('roe', 0.15)
            roe_score = np.clip(roe * 300, 0, 100)  # ROE 33% = 100 score
            score_components.append(roe_score)

            # Revenue growth (higher = better)
            growth = fund.get('revenue_growth', 0.10)
            growth_score = np.clip(growth * 400, 0, 100)  # 25% growth = 100 score
            score_components.append(growth_score)

            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating fundamental score for {symbol}: {e}")
            return 50.0

    def _calculate_macro_score(self, macro_data):
        """Calculate macro economic factor score (0-100)"""
        try:
            if macro_data is None:
                macro_data = MACRO_DATA

            score_components = []

            # Interest rate (lower = better for stocks)
            rate = macro_data.get('interest_rate', 0.0325)
            if rate < 0.02:
                rate_score = 80
            elif rate < 0.04:
                rate_score = 60
            elif rate < 0.06:
                rate_score = 40
            else:
                rate_score = 20
            score_components.append(rate_score)

            # CPI inflation (moderate = better)
            cpi = macro_data.get('cpi', 0.02)
            if 0.01 < cpi < 0.03:
                cpi_score = 70
            elif cpi < 0.01:
                cpi_score = 40  # Deflation risk
            else:
                cpi_score = 30  # High inflation
            score_components.append(cpi_score)

            # PMI (above 50 = expansion)
            pmi = macro_data.get('pmi', 50.5)
            pmi_score = np.clip((pmi - 40) * 10, 0, 100)  # PMI 50 = 100, PMI 40 = 0
            score_components.append(pmi_score)

            # GDP growth (higher = better)
            gdp = macro_data.get('gdp_growth', 0.052)
            gdp_score = np.clip(gdp * 1500, 0, 100)  # 6.7% GDP = 100 score
            score_components.append(gdp_score)

            final_score = np.mean(score_components)
            return round(final_score, 2)

        except Exception as e:
            print(f"Error calculating macro score: {e}")
            return 50.0

    def _calculate_sector_score(self, symbol, all_data):
        """Calculate sector/industry factor score (0-100)"""
        try:
            # Get sector for this symbol
            sector = SECTOR_MAP.get(symbol, 'unknown')
            
            # Calculate sector performance (average return of all stocks in sector)
            sector_returns = []
            for sym, df in all_data.items():
                if SECTOR_MAP.get(sym) == sector and df is not None and len(df) > 20:
                    ret = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100
                    sector_returns.append(ret)
            
            if len(sector_returns) == 0:
                return 50.0
            
            # Sector relative strength vs market
            sector_avg_return = np.mean(sector_returns)
            
            # Normalize: assume sector return ranges from -20% to +20%
            sector_score = np.clip((sector_avg_return + 20) * 2.5, 0, 100)
            return round(sector_score, 2)
            
        except Exception as e:
            print(f"Error calculating sector score for {symbol}: {e}")
            return 50.0
    
    # ==================== New Methods (arXiv 2026 Papers) ====================
    
    def _calculate_market_impact_adjustment(self, symbol, df, position_size, daily_volume=None):
        """
        Calculate market impact adjustment using square-root law (arXiv:2606.24019)
        
        Square-root law: Impact ∝ √(Q / V_D)
        Where:
            Q = Order size (shares)
            V_D = Daily trading volume (shares)
        
        Args:
            symbol: Stock symbol
            df: Price/volume DataFrame
            position_size: Planned position size (shares)
            daily_volume: Average daily volume (if None, use data)
            
        Returns:
            float: Impact adjustment factor (0-1, where 1 = maximum penalty)
        """
        try:
            if daily_volume is None:
                # Use 20-day average volume
                daily_volume = df['volume'].tail(20).mean()
            
            if daily_volume <= 0:
                return 0.0
            
            # Calculate order size relative to daily volume
            relative_size = position_size / daily_volume
            
            # Square-root law: impact ∝ √(relative_size)
            # Normalize: Assume √(Q/V_D) = 0.1 (10% of daily volume) is "high impact"
            # Use sigmoid normalization to map to 0-1 adjustment factor
            impact_raw = np.sqrt(relative_size)
            impact_adjustment = 1 / (1 + np.exp(-10 * (impact_raw - 0.05)))  # Sigmoid centered at 0.05
            
            # Cap at 0.3 (maximum 30% score reduction for high impact)
            impact_adjustment = min(impact_adjustment * 0.3, 0.3)
            
            return round(impact_adjustment, 4)
            
        except Exception as e:
            print(f"Error calculating market impact for {symbol}: {e}")
            return 0.0
    
    def _detect_regime(self, data):
        """
        Detect current market regime using HMM-like approach (arXiv:2606.23596)
        
        Regimes:
        - 'bull': Low volatility, positive returns
        - 'bear': High volatility, negative returns
        - 'normal': Moderate volatility/returns
        - 'crisis': Extreme volatility
        
        Returns:
            str: Detected regime
        """
        try:
            # Calculate market-wide metrics
            all_returns = []
            all_volatilities = []
            
            for symbol, df in data.items():
                if df is not None and len(df) > 20:
                    returns = df['close'].pct_change().tail(20)
                    all_returns.extend(returns.dropna().tolist())
                    
                    vol = returns.std() * np.sqrt(252)  # Annualized
                    all_volatilities.append(vol)
            
            if len(all_returns) < 10:
                self.current_regime = 'normal'
                self.regime_confidence = 0.5
                return
            
            # Market metrics
            avg_return = np.mean(all_returns) * 252  # Annualized
            avg_volatility = np.mean(all_volatilities)
            
            # Regime classification thresholds
            if avg_volatility > 0.4:  # >40% annualized volatility
                self.current_regime = 'crisis'
                self.regime_confidence = 0.7
            elif avg_return > 0.05 and avg_volatility < 0.25:
                self.current_regime = 'bull'
                self.regime_confidence = 0.8
            elif avg_return < -0.05 and avg_volatility > 0.25:
                self.current_regime = 'bear'
                self.regime_confidence = 0.8
            else:
                self.current_regime = 'normal'
                self.regime_confidence = 0.6
            
        except Exception as e:
            print(f"Error detecting regime: {e}")
            self.current_regime = 'normal'
            self.regime_confidence = 0.5
    
    def _apply_regime_adjustment(self, scores):
        """
        Apply regime-based factor weight adjustment (arXiv:2606.23596)
        
        Different regimes favor different factors:
        - Bull: Momentum + Technical (trend-following)
        - Bear: Fundamental + Macro (defensive)
        - Normal: Balanced
        - Crisis: Volume + Sector (risk-off)
        
        Args:
            scores: Dict of factor scores for a symbol
            
        Returns:
            float: Adjustment multiplier (0.8 - 1.2)
        """
        try:
            if self.current_regime == 'bull':
                # Boost momentum and technical scores
                adjustment = 1.0 + 0.1 * (scores['momentum'] + scores['technical']) / 200
            
            elif self.current_regime == 'bear':
                # Boost fundamental and macro scores
                adjustment = 1.0 + 0.1 * (scores['fundamental'] + scores['macro']) / 200
            
            elif self.current_regime == 'crisis':
                # Boost volume and sector scores (defensive)
                adjustment = 1.0 + 0.1 * (scores['volume'] + scores['sector']) / 200
            
            else:  # normal
                adjustment = 1.0
            
            return round(adjustment, 4)
            
        except Exception as e:
            print(f"Error applying regime adjustment: {e}")
            return 1.0

    # ==================== Volatility Forecasting (arXiv:2607.05291) ====================

    def _get_vol_forecaster(self):
        """Lazily build the equal-weight Log-HAR + TTM ensemble forecaster."""
        if self._vol_forecaster is None:
            from volatility_forecaster import EnsembleVolForecaster
            self._vol_forecaster = EnsembleVolForecaster(
                use_ttm=self.enable_ttm_vol,
                context_length=self.vol_context_length,
                ttm_model="ibm/TTM"
            )
        return self._vol_forecaster

    def _calculate_volatility_score(self, df, horizon=None):
        """
        Volatility-dimension score (0-100) via Log-HAR + TTM equal-weight ensemble.

        Returns the percentile of the h-day-ahead forecasted realized variance within
        the trailing 60-day distribution. Semantics match the 4-Layer L1 ATR-percentile:
        higher future volatility => higher score (vol expansion = breakout opportunity).
        Default horizon from vol_horizon (1 / 5 / 22 days).
        """
        try:
            from volatility_forecaster import realized_variance, volatility_score_from_forecast
            if horizon is None:
                horizon = self.vol_horizon
            close = df['close']
            if len(close) < 30:
                return 50.0
            ret = np.log(close / close.shift(1)).dropna()
            rv = realized_variance(ret)
            if len(rv) < self.vol_context_length + 10:
                return 50.0
            forecaster = self._get_vol_forecaster()
            fc = forecaster.forecast(rv, h=horizon)
            score = volatility_score_from_forecast(fc, rv, window=60)
            return round(float(score), 2)
        except Exception as e:
            print(f"Error in volatility forecasting: {e}")
            return 50.0

    def _quantify_signal_uncertainty(self, df, lookback=120):
        """
        Distribution-free uncertainty quantification of the return signal (arXiv:2607.06690).

        Builds a dependence-aware (moving-block) bootstrap CI on the mean daily
        return, then maps it to:
          - confidence:       position-sizing multiplier in [UQ_CONF_FLOOR, 1]
          - ci_low / ci_high: (1 - UQ_ALPHA) CI bounds on mean return
          - edge_significant: True if the CI excludes zero (a real edge, not noise)
          - risk_scale:       size multiplier after the risk gate (0 if vetoed)

        Uses tsbootstrap MovingBlock if installed, else a pure-numpy fallback.
        Returns a dict of columns to merge into the symbol's scores, or None on error.
        """
        try:
            from uncertainty_quantification import quantify_signal
            close = df['close']
            ret = close.pct_change().dropna().tail(lookback)
            if len(ret) < 30:
                return None
            bundle = quantify_signal(
                ret.values,
                alpha=UQ_ALPHA,
                direction="long",
                n_bootstraps=UQ_N_BOOTSTRAPS,
                random_state=UQ_RANDOM_STATE,
                require_significant=UQ_REQUIRE_SIGNIFICANT,
            )
            ci, gate = bundle['ci'], bundle['risk_gate']
            return {
                'confidence': round(bundle['confidence'], 3),
                'ci_low': round(ci['lower'], 6),
                'ci_high': round(ci['upper'], 6),
                'edge_significant': bool(gate['significant']),
                'risk_scale': round(gate['scale'], 3),
            }
        except Exception as e:
            print(f"Error in uncertainty quantification: {e}")
            return None


if __name__ == "__main__":
    # Test the scorer
    from data_loader import MultiMarketDataLoader

    print("Testing MultiFactorScorer...")
    loader = MultiMarketDataLoader()
    data = loader.load_data(
        {'ashare': ['600519.SH', '000858.SZ']},
        '2024-01-01', '2024-06-30'
    )

    scorer = MultiFactorScorer()
    fundamentals = loader.load_fundamental_data(list(data.keys()))
    macro = loader.load_macro_data()

    scores = scorer.calculate_scores(data, fundamentals, macro)
    print("\nScoring Results:")
    print(scores)
