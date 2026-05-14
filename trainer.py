import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import config
import data_manager
from braid_invariants import compute_braid_complexity

def main():
    if not config.HF_TOKEN:
        print("HF_TOKEN not set")
        return

    df = data_manager.load_master_data()
    all_results = {}
    today = datetime.now().strftime("%Y-%m-%d")

    for universe_name, tickers in config.UNIVERSES.items():
        print(f"\n=== Universe: {universe_name} (Braid Invariants) ===")
        prices = data_manager.prepare_price_matrix(df, tickers)
        if prices.empty or len(prices) < max(config.WINDOWS) + 10:
            print("  Insufficient data")
            all_results[universe_name] = {"top_etfs": []}
            continue

        # Store best per ETF across windows (lowest crossing count)
        best_per_etf = {}  # ticker -> (best_crossings, best_window)
        window_results = {}

        for win in config.WINDOWS:
            if len(prices) < win:
                continue
            window_prices = prices.iloc[-win:]
            crossing_counts, total_crossings = compute_braid_complexity(window_prices)
            window_results[win] = {
                "total_crossings": total_crossings,
                "crossing_counts": crossing_counts
            }
            print(f"  Window {win}d: total crossings = {total_crossings}")
            # Update best per ETF
            for ticker, count in crossing_counts.items():
                if ticker not in best_per_etf or count < best_per_etf[ticker][0]:
                    best_per_etf[ticker] = (count, win)

        if not best_per_etf:
            print("  No valid windows")
            all_results[universe_name] = {"top_etfs": []}
            continue

        # Sort ETFs by best crossing count (ascending) -> lower = more ordered
        sorted_etfs = sorted(best_per_etf.items(), key=lambda x: x[1][0])
        top_etfs = []
        full_scores = {}
        for ticker, (count, win) in sorted_etfs[:config.TOP_N]:
            top_etfs.append({
                "ticker": ticker,
                "best_crossings": int(count),
                "window": win
            })
            full_scores[ticker] = {
                "best_crossings": int(count),
                "best_window": win
            }
        print(f"  Top 3 ETFs (lowest crossing counts): {[e['ticker'] for e in top_etfs]}")
        all_results[universe_name] = {
            "top_etfs": top_etfs,
            "full_scores": full_scores,
            "window_results": window_results,
            "run_date": today
        }

    Path("results").mkdir(exist_ok=True)
    local_path = Path(f"results/braid_{today}.json")
    with open(local_path, "w") as f:
        json.dump({"run_date": today, "universes": all_results}, f, indent=2)

    import push_results
    push_results.push_daily_result(local_path)
    print("\n=== Topological Braid / Knot Invariants Engine complete ===")

if __name__ == "__main__":
    main()
