"""Vectorized financial performance analytics engine powered by NumPy and pandas."""

from typing import Any, Dict, List
import numpy as np
import pandas as pd


def compute_portfolio_metrics(trades_df: pd.DataFrame, initial_capital: float = 10000.0) -> Dict[str, Any]:
    """Calculate comprehensive performance and risk metrics on closed trades."""
    if trades_df.empty or "pnl" not in trades_df.columns:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown_pct": 0.0,
            "max_drawdown_amount": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "expectancy_r": 0.0,
            "net_pnl": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "win_loss_ratio": 0.0,
            "final_equity": float(initial_capital),
        }

    # Ensure chronological sort
    df = trades_df.sort_values("entry_time").copy()
    pnls = df["pnl"].astype(float).to_numpy()
    total_trades = len(pnls)

    if total_trades == 0:
        return compute_portfolio_metrics(pd.DataFrame(), initial_capital)

    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]

    gross_profit = float(np.sum(wins)) if len(wins) > 0 else 0.0
    gross_loss = float(np.abs(np.sum(losses))) if len(losses) > 0 else 0.0
    net_pnl = float(np.sum(pnls))

    # 1. Win Rate
    win_rate = float((len(wins) / total_trades) * 100.0)

    # 2. Profit Factor
    if gross_loss > 0:
        profit_factor = round(gross_profit / gross_loss, 2)
    elif gross_profit > 0:
        profit_factor = 99.99  # Undefined high profit factor
    else:
        profit_factor = 0.0

    # 3. Average Win, Loss, and Win/Loss Ratio
    avg_win = float(np.mean(wins)) if len(wins) > 0 else 0.0
    avg_loss = float(np.abs(np.mean(losses))) if len(losses) > 0 else 0.0
    win_loss_ratio = round(avg_win / avg_loss, 2) if avg_loss > 0 else (avg_win if avg_win > 0 else 0.0)

    # 4. Equity Curve & Maximum Drawdown
    cumulative_pnl = np.cumsum(pnls)
    equity_curve = initial_capital + cumulative_pnl
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = running_max - equity_curve
    max_dd_amount = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

    # Drawdown percentage relative to peak
    drawdown_pcts = np.where(running_max > 0, (drawdowns / running_max) * 100.0, 0.0)
    max_dd_pct = float(np.max(drawdown_pcts)) if len(drawdown_pcts) > 0 else 0.0

    # 5. Annualized Sharpe Ratio (assuming risk-free rate = 0.0, normalized trade returns)
    returns = pnls / initial_capital
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1) if len(returns) > 1 else 0.0

    if std_return > 0:
        sharpe_ratio = round(float((mean_return / std_return) * np.sqrt(252)), 2)
    else:
        sharpe_ratio = 0.0

    # 6. Annualized Sortino Ratio (downside deviation only)
    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0:
        downside_std = np.sqrt(np.mean(downside_returns**2))
        sortino_ratio = round(float((mean_return / downside_std) * np.sqrt(252)), 2) if downside_std > 0 else 0.0
    else:
        sortino_ratio = 99.99 if mean_return > 0 else 0.0

    # 7. Expectancy in R-multiples
    if "r_multiple" in df.columns and df["r_multiple"].notna().any():
        r_vals = df["r_multiple"].dropna().to_numpy()
        expectancy_r = round(float(np.mean(r_vals)), 2) if len(r_vals) > 0 else 0.0
    else:
        expectancy_r = 0.0

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "profit_factor": profit_factor,
        "max_drawdown_pct": round(max_dd_pct, 2),
        "max_drawdown_amount": round(max_dd_amount, 2),
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "expectancy_r": expectancy_r,
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "win_loss_ratio": win_loss_ratio,
        "final_equity": round(float(equity_curve[-1]), 2),
    }


def compute_equity_series(trades_df: pd.DataFrame, initial_capital: float = 10000.0) -> List[Dict[str, Any]]:
    """Compute point-in-time equity curve and drawdown series for graphing."""
    if trades_df.empty or "pnl" not in trades_df.columns:
        return [{"trade_number": 0, "equity": initial_capital, "drawdown_pct": 0.0, "timestamp": None}]

    df = trades_df.sort_values("entry_time").copy()
    pnls = df["pnl"].astype(float).to_numpy()
    timestamps = df["entry_time"].astype(str).tolist()

    cumulative_pnl = np.cumsum(pnls)
    equity = initial_capital + cumulative_pnl
    running_max = np.maximum.accumulate(equity)
    drawdowns_pct = np.where(running_max > 0, ((running_max - equity) / running_max) * 100.0, 0.0)

    series = [{"trade_number": 0, "equity": round(initial_capital, 2), "drawdown_pct": 0.0, "timestamp": "Start"}]
    for i in range(len(pnls)):
        series.append({
            "trade_number": i + 1,
            "equity": round(float(equity[i]), 2),
            "drawdown_pct": round(float(drawdowns_pct[i]), 2),
            "pnl": round(float(pnls[i]), 2),
            "timestamp": timestamps[i],
        })

    return series


def compute_behavioral_matrix(trades_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Aggregate trading metrics grouped by emotional psychological state."""
    if trades_df.empty or "emotional_state" not in trades_df.columns:
        return []

    grouped = trades_df.groupby("emotional_state")
    matrix = []

    for state, group in grouped:
        pnls = group["pnl"].astype(float).to_numpy()
        wins = pnls[pnls > 0]
        losses = pnls[pnls < 0]

        total = len(pnls)
        win_rate = (len(wins) / total) * 100.0 if total > 0 else 0.0
        gross_profit = float(np.sum(wins)) if len(wins) > 0 else 0.0
        gross_loss = float(np.abs(np.sum(losses))) if len(losses) > 0 else 0.0

        if gross_loss > 0:
            pf = round(gross_profit / gross_loss, 2)
        elif gross_profit > 0:
            pf = 99.99
        else:
            pf = 0.0

        avg_r = (
            round(float(group["r_multiple"].dropna().mean()), 2)
            if "r_multiple" in group.columns and group["r_multiple"].notna().any()
            else 0.0
        )

        matrix.append({
            "emotional_state": state,
            "trade_count": total,
            "win_rate": round(win_rate, 2),
            "profit_factor": pf,
            "net_pnl": round(float(np.sum(pnls)), 2),
            "avg_r_multiple": avg_r,
        })

    # Sort by net pnl descending
    matrix.sort(key=lambda x: x["net_pnl"], reverse=True)
    return matrix
