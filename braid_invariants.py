import numpy as np
import pandas as pd

def compute_crossing_counts(prices_df):
    """
    For a DataFrame of daily prices (columns = ETFs, index = dates),
    compute the number of times each ETF swaps rank with another ETF
    (i.e., the number of crossings it participates in).
    Also returns total crossing count (universe complexity).
    """
    # Normalize each price series to start at 0 (cumulative return)
    # Actually use cumulative log returns to make paths comparable
    cumulative_returns = np.log(prices_df / prices_df.iloc[0])
    # Get ranks each day (higher cumulative return = higher rank)
    ranks = cumulative_returns.rank(axis=1, method='dense', ascending=False).astype(int)
    n_etfs = prices_df.shape[1]
    # Initialize crossing counts per ETF
    crossing_counts = {col: 0 for col in prices_df.columns}
    total_crossings = 0
    # Iterate over consecutive days
    for i in range(1, len(ranks)):
        prev = ranks.iloc[i-1]
        curr = ranks.iloc[i]
        # Find swaps: pairs (a,b) where rank order changed
        # Simple: for each ETF, if its rank changed, count crossing with the other ETF that swapped
        # We'll compute by comparing order lists
        prev_order = list(prev.sort_values().index)
        curr_order = list(curr.sort_values().index)
        # Use inversion counting between permutations?
        # For each pair, if relative order changes, that's a crossing.
        for j in range(n_etfs):
            for k in range(j+1, n_etfs):
                etf_j = prev_order[j]
                etf_k = prev_order[k]
                # Find positions of these ETFs in current order
                pos_j = curr_order.index(etf_j)
                pos_k = curr_order.index(etf_k)
                if pos_j > pos_k:  # order reversed
                    crossing_counts[etf_j] += 1
                    crossing_counts[etf_k] += 1
                    total_crossings += 1
    return crossing_counts, total_crossings

def compute_braid_complexity(prices_df):
    """Return ETF crossing counts and total crossings for a given window."""
    crossing_counts, total_crossings = compute_crossing_counts(prices_df)
    return crossing_counts, total_crossings
