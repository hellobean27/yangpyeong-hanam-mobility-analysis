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
    assert math.isclose(top3 / 398_524 * 100, 65.7441, abs_tol=0.01)


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


def test_mode_shares_and_policy():
    df = pd.read_csv(DATA / "mode_inputs.csv").set_index("metric")
    total = float(df.loc["total_movement", "value"])
    vehicle = float(df.loc["vehicle_movement", "value"])
    public = float(df.loc["public_transport_movement", "value"])
    other = float(df.loc["other_movement", "value"])
    vehicle_km = float(df.loc["vehicle_km", "value"])

    assert math.isclose(vehicle + public + other, total, abs_tol=0.05)
    assert math.isclose(vehicle / total * 100, 98.7563, abs_tol=0.001)
    assert math.isclose(public / total * 100, 0.9081, abs_tol=0.001)
    assert math.isclose(vehicle_km * 0.05, 74_977.15, abs_tol=0.1)
    assert math.isclose(vehicle_km * 0.10, 149_954.3, abs_tol=0.1)
    assert math.isclose(vehicle_km * 0.20, 299_908.6, abs_tol=0.1)
