"""
Load NYC school/program CSV and add site_name_clean from simple keyword rules.
CSV is expected next to this file: schooldata.csv
"""

from pathlib import Path

import pandas as pd


def add_site_name_clean(df: pd.DataFrame, site_col: str = "site_name") -> pd.DataFrame:
    """Add site_name_clean using keywords in the site name.

    Values: university, college, high_school, primary_school, school,
    other_institution, unknown.

    high_school and primary_school use extra patterns (e.g. PS/MS/IS numbers,
    middle school). Generic school / academy / charter with no level hint
    stays school.
    """
    s = df[site_col].fillna("").str.lower()
    out = df.copy()
    out["site_name_clean"] = "unknown"

    for word, kind in [
        ("university", "university"),
        ("college", "college"),
    ]:
        pick = s.str.contains(word, regex=False, na=False) & (
            out["site_name_clean"] == "unknown"
        )
        out.loc[pick, "site_name_clean"] = kind

    unk = out["site_name_clean"] == "unknown"

    high = (
        s.str.contains(r"high school|senior high|secondary school", regex=True, na=False)
        | s.str.contains(r"\bhs[\s.\-]*\d", regex=True, na=False)
    ) & unk
    out.loc[high, "site_name_clean"] = "High_school"

    unk = out["site_name_clean"] == "Unknown"
    primary = (
        s.str.contains(
            r"elementary|middle school|junior high|kindergarten|pre[-\s]?k|primary school|"
            r"k[-\s]to[-\s][58]\b|grades?\s*(?:pk|pre[-\s]?k|elementary)\b|"
            r"\bk[-\s](?:5|6|7|8)\b",
            regex=True,
            na=False,
        )
        | s.str.contains(
            r"\bps[\s.\-]*\d|\bms[\s.\-]*\d|\bis[\s.\-]*\d",
            regex=True,
            na=False,
        )
        | s.str.contains("j.h.s", regex=False, na=False)
        | s.str.contains("jhs", regex=False, na=False)
    ) & unk
    out.loc[primary, "site_name_clean"] = "Primary_school"

    unk = out["site_name_clean"] == "Not clear"
    for word, kind in [
        ("school", "Some kind ofschool"),
        ("academy", "Academy"),
        ("charter", "Charter school"),
        ("center", "Center"),
        ("institute", "Institute"),
        ("foundation", "Foundation"),
    ]:
        pick = s.str.contains(word, regex=False, na=False) & unk
        out.loc[pick, "site_name_clean"] = kind
        unk = out["site_name_clean"] == "unknown"

    return out


def main() -> None:
    base = Path(__file__).resolve().parent
    csv_path = base / "schooldata.csv"
    if not csv_path.exists():
        raise SystemExit(f"Missing CSV: {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = (
        df.columns.str.replace(r"\s+", " ", regex=True)
        .str.lower()
        .str.strip()
        .str.replace("/", "", regex=False)
        .str.replace(" ", "_")
    )
    df = df.rename(
        columns={
            "grade_level__age_group": "grade_level",
            "borough__community": "borough_community",
            "location_1": "location",
        }
    )

    df = add_site_name_clean(df)
    print(df["site_name_clean"].value_counts())
    print(df[["site_name", "site_name_clean"]].head(10))


if __name__ == "__main__":
    main()
