from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

TOTAL_EXPECTED = 398_524
TOP_ORIGINS = ["양서면", "양평읍", "서종면"]
CORE_DESTINATIONS = ["덕풍3동", "미사1동", "신장2동"]
TRANSFER_SCENARIOS = [0.05, 0.10, 0.20]


def read_inputs():
    return {
        "origins": pd.read_csv(DATA / "origin_totals.csv"),
        "od": pd.read_csv(DATA / "key_od.csv"),
        "purposes": pd.read_csv(DATA / "purpose_totals.csv"),
        "mode": pd.read_csv(DATA / "mode_inputs.csv"),
        "transit": pd.read_csv(DATA / "transit_supply.csv"),
    }


def metric(mode: pd.DataFrame, name: str) -> float:
    rows = mode.loc[mode["metric"] == name, "value"]
    if rows.empty:
        raise KeyError(f"missing mode metric: {name}")
    return float(rows.iloc[0])


def analyze_origins(origins: pd.DataFrame):
    total = int(origins["count"].sum())
    if total != TOTAL_EXPECTED:
        raise ValueError(f"origin total mismatch: {total:,} != {TOTAL_EXPECTED:,}")

    ranked = origins.sort_values("count", ascending=False).copy()
    ranked["share_pct"] = ranked["count"] / total * 100

    top3_count = int(
        ranked.loc[ranked["origin"].isin(TOP_ORIGINS), "count"].sum()
    )
    summary = pd.DataFrame(
        [{
            "total_movement": total,
            "top3_movement": top3_count,
            "top3_share_pct": top3_count / total * 100,
        }]
    )

    ranked.to_csv(OUT / "origin_ranking.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "origin_summary.csv", index=False, encoding="utf-8-sig")

    plot_df = ranked.sort_values("count")
    plt.figure(figsize=(9, 6))
    plt.barh(plot_df["origin"], plot_df["count"])
    plt.xlabel("Movement")
    plt.ylabel("Origin")
    plt.title("Yangpyeong origins to Hanam")
    plt.tight_layout()
    plt.savefig(OUT / "origin_totals.png", dpi=180)
    plt.close()
    return total, ranked, summary


def analyze_od(od: pd.DataFrame, total: int):
    ranked = od.sort_values("count", ascending=False).copy()
    ranked["od"] = ranked["origin"] + " → " + ranked["destination"]
    ranked["share_of_total_pct"] = ranked["count"] / total * 100

    core_mask = ranked["origin"].isin(TOP_ORIGINS) & ranked["destination"].isin(
        CORE_DESTINATIONS
    )
    core8_count = int(ranked.loc[core_mask, "count"].sum())

    destination = (
        ranked.loc[core_mask]
        .groupby("destination", as_index=False)["count"]
        .sum()
        .sort_values("count", ascending=False)
    )
    destination["share_within_core8_pct"] = (
        destination["count"] / core8_count * 100
    )

    ranked.to_csv(OUT / "key_od_ranking.csv", index=False, encoding="utf-8-sig")
    destination.to_csv(
        OUT / "destination_concentration.csv", index=False, encoding="utf-8-sig"
    )

    plot_df = ranked.sort_values("count")
    plt.figure(figsize=(10, 6))
    plt.barh(plot_df["od"], plot_df["count"])
    plt.xlabel("Movement")
    plt.ylabel("OD")
    plt.title("Key Yangpyeong-Hanam OD flows")
    plt.tight_layout()
    plt.savefig(OUT / "key_od.png", dpi=180)
    plt.close()

    return ranked, destination, core8_count


def analyze_purposes(purposes: pd.DataFrame, total: int):
    purpose_total = int(purposes["count"].sum())
    if purpose_total != total:
        raise ValueError(
            f"purpose total mismatch: {purpose_total:,} != {total:,}"
        )

    result = purposes.copy()
    result["share_pct"] = result["count"] / total * 100
    result = result.sort_values("count", ascending=False)
    result.to_csv(OUT / "purpose_summary.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(8, 5))
    plt.bar(result["purpose"], result["share_pct"])
    plt.ylabel("Share (%)")
    plt.xlabel("Purpose")
    plt.title("Movement purpose composition")
    plt.tight_layout()
    plt.savefig(OUT / "purpose_share.png", dpi=180)
    plt.close()
    return result


def analyze_mode_and_policy(mode: pd.DataFrame):
    total_movement = metric(mode, "total_movement")
    vehicle = metric(mode, "vehicle_movement")
    public = metric(mode, "public_transport_movement")
    other = metric(mode, "other_movement")
    avg_distance = metric(mode, "avg_vehicle_distance")
    avg_time = metric(mode, "avg_vehicle_time")
    vehicle_km = metric(mode, "vehicle_km")

    component_sum = vehicle + public + other
    if abs(component_sum - total_movement) > 0.05:
        raise ValueError(
            f"mode component mismatch: {component_sum:.2f} != {total_movement:.2f}"
        )

    mode_summary = pd.DataFrame(
        [{
            "vehicle_share_pct": vehicle / total_movement * 100,
            "public_transport_share_pct": public / total_movement * 100,
            "other_share_pct": other / total_movement * 100,
            "vehicle_to_public_ratio": vehicle / public,
            "avg_vehicle_distance_km": avg_distance,
            "avg_vehicle_time_min": avg_time,
            "simple_avg_speed_kmh": avg_distance / (avg_time / 60),
            "weekly_vehicle_km": vehicle_km,
        }]
    )
    mode_summary.to_csv(OUT / "mode_summary.csv", index=False, encoding="utf-8-sig")

    rows = []
    for rate in TRANSFER_SCENARIOS:
        weekly_movement = vehicle * rate
        weekly_km = vehicle_km * rate
        rows.append(
            {
                "transfer_rate_pct": int(rate * 100),
                "weekly_vehicle_movement_reduction": weekly_movement,
                "daily_vehicle_movement_reduction": weekly_movement / 7,
                "weekly_vehicle_km_reduction": weekly_km,
                "daily_vehicle_km_reduction": weekly_km / 7,
                "annual_vehicle_km_reduction_simple_52w": weekly_km * 52,
            }
        )

    scenarios = pd.DataFrame(rows)
    scenarios.to_csv(OUT / "policy_scenarios.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(7, 5))
    plt.bar(
        scenarios["transfer_rate_pct"].astype(str) + "%",
        scenarios["weekly_vehicle_km_reduction"],
    )
    plt.ylabel("Weekly vehicle-km reduction")
    plt.xlabel("Transfer scenario")
    plt.title("Vehicle-km reduction scenarios")
    plt.tight_layout()
    plt.savefig(OUT / "policy_scenarios.png", dpi=180)
    plt.close()

    return mode_summary, scenarios


def analyze_transit(transit: pd.DataFrame):
    result = transit.copy()
    result["seoul_to_hanam_supply_ratio"] = (
        result["seoul_weekday_runs"] / result["hanam_weekday_runs"]
    )
    result.to_csv(
        OUT / "transit_supply_comparison.csv", index=False, encoding="utf-8-sig"
    )

    x = range(len(result))
    width = 0.36
    plt.figure(figsize=(8, 5))
    plt.bar(
        [i - width / 2 for i in x],
        result["seoul_weekday_runs"],
        width=width,
        label="Seoul-bound",
    )
    plt.bar(
        [i + width / 2 for i in x],
        result["hanam_weekday_runs"],
        width=width,
        label="Hanam-bound",
    )
    plt.xticks(list(x), result["origin"])
    plt.ylabel("Weekday runs")
    plt.title("Representative bus supply comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "transit_supply.png", dpi=180)
    plt.close()
    return result


def main():
    data = read_inputs()
    total, _, origin_summary = analyze_origins(data["origins"])
    _, destination, core8_count = analyze_od(data["od"], total)
    purpose = analyze_purposes(data["purposes"], total)
    mode, scenarios = analyze_mode_and_policy(data["mode"])
    transit = analyze_transit(data["transit"])

    print(f"Total movement: {total:,}")
    print(
        f"Top 3 origins: {int(origin_summary.iloc[0]['top3_movement']):,} "
        f"({origin_summary.iloc[0]['top3_share_pct']:.2f}%)"
    )
    print(f"Core 8 OD: {core8_count:,} ({core8_count / total * 100:.2f}%)")
    print("\nDestination concentration")
    print(destination.to_string(index=False))
    print("\nPurpose")
    print(purpose.to_string(index=False))
    print("\nMode")
    print(mode.to_string(index=False))
    print("\nPolicy scenarios")
    print(scenarios.to_string(index=False))
    print("\nTransit supply")
    print(transit.to_string(index=False))


if __name__ == "__main__":
    main()
