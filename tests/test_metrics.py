import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def test_origin_total_and_top3():
    df = pd.read_csv(DATA / "origin_totals.csv")
    assert int(df["count"].sum()) == 398_524
    top3 = df[df["origin"].isin(["양서면", "양평읍", "서종면"])]["count"].sum()
    assert int(top3) == 262_010
    assert math.isclose(top3 / 398_524 * 100, 65.7451, abs_tol=0.01)


def test_purpose_total():
    df = pd.read_csv(DATA / "purpose_totals.csv")
    assert int(df["count"].sum()) == 398_524


def test_core8_od():
    df = pd.read_csv(DATA / "key_od.csv")
    core = df[
        df["origin"].isin(["양서면", "양평읍", "서종면"])
        & df["destination"].isin(["덕풍3동", "미사1동", "신장2동"])
    ]
    assert int(core["count"].sum()) == 151_872
    assert math.isclose(151_872 / 398_524 * 100, 38.1086, abs_tol=0.01)


def test_mode_shares_person_km_and_carbon():
    df = pd.read_csv(DATA / "mode_inputs.csv").set_index("metric")
    total = float(df.loc["total_movement", "value"])
    vehicle = float(df.loc["vehicle_movement", "value"])
    public = float(df.loc["public_transport_movement", "value"])
    other = float(df.loc["other_movement", "value"])
    avg_distance = float(df.loc["avg_vehicle_distance", "value"])
    person_km = float(df.loc["vehicle_mode_person_km", "value"])

    assert math.isclose(vehicle + public + other, total, abs_tol=0.05)
    assert math.isclose(vehicle / total * 100, 98.7563, abs_tol=0.001)
    assert math.isclose(public / total * 100, 0.9081, abs_tol=0.001)
    assert math.isclose(vehicle * avg_distance, person_km, abs_tol=2)

    net_factor = 0.2111 - 0.0291
    assert math.isclose(person_km * 0.05 * net_factor / 1000, 13.6458, abs_tol=0.01)
    assert math.isclose(person_km * 0.10 * net_factor / 1000, 27.2917, abs_tol=0.01)
    assert math.isclose(person_km * 0.20 * net_factor / 1000, 54.5834, abs_tol=0.01)


def test_equity_inputs():
    origins = pd.read_csv(DATA / "origin_totals.csv")
    equity = pd.read_csv(DATA / "equity_inputs.csv")
    df = origins.merge(equity, on="origin", validate="one_to_one")

    assert int(df["population_2026_08"].sum()) == 127_137
    no_hub = df[~df["fixed_hub"]]
    assert int(no_hub["population_2026_08"].sum()) == 23_632
    assert int(no_hub["count"].sum()) == 56_224


def test_service_scenario_max_gap():
    df = pd.read_csv(DATA / "service_scenario.csv")

    def to_min(s):
        h, m = map(int, s.split(":"))
        return h * 60 + m

    def max_gap(s):
        values = sorted(to_min(x) for x in s.split("|"))
        return max(b - a for a, b in zip(values, values[1:]))

    current = df.loc[df["scenario"] == "current", "departures"].iloc[0]
    proposal = df.loc[df["scenario"] == "proposal", "departures"].iloc[0]
    assert max_gap(current) == 405
    assert max_gap(proposal) == 120


def test_time_demand_and_service_proxy_inputs():
    demand = pd.read_csv(DATA / "time_demand_hanam.csv")
    assert math.isclose(
        float(demand.loc[demand["time"] == "14:00", "vehicle_daily_avg"].iloc[0]),
        659.136,
        abs_tol=0.001,
    )
    service = pd.read_csv(DATA / "service_scenario.csv")
    assert int(service.loc[service["scenario"] == "current", "weekday_runs"].iloc[0]) == 3
    assert int(service.loc[service["scenario"] == "proposal", "weekday_runs"].iloc[0]) == 8
