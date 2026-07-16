# Notebooks

Analysis notebooks, in execution order. Reusable logic lives in `src/`; notebooks stay
focused on exploration, narrative, and visualization.

| Notebook | Task | Purpose |
|---|---|---|
| `01_data_exploration.ipynb` | Task 1 | Load & validate the unified dataset, explore the schema, document enrichment |
| `02_eda.ipynb` | Task 2 | Temporal coverage, Access/Usage trends, event overlays, correlations, key insights |
| `03_event_impact_modeling.ipynb` | Task 3 | Event-indicator association matrix, effect functions, historical validation |
| `04_forecasting.ipynb` | Task 4 | 2025–2027 forecasts with scenarios and confidence intervals |

Run from the repository root so `src/` imports resolve:

```bash
jupyter lab
```
