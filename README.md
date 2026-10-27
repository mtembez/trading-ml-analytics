# Algorithmic Trading Journal & Behavioral ML Analytics Platform

[![Trading ML CI/CD](https://github.com/mtembez/trading-ml-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/mtembez/trading-ml-analytics/actions/workflows/ci.yml)
[![Coverage: 92%](https://img.shields.io/badge/Coverage-92%25-brightgreen.svg)](https://github.com/mtembez/trading-ml-analytics)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django 5.1](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade quantitative trading journal, vectorized performance engine, and behavioral machine learning platform. Built with **Django REST Framework**, **NumPy/pandas vectorized calculations**, **scikit-learn Random Forest classifier**, and a **React dashboard**.

> **Key Achievement**: Applied pandas and scikit-learn to model historical execution data, uncovering behavioral patterns (FOMO, revenge trading, risk compression) and deploying predictive pre-trade guardrails to improve trade selection through statistical analysis.

---

## Architecture Overview

```
                           +---------------------------------------+
                           |          React Vite Dashboard         |
                           |   (KPI Cards, SVG Equity Curve,       |
                           |    Pre-Trade Guardrail Evaluator)     |
                           +-------------------+-------------------+
                                               |
                                     REST API JSON Requests
                                               v
                           +---------------------------------------+
                           |       Django REST Framework API       |
                           |   (/trades/, /analytics/, /ml/)       |
                           +-------------------+-------------------+
                                               |
             +---------------------------------+---------------------------------+
             |                                                                   |
             v                                                                   v
+-----------------------------+                                     +-----------------------------+
| Vectorized Analytics Engine |                                     | Behavioral ML Engine        |
| (NumPy & pandas)            |                                     | (scikit-learn Random Forest)|
| - Win Rate & Profit Factor  |                                     | - Win Probability Scoring   |
| - Max Drawdown Curve        |                                     | - Pre-Trade Guardrails      |
| - Sharpe & Sortino Ratios   |                                     | - Tilt & Revenge Detection  |
| - Mathematical Expectancy   |                                     | - Behavioral Feature Vector |
+-----------------------------+                                     +-----------------------------+
             |                                                                   |
             +---------------------------------+---------------------------------+
                                               |
                                               v
                           +---------------------------------------+
                           |   PostgreSQL / SQLite Database        |
                           |  (Trade Schema, Referential Checks,   |
                           |   CheckConstraints for PnL & Risk)    |
                           +---------------------------------------+
```

---

## Mathematical Formulations

### 1. Realized Profit and Loss ($\text{PnL}$)
- **Long Positions**: $\text{PnL} = (\text{Exit Price} - \text{Entry Price}) \times \text{Quantity}$
- **Short Positions**: $\text{PnL} = (\text{Entry Price} - \text{Exit Price}) \times \text{Quantity}$

### 2. Risk-Normalized Return ($R$-Multiple)
$$\text{Risk} = |\text{Entry Price} - \text{Stop Loss}| \times \text{Quantity}$$
$$R = \frac{\text{Realized PnL}}{\text{Risk}}$$

### 3. Annualized Sharpe Ratio
$$\text{Sharpe} = \frac{\bar{r} - r_f}{\sigma_r} \times \sqrt{252}$$
Where $\bar{r}$ is the mean trade return, $r_f = 0.0$ is the risk-free benchmark, and $\sigma_r$ is return volatility.

### 4. Annualized Sortino Ratio
Penalizes exclusively harmful downside volatility rather than total variance:
$$\text{Sortino} = \frac{\bar{r} - r_f}{\sigma_{\text{downside}}} \times \sqrt{252}, \quad \sigma_{\text{downside}} = \sqrt{\frac{1}{N} \sum_{i=1}^N \min(r_i - r_f, 0)^2}$$

### 5. Peak-to-Trough Maximum Drawdown ($MDD$)
$$MDD = \max_{t} \left( \frac{\max_{\tau \le t} \text{Equity}_\tau - \text{Equity}_t}{\max_{\tau \le t} \text{Equity}_\tau} \right) \times 100$$

### 6. Mathematical Expectancy ($E$)
$$E = (W \times \bar{R}_{\text{win}}) - ((1 - W) \times \bar{R}_{\text{loss}})$$

---

## Machine Learning Behavioral Model (`ml/`)

The platform's **Random Forest Classifier** (`ml/models/trade_outcome_rf.joblib`) ingests clinical execution features to intercept psychological errors:
- **Planned Risk/Reward Asymmetry**: Intercepts trades where reward-to-risk drops below 1.0.
- **Emotional Bias Score**: Tracks emotional state (`disciplined` = 0.0, `fomo` = 2.2, `revenge` = 3.0).
- **Stress & Tilt Index**: Integrates consecutive losses to trigger mandatory cooldown guardrails.
- **Circadian & Session Timing**: Captures liquidity windows across London/New York market overlaps.

---

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/trades/` | List historical trades with symbol, asset class, and emotional filters |
| `POST` | `/api/v1/trades/` | Record new trade entry with automatic PnL and R-multiple calculation |
| `GET` | `/api/v1/analytics/overview/` | Vectorized portfolio metrics (Sharpe, Sortino, Win Rate, Drawdown) |
| `GET` | `/api/v1/analytics/equity-curve/` | Point-in-time cumulative equity and drawdown series for graphing |
| `GET` | `/api/v1/analytics/behavioral/` | Performance matrix grouped by emotional psychological state |
| `POST` | `/api/v1/ml/predict/` | Pre-trade machine learning win probability and guardrail assessment |

---

## Local Development & Testing

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Run Deterministic Pytest Suite (Coverage: 92%)
```bash
pytest -v --cov=apps --cov=ml --cov-report=term-missing
```

Output:
```text
============================== 15 passed in 2.89s ==============================
Coverage: 92%
```

### 4. Build Frontend
```bash
cd frontend
npm install
npm run build
```

---

## Author
**Simon M. Munyambu**  
GitHub: [@mtembez](https://github.com/mtembez)  
Email: simonmaeleq7@gmail.com
