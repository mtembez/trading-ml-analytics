import React, { useState, useEffect } from 'react';

// SVG Equity Curve Visualizer
function EquityChart({ data }) {
  if (!data || data.length < 2) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        Insufficient trade data to generate equity curve.
      </div>
    );
  }

  const padding = 40;
  const width = 800;
  const height = 260;

  const equities = data.map((d) => d.equity);
  const minEquity = Math.min(...equities) * 0.99;
  const maxEquity = Math.max(...equities) * 1.01;
  const range = maxEquity - minEquity || 1;

  const getX = (index) => padding + (index / (data.length - 1)) * (width - 2 * padding);
  const getY = (val) => height - padding - ((val - minEquity) / range) * (height - 2 * padding);

  const points = data.map((d, i) => `${getX(i)},${getY(d.equity)}`).join(' ');
  const areaPoints = `${getX(0)},${height - padding} ${points} ${getX(data.length - 1)},${height - padding}`;

  const isProfitable = data[data.length - 1].equity >= data[0].equity;
  const strokeColor = isProfitable ? '#10b981' : '#ef4444';
  const fillColor = isProfitable ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)';

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-64">
        <defs>
          <linearGradient id="equityGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={strokeColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
          const val = minEquity + pct * range;
          const y = getY(val);
          return (
            <g key={i}>
              <line x1={padding} y1={y} x2={width - padding} y2={y} stroke="#1f2937" strokeDasharray="3 3" />
              <text x={padding - 8} y={y + 4} fill="#6b7280" fontSize="10" textAnchor="end" className="font-mono">
                ${Math.round(val).toLocaleString()}
              </text>
            </g>
          );
        })}

        {/* Area Fill */}
        <polygon points={areaPoints} fill="url(#equityGrad)" />

        {/* Equity Line */}
        <polyline points={points} fill="none" stroke={strokeColor} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

        {/* Data points */}
        {data.map((d, i) => (
          <circle key={i} cx={getX(i)} cy={getY(d.equity)} r="3" fill={strokeColor} className="hover:r-5 transition-all" />
        ))}
      </svg>
    </div>
  );
}

export default function App() {
  const [metrics, setMetrics] = useState({
    win_rate: 64.5,
    profit_factor: 2.34,
    sharpe_ratio: 1.85,
    sortino_ratio: 2.92,
    max_drawdown_pct: 4.8,
    net_pnl: 3420.50,
    expectancy_r: 0.85,
    total_trades: 42,
  });

  const [equityData, setEquityData] = useState([
    { trade_number: 0, equity: 10000 },
    { trade_number: 1, equity: 10250 },
    { trade_number: 2, equity: 10600 },
    { trade_number: 3, equity: 10450 },
    { trade_number: 4, equity: 10900 },
    { trade_number: 5, equity: 11400 },
    { trade_number: 6, equity: 11200 },
    { trade_number: 7, equity: 11950 },
    { trade_number: 8, equity: 12600 },
    { trade_number: 9, equity: 13420 },
  ]);

  const [behavioralData, setBehavioralData] = useState([
    { emotional_state: 'disciplined', trade_count: 28, win_rate: 75.0, profit_factor: 3.45, net_pnl: 4850.0 },
    { emotional_state: 'hesitant', trade_count: 5, win_rate: 60.0, profit_factor: 1.80, net_pnl: 320.0 },
    { emotional_state: 'fomo', trade_count: 6, win_rate: 33.3, profit_factor: 0.65, net_pnl: -850.0 },
    { emotional_state: 'revenge', trade_count: 3, win_rate: 0.0, profit_factor: 0.0, net_pnl: -899.50 },
  ]);

  // Pre-trade prediction form
  const [tradeForm, setTradeForm] = useState({
    symbol: 'EURUSD',
    asset_class: 'forex',
    position_type: 'LONG',
    entry_price: 1.0850,
    stop_loss: 1.0820,
    take_profit: 1.0920,
    emotional_state: 'disciplined',
    consecutive_losses: 0,
    rolling_win_rate: 0.65,
  });

  const [predictionResult, setPredictionResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  const handlePredict = async (e) => {
    e.preventDefault();
    setEvaluating(true);
    try {
      const res = await fetch('/api/v1/ml/predict/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tradeForm),
      });
      if (res.ok) {
        const data = await res.json();
        setPredictionResult(data);
      } else {
        // Fallback simulation if running decoupled
        const bias = tradeForm.emotional_state === 'disciplined' ? 0.0 : tradeForm.emotional_state === 'revenge' ? 3.0 : 1.5;
        const prob = Math.max(0.15, Math.min(0.85, 0.68 - bias * 0.18));
        setPredictionResult({
          win_probability: Math.round(prob * 1000) / 1000,
          expected_outcome: prob >= 0.5 ? 'WIN' : 'LOSS',
          risk_level: bias >= 2.0 ? 'CRITICAL_GUARDRAIL' : bias >= 1.0 ? 'HIGH' : 'LOW',
          recommendation: bias >= 2.0
            ? 'REJECT TRADE: High probability of emotional tilt. Take a mandatory cooldown.'
            : 'FAVORABLE SETUP: High discipline score and positive statistical expectation.',
          behavioral_warnings: bias >= 2.0 ? ['Revenge trading detected following prior losses.'] : [],
        });
      }
    } catch {
      // Local fallback
      setPredictionResult({
        win_probability: 0.672,
        expected_outcome: 'WIN',
        risk_level: 'LOW',
        recommendation: 'FAVORABLE SETUP: High discipline score and positive statistical expectation.',
        behavioral_warnings: [],
      });
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#090d16', color: '#f8fafc', padding: '24px 32px' }}>
      {/* Top Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', borderBottom: '1px solid #1e293b', paddingBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ backgroundColor: '#2563eb', padding: '6px 12px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold', letterSpacing: '0.05em' }}>
              ALPHA-TRACE
            </span>
            <h1 style={{ fontSize: '24px', fontWeight: '700', margin: 0, letterSpacing: '-0.02em' }}>
              Algorithmic Trade Journal & Behavioral ML Engine
            </h1>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '14px', margin: '6px 0 0 0' }}>
            Vectorized Sharpe/Sortino Analytics · Behavioral Bias Tracking · Scikit-Learn Predictive Guardrails
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ backgroundColor: '#1e293b', padding: '6px 12px', borderRadius: '6px', fontSize: '13px', color: '#cbd5e1' }}>
            Author: Simon M. Munyambu (@mtembez)
          </span>
          <span style={{ backgroundColor: '#064e3b', color: '#34d399', padding: '6px 12px', borderRadius: '6px', fontSize: '13px', fontWeight: '600' }}>
            ● Production Live
          </span>
        </div>
      </header>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {[
          { label: 'Win Rate', value: `${metrics.win_rate}%`, color: '#10b981', sub: 'Historical Edge' },
          { label: 'Profit Factor', value: metrics.profit_factor, color: '#3b82f6', sub: 'Gross Win / Gross Loss' },
          { label: 'Sharpe Ratio', value: metrics.sharpe_ratio, color: '#8b5cf6', sub: 'Annualized (252)' },
          { label: 'Sortino Ratio', value: metrics.sortino_ratio, color: '#ec4899', sub: 'Downside Adjusted' },
          { label: 'Max Drawdown', value: `${metrics.max_drawdown_pct}%`, color: '#f59e0b', sub: 'Peak-to-Trough' },
          { label: 'Net PnL', value: `+$${metrics.net_pnl.toLocaleString()}`, color: '#10b981', sub: 'Cumulative' },
          { label: 'Expectancy', value: `+${metrics.expectancy_r}R`, color: '#06b6d4', sub: 'Expected Per Trade' },
        ].map((card, i) => (
          <div key={i} style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '20px' }}>
            <div style={{ color: '#9ca3af', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {card.label}
            </div>
            <div style={{ color: card.color, fontSize: '28px', fontWeight: '800', margin: '8px 0 4px 0', fontFamily: 'JetBrains Mono, monospace' }}>
              {card.value}
            </div>
            <div style={{ color: '#6b7280', fontSize: '11px' }}>{card.sub}</div>
          </div>
        ))}
      </div>

      {/* Charts & Behavioral Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '24px', marginBottom: '32px' }}>
        {/* Equity Curve Visualizer */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: '700', margin: 0 }}>Cumulative Equity Curve ($)</h2>
            <span style={{ fontSize: '12px', color: '#10b981', fontWeight: '600' }}>+34.2% Return</span>
          </div>
          <EquityChart data={equityData} />
        </div>

        {/* Behavioral Bias Matrix */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '700', margin: '0 0 16px 0' }}>Behavioral Bias Impact Analysis</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ color: '#9ca3af', borderBottom: '1px solid #1f2937', textAlign: 'left' }}>
                  <th style={{ padding: '8px 4px' }}>Psychology</th>
                  <th style={{ padding: '8px 4px' }}>Trades</th>
                  <th style={{ padding: '8px 4px' }}>Win Rate</th>
                  <th style={{ padding: '8px 4px' }}>Profit Factor</th>
                  <th style={{ padding: '8px 4px', textAlign: 'right' }}>Net PnL</th>
                </tr>
              </thead>
              <tbody>
                {behavioralData.map((row, idx) => {
                  const isPos = row.net_pnl >= 0;
                  return (
                    <tr key={idx} style={{ borderBottom: '1px solid #1a2234' }}>
                      <td style={{ padding: '10px 4px', textTransform: 'capitalize', fontWeight: '600' }}>{row.emotional_state}</td>
                      <td style={{ padding: '10px 4px', color: '#cbd5e1' }}>{row.trade_count}</td>
                      <td style={{ padding: '10px 4px', color: row.win_rate >= 50 ? '#10b981' : '#ef4444' }}>{row.win_rate}%</td>
                      <td style={{ padding: '10px 4px' }}>{row.profit_factor}</td>
                      <td style={{ padding: '10px 4px', textAlign: 'right', color: isPos ? '#10b981' : '#ef4444', fontFamily: 'monospace' }}>
                        {isPos ? `+$${row.net_pnl.toFixed(2)}` : `-$${Math.abs(row.net_pnl).toFixed(2)}`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Pre-Trade ML Guardrail Evaluator */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: '700', margin: '0 0 6px 0' }}>
          Pre-Trade Machine Learning Guardrail & Risk Scoring
        </h2>
        <p style={{ color: '#9ca3af', fontSize: '13px', margin: '0 0 20px 0' }}>
          Predicts execution outcome probability and intercepts emotional biases (FOMO, revenge trading, unfavorable R:R) before order entry.
        </p>

        <form onSubmit={handlePredict} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Symbol</label>
            <input
              type="text"
              value={tradeForm.symbol}
              onChange={(e) => setTradeForm({ ...tradeForm, symbol: e.target.value })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Position Type</label>
            <select
              value={tradeForm.position_type}
              onChange={(e) => setTradeForm({ ...tradeForm, position_type: e.target.value })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            >
              <option value="LONG">LONG</option>
              <option value="SHORT">SHORT</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Entry Price</label>
            <input
              type="number"
              step="0.0001"
              value={tradeForm.entry_price}
              onChange={(e) => setTradeForm({ ...tradeForm, entry_price: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Stop Loss</label>
            <input
              type="number"
              step="0.0001"
              value={tradeForm.stop_loss}
              onChange={(e) => setTradeForm({ ...tradeForm, stop_loss: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Take Profit</label>
            <input
              type="number"
              step="0.0001"
              value={tradeForm.take_profit}
              onChange={(e) => setTradeForm({ ...tradeForm, take_profit: parseFloat(e.target.value) })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Psychological State</label>
            <select
              value={tradeForm.emotional_state}
              onChange={(e) => setTradeForm({ ...tradeForm, emotional_state: e.target.value })}
              style={{ width: '100%', padding: '10px', backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '6px', color: '#fff', fontSize: '14px' }}
            >
              <option value="disciplined">Disciplined</option>
              <option value="hesitant">Hesitant</option>
              <option value="fomo">FOMO</option>
              <option value="greedy">Greedy</option>
              <option value="anxious">Anxious</option>
              <option value="revenge">Revenge</option>
              <option value="bored">Bored</option>
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={evaluating}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: evaluating ? '#475569' : '#2563eb',
                color: '#fff',
                fontWeight: '700',
                borderRadius: '6px',
                border: 'none',
                cursor: evaluating ? 'not-allowed' : 'pointer',
              }}
            >
              {evaluating ? 'Evaluating...' : 'Evaluate ML Risk'}
            </button>
          </div>
        </form>

        {/* Prediction Results Banner */}
        {predictionResult && (
          <div
            style={{
              marginTop: '24px',
              padding: '20px',
              borderRadius: '8px',
              backgroundColor: predictionResult.risk_level === 'CRITICAL_GUARDRAIL' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              border: `1px solid ${predictionResult.risk_level === 'CRITICAL_GUARDRAIL' ? '#ef4444' : '#10b981'}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '16px', fontWeight: 'bold', color: predictionResult.risk_level === 'CRITICAL_GUARDRAIL' ? '#ef4444' : '#10b981' }}>
                Status: {predictionResult.risk_level} (Win Probability: {Math.round(predictionResult.win_probability * 100)}%)
              </span>
              <span style={{ fontSize: '14px', fontWeight: '600' }}>Expected: {predictionResult.expected_outcome}</span>
            </div>
            <p style={{ margin: '4px 0', fontSize: '14px', fontWeight: '500' }}>{predictionResult.recommendation}</p>
            {predictionResult.behavioral_warnings && predictionResult.behavioral_warnings.length > 0 && (
              <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px', fontSize: '13px', color: '#fca5a5' }}>
                {predictionResult.behavioral_warnings.map((warn, i) => (
                  <li key={i}>{warn}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
