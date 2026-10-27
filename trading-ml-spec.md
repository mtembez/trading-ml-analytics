# Algorithmic Trading Journal & Behavioral ML Analytics Platform: Technical Specification

## System Overview
An enterprise-grade quantitative trading journal and statistical analytics platform. Combines Django REST Framework, vectorized NumPy/pandas portfolio metrics (Win Rate, Profit Factor, Max Drawdown, Sharpe Ratio, Sortino Ratio, Expectancy), and a scikit-learn Machine Learning behavioral model predicting trade outcome probabilities and detecting emotional trading biases (e.g. FOMO, revenge trading).

## Mathematical Formulations
1. **Realized PnL**:
   - For `LONG`: $\text{PnL} = (\text{exit\_price} - \text{entry\_price}) \times \text{quantity}$
   - For `SHORT`: $\text{PnL} = (\text{entry\_price} - \text{exit\_price}) \times \text{quantity}$

2. **R-Multiple ($R$)**:
   - Initial Dollar Risk: $\text{Risk} = |\text{entry\_price} - \text{stop\_loss}| \times \text{quantity}$
   - $R = \frac{\text{Realized PnL}}{\text{Risk}}$

3. **Win Rate ($W$)**:
   - $W = \frac{N_{\text{wins}}}{N_{\text{total}}} \times 100$

4. **Profit Factor ($PF$)**:
   - $PF = \frac{\sum \text{Gross Profit}}{|\sum \text{Gross Loss}|}$

5. **Maximum Drawdown ($MDD$)**:
   - $MDD = \max_{t} \left( \frac{\text{Peak}_t - \text{Equity}_t}{\text{Peak}_t} \right) \times 100$

6. **Annualized Sharpe Ratio**:
   - $\text{Sharpe} = \frac{\bar{r} - r_f}{\sigma_r} \times \sqrt{252}$

7. **Annualized Sortino Ratio**:
   - $\text{Sortino} = \frac{\bar{r} - r_f}{\sigma_{\text{downside}}} \times \sqrt{252}$ where $\sigma_{\text{downside}} = \sqrt{\frac{1}{N} \sum \min(r_i - r_f, 0)^2}$

8. **Mathematical Expectancy ($E$)**:
   - $E = (W \times \bar{R}_{\text{win}}) - ((1 - W) \times \bar{R}_{\text{loss}})$
