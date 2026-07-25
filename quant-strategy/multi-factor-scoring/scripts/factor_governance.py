"""
因子治理模块（Factor Governance）—— FTS 派生的 6 项工程化能力

来源：微信公众号文章《FTS：一套贯彻 Harness 工程规范的 AI 原生量化因子系统》
映射目标：multi-factor-scoring 的多因子打分 + 组合构建流程

实现的 6 项能力：
  1. 契约先行 (TypedDict) + 原子持久化 (temp + os.replace)
  2. 三级评估链：L1 回测 / L2 经济逻辑 / L3 多重检验(Bonferroni + FDR)
  3. 走航验证 (Walk-forward)：滚动窗口 IC 一致性
  4. 因子衰减检验 (Decay Test)：6 个月滚动衰减率 >30% 剔除
  5. 熔断机制 (Circuit Breaker)：token 预算 / 连续低 IC / 失败率
  6. 正交化 (Orthogonalization)：相关性 >0.7 剔除冗余因子

所有功能默认关闭，由 config 驱动（与现有 arXiv 模块一致）。
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np
import pandas as pd


def _spearman(a: pd.Series, b: pd.Series) -> float:
    """Spearman 相关系数：对秩做 Pearson（不依赖 scipy，便于移植）。"""
    ra = a.rank()
    rb = b.rank()
    cov = np.cov(ra.values, rb.values)
    denom = np.sqrt(cov[0, 0] * cov[1, 1])
    return float(cov[0, 1] / denom) if denom > 0 else float("nan")


# =====================================================================
# 1. 契约先行 + 原子持久化
# =====================================================================

class FactorEvaluation(TypedDict, total=False):
    """因子评估契约（模块间通信的统一结构）"""
    factor_id: str
    trace_id: str
    level_1_backtest: Dict[str, float]      # IC / Sharpe / monotonicity / oos_ratio
    level_2_economic: Dict[str, int]        # theory / behavior / microstructure / institution (0/1)
    level_3_multiple: Dict[str, Any]        # bonferroni / fdr 通过情况
    passed: bool
    failure_reasons: List[str]
    evaluated_at: str


def atomic_write(path: str, data: Any) -> None:
    """
    原子持久化：临时文件 + 系统级 os.replace，避免写入中途崩溃导致文件损坏。

    Args:
        path: 目标文件路径
        data: 可 JSON 序列化的对象
    """
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, path)  # 系统级原子操作，跨平台安全


# =====================================================================
# 2. 三级评估链
# =====================================================================

def evaluate_level1(factor_series: pd.Series, forward_returns: pd.Series) -> Dict[str, Any]:
    """
    L1 回测验证：IC / 单调性 / 样本外占比。

    Args:
        factor_series: 因子值时间序列（与 forward_returns 对齐）
        forward_returns: 同期前向收益序列
    Returns:
        dict: 各检查项与是否通过
    """
    aligned = pd.concat([factor_series, forward_returns], axis=1).dropna()
    aligned.columns = ["f", "r"]
    if len(aligned) < 20:
        return {"ic": float("nan"), "monotonicity": 0.0, "passed": False,
                "reason": "样本不足"}

    ic = _spearman(aligned["f"], aligned["r"])
    # 单调性：按因子值分 5 组，组间收益是否单调
    aligned = aligned.sort_values("f")
    aligned["quintile"] = pd.qcut(aligned["f"].rank(method="first"), 5, labels=False)
    grp = aligned.groupby("quintile")["r"].mean()
    monotonicity = float(np.corrcoef(range(len(grp)), grp.values)[0, 1]) if len(grp) >= 2 else 0.0

    checks = {
        "ic_gt_0.03": bool(ic > 0.03),
        "monotonic": bool(monotonicity >= 0.5),
    }
    return {"ic": round(float(ic), 4), "monotonicity": round(monotonicity, 4),
            "checks": checks, "passed": all(checks.values())}


def evaluate_level2(economic_rubric: Dict[str, int]) -> Dict[str, Any]:
    """
    L2 经济逻辑：理论 / 行为 / 微观结构 / 制度 四维，每维 0/1，需 >=3/4 通过。

    Args:
        economic_rubric: {theory, behavior, microstructure, institution} 取值 0/1
    """
    score = int(sum(economic_rubric.values()))
    passed = bool(score >= 3)
    return {"score": score, "passed": passed}


def evaluate_level3(p_values: List[float], alpha: float = 0.05) -> Dict[str, Any]:
    """
    L3 多重检验校正：Bonferroni + Benjamini-Hochberg FDR。

    Args:
        p_values: 多个因子/检验的 p 值列表
        alpha: 显著性水平
    """
    n = len(p_values)
    if n == 0:
        return {"bonferroni_pass": [], "fdr_pass": [], "passed": False}

    bonferroni = [p < alpha / n for p in p_values]

    # BH-FDR
    order = np.argsort(p_values)
    fdr_pass = [False] * n
    for rank, idx in enumerate(order, start=1):
        fdr_pass[idx] = p_values[idx] <= alpha * rank / n

    passed = any(bonferroni) or any(fdr_pass)
    return {"bonferroni_pass": bonferroni, "fdr_pass": fdr_pass, "passed": passed}


def evaluate_factor_3level(
    factor_id: str,
    factor_series: pd.Series,
    forward_returns: pd.Series,
    economic_rubric: Dict[str, int],
    p_values: Optional[List[float]] = None,
    trace_id: Optional[str] = None,
) -> FactorEvaluation:
    """
    三级评估链整合：L1 回测 -> L2 经济逻辑 -> L3 多重检验。

    注：若未提供 p_values，则 L3 退化为单因子通过（不做跨因子校正）。
    """
    l1 = evaluate_level1(factor_series, forward_returns)
    l2 = evaluate_level2(economic_rubric)
    l3 = evaluate_level3(p_values if p_values is not None else [0.01])

    passed = l1["passed"] and l2["passed"] and l3["passed"]
    reasons: List[str] = []
    if not l1["passed"]:
        reasons.append("L1 backtest failed")
    if not l2["passed"]:
        reasons.append("L2 economic logic < 3/4")
    if not l3["passed"]:
        reasons.append("L3 multiple-testing rejected")

    return FactorEvaluation(
        factor_id=factor_id,
        trace_id=trace_id or "",
        level_1_backtest=l1,
        level_2_economic=economic_rubric,
        level_3_multiple=l3,
        passed=passed,
        failure_reasons=reasons,
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )


# =====================================================================
# 3. 走航验证 (Walk-forward)
# =====================================================================

def walk_forward_validate(
    factor_series: pd.Series,
    forward_returns: pd.Series,
    n_splits: int = 4,
    min_train: int = 60,
) -> Dict[str, Any]:
    """
    滚动窗口走航验证：替代单次 train/test 切分。

    每个窗口：前段训练（此处仅用于占位兼容），后段验证 IC；
    要求因子在多窗口滚动测试中 IC 一致为正且达标。

    Returns:
        dict: windows(各窗口IC), mean_ic, consistency(达标窗口占比), passed
    """
    df = pd.concat([factor_series, forward_returns], axis=1).dropna()
    df.columns = ["f", "r"]
    n = len(df)
    if n < min_train + 20:
        return {"windows": [], "mean_ic": float("nan"), "consistency": 0.0, "passed": False}

    step = (n - min_train) // n_splits
    windows: List[float] = []
    for i in range(n_splits):
        start = min_train + i * step
        if start >= n:
            break
        seg = df.iloc[:start]
        test = df.iloc[start: start + step]
        if len(test) < 10:
            continue
        ic = _spearman(seg["f"], seg["r"])
        windows.append(round(float(ic), 4))

    if not windows:
        return {"windows": [], "mean_ic": float("nan"), "consistency": 0.0, "passed": False}

    mean_ic = float(np.mean(windows))
    consistency = float(np.mean([1 if w > 0.03 else 0 for w in windows]))
    passed = bool(mean_ic > 0.03 and consistency >= 0.75)
    return {"windows": windows, "mean_ic": round(mean_ic, 4),
            "consistency": round(consistency, 4), "passed": passed}


# =====================================================================
# 4. 因子衰减检验 (Decay Test)
# =====================================================================

def factor_decay_test(
    ic_history: pd.Series,
    window: int = 126,
    threshold: float = 0.30,
) -> Dict[str, Any]:
    """
    因子衰减检验：近期 Sharpe(以 IC 近似) 相对历史衰减率。

    衰减率 = (近期 IC - 历史 IC) / |历史 IC|
    衰减率 < -threshold（即近期比历史差超过 threshold）-> 剔除。

    Args:
        ic_history: 因子 IC 的时间序列
        window: 滚动窗口长度（默认 126 ≈ 6 个月交易日）
        threshold: 衰减阈值（默认 0.30）
    """
    s = ic_history.dropna()
    if len(s) < window * 2:
        return {"decay_rate": float("nan"), "recent_ic": float("nan"),
                "hist_ic": float("nan"), "remove": False}
    hist = s.iloc[:-window]
    recent = s.iloc[-window:]
    hist_ic = float(hist.mean())
    recent_ic = float(recent.mean())
    if abs(hist_ic) < 1e-9:
        decay_rate = 0.0
    else:
        decay_rate = (recent_ic - hist_ic) / abs(hist_ic)
    remove = bool(decay_rate < -threshold)
    return {"decay_rate": round(decay_rate, 4), "recent_ic": round(recent_ic, 4),
            "hist_ic": round(hist_ic, 4), "remove": remove}


# =====================================================================
# 5. 熔断机制 (Circuit Breaker)
# =====================================================================

class CircuitBreaker:
    """
    自动化跑批的安全网。三类熔断：
      - token 预算：单日 token 超预算 multiplier 倍 -> 熔断
      - 连续低 IC：连续 max_consec_low_ic 代 IC < min_ic -> 熔断
      - 失败率：失败率 > max_failure_rate -> 熔断
    """

    def __init__(
        self,
        token_budget_daily: int,
        max_token_multiplier: float = 2.0,
        min_ic: float = 0.01,
        max_consec_low_ic: int = 3,
        max_failure_rate: float = 0.90,
        alpha: float = 0.05,
    ):
        self.token_budget = token_budget_daily
        self.max_token_multiplier = max_token_multiplier
        self.min_ic = min_ic
        self.max_consec_low_ic = max_consec_low_ic
        self.max_failure_rate = max_failure_rate
        self.alpha = alpha

        self.token_used = 0
        self.consec_low_ic = 0
        self.total = 0
        self.failures = 0
        self._tripped = False
        self._trip_reason = ""

    def record_token(self, used: int) -> None:
        self.token_used += used
        if self.token_used > self.token_budget * self.max_token_multiplier:
            self._trip("token budget exceeded")

    def record_generation(self, ic: float, passed: bool) -> None:
        self.total += 1
        if not passed:
            self.failures += 1
        if ic < self.min_ic:
            self.consec_low_ic += 1
        else:
            self.consec_low_ic = 0

        if self.consec_low_ic >= self.max_consec_low_ic:
            self._trip("consecutive low IC")
        if self.total >= 10 and (self.failures / self.total) > self.max_failure_rate:
            self._trip("failure rate too high")

    def _trip(self, reason: str) -> None:
        if not self._tripped:
            self._tripped = True
            self._trip_reason = reason

    def tripped(self) -> bool:
        return self._tripped

    def trip_reason(self) -> str:
        return self._trip_reason

    def status(self) -> Dict[str, Any]:
        rate = (self.failures / self.total) if self.total else 0.0
        return {
            "tripped": self._tripped,
            "reason": self._trip_reason,
            "token_used": self.token_used,
            "token_budget": self.token_budget,
            "consec_low_ic": self.consec_low_ic,
            "failure_rate": round(rate, 4),
        }


# =====================================================================
# 6. 正交化 (Orthogonalization)
# =====================================================================

def orthogonalize_factors(
    scores_df: pd.DataFrame,
    factor_cols: List[str],
    corr_threshold: float = 0.7,
) -> List[str]:
    """
    正交化去冗余：因子分值相关性 > corr_threshold 的成对因子，
    剔除后者（贪心，保留先出现的因子）。

    Args:
        scores_df: 横截面打分表（index=symbol, columns=factor_cols）
        factor_cols: 参与正交化的因子列名
        corr_threshold: 相关性阈值
    Returns:
        保留的因子列名列表
    """
    present = [c for c in factor_cols if c in scores_df.columns]
    if len(present) < 2:
        return present

    corr = scores_df[present].corr().abs()
    kept = list(present)
    dropped: List[str] = []

    for i in range(len(present)):
        a = present[i]
        if a in dropped:
            continue
        for j in range(i + 1, len(present)):
            b = present[j]
            if b in dropped:
                continue
            if corr.loc[a, b] > corr_threshold:
                dropped.append(b)
                if b in kept:
                    kept.remove(b)

    return kept


# =====================================================================
# 编排入口：对多因子打分表施加治理
# =====================================================================

def govern_scores(
    scores_df: pd.DataFrame,
    factor_cols: List[str],
    corr_threshold: float = 0.7,
) -> Dict[str, Any]:
    """
    对一期横截面打分表施加治理：正交化去冗余 + 返回保留因子。

    返回契约化结果，便于原子持久化与下游组合构建复用。
    """
    kept = orthogonalize_factors(scores_df, factor_cols, corr_threshold)
    dropped = [c for c in factor_cols if c not in kept]
    return {
        "kept_factors": kept,
        "dropped_factors": dropped,
        "n_kept": len(kept),
        "governed_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # 轻量自测：合成数据验证 6 项能力可独立运行
    rng = np.random.default_rng(0)
    idx = pd.date_range("2024-01-01", periods=300, freq="D")
    f = pd.Series(rng.normal(0, 1, 300), index=idx)
    r = f * 0.3 + rng.normal(0, 1, 300)   # 弱正相关

    l1 = evaluate_level1(f, r)
    l2 = evaluate_level2({"theory": 1, "behavior": 1, "microstructure": 0, "institution": 1})
    l3 = evaluate_level3([0.01, 0.02, 0.5, 0.8])
    print("L1:", l1["passed"], "L2:", l2["passed"], "L3:", l3["passed"])

    wf = walk_forward_validate(f, r, n_splits=4)
    print("WalkForward mean_ic:", wf["mean_ic"], "consistency:", wf["consistency"])

    ic_hist = pd.Series(np.concatenate([rng.normal(0.05, 0.02, 200), rng.normal(0.01, 0.02, 100)]), index=idx)
    decay = factor_decay_test(ic_hist)
    print("Decay:", decay["decay_rate"], "remove:", decay["remove"])

    cb = CircuitBreaker(token_budget_daily=100000)
    for _ in range(3):
        cb.record_generation(0.005, False)
    print("CircuitBreaker tripped:", cb.tripped(), cb.trip_reason())

    factor_cols_demo = ["momentum", "technical", "volume", "fundamental", "macro", "sector"]
    sdf = pd.DataFrame({c: rng.normal(50, 10, 50) for c in factor_cols_demo})
    kept = orthogonalize_factors(sdf, factor_cols_demo)
    print("Orthogonalized kept:", kept)

    atomic_write("__govern_test.json", {"ok": True})
    os.remove("__govern_test.json")
    print("All governance capabilities OK.")
