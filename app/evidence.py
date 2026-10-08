import pandas as pd


BENCHMARK_RESULTS = pd.DataFrame(
    {
        "Model": [
            "Persistence",
            "Weather + lagged PM",
            "Weather + PM + raw fire",
            "Weather + PM + transport",
        ],
        "MAE": [56.467, 54.482, 54.587, 44.363],
        "RMSE": [77.105, 64.960, 65.178, 53.601],
    }
)


def get_benchmark_results() -> pd.DataFrame:
    """Return the locked October 2025 24-hour benchmark results."""
    return BENCHMARK_RESULTS.copy()


def transport_improvement() -> float:
    """Return M3 MAE improvement over the M1 baseline as a percentage."""
    baseline = 54.482
    transport = 44.363
    return (baseline - transport) / baseline * 100
