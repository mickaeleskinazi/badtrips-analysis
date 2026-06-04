from __future__ import annotations

import csv
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


TARGET_GROUPS = [
    "psilocybin_mushrooms",
    "lsd_lysergamides",
    "dmt_ayahuasca_5meo",
    "other_tryptamines",
    "phenethylamines_2c_nbome_dox",
    "mdma_entactogens",
    "amphetamine_like_stimulants",
    "cannabis_natural",
    "synthetic_cannabinoids",
    "ketamine_pcp_arylcyclohexylamines",
    "dxm",
    "salvia",
    "deliriants_anticholinergics",
    "benzodiazepines_zdrugs_sedatives",
    "opioids",
    "alcohol",
]

MARKERS = [
    "interoceptive_threat",
    "fear_of_death",
    "fear_of_madness",
    "loss_of_control",
    "derealization_depersonalization",
    "paranoia_social_threat",
    "time_distortion",
    "medical_intervention",
    "social_support",
    "acceptance_surrender",
    "integration_positive_afterwards",
]

CONTROL_COLUMNS = [
    "log_word_count",
    "multi_target_group",
    "exp_year_z",
    "age_z",
    "age_available",
    "gender_female",
    "gender_other_or_unclear",
    "context_alone",
    "context_with_others",
    "first_time",
    "experienced_user",
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def add_target_group_dummies(df: pd.DataFrame) -> pd.DataFrame:
    target_text = df["target_groups"].fillna("")
    for group in TARGET_GROUPS:
        df[f"group__{group}"] = target_text.str.contains(fr"(?:^|\s\|\s){group}(?:$|\s\|\s)", regex=True).astype(int)
    return df


def prepare_analysis_table(
    report_codes_path: Path,
    covariates_path: Path,
    doses_path: Path | None = None,
) -> pd.DataFrame:
    codes = read_csv(report_codes_path)
    covars = read_csv(covariates_path)
    df = codes.merge(covars.drop(columns=["target_groups", "families"], errors="ignore"), on="report_id", how="left")

    if doses_path and doses_path.exists():
        doses = read_csv(doses_path)
        df = df.merge(doses.drop(columns=["target_groups"], errors="ignore"), on="report_id", how="left")

    for column in MARKERS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

    numeric_columns = [
        "age",
        "exp_year",
        "word_count",
        "multi_target_group",
        "context_alone",
        "context_with_others",
        "first_time",
        "experienced_user",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["log_word_count"] = np.log1p(df["word_count"].fillna(df["word_count"].median()))
    df["multi_target_group"] = df["multi_target_group"].fillna(0).astype(int)
    df["age_available"] = df["age"].between(12, 80).astype(int)
    valid_age = df["age"].where(df["age"].between(12, 80))
    df["age_z"] = zscore(valid_age.fillna(valid_age.median()))
    df["exp_year_z"] = zscore(df["exp_year"].fillna(df["exp_year"].median()))

    gender = df["gender"].fillna("")
    df["gender_female"] = (gender == "female").astype(int)
    df["gender_other_or_unclear"] = (gender == "other_or_unclear").astype(int)

    for column in ["context_alone", "context_with_others", "first_time", "experienced_user"]:
        df[column] = df[column].fillna(0).astype(int)

    df = add_target_group_dummies(df)

    for column in [
        "dose_max_mg",
        "dose_max_ug",
        "dose_max_g",
        "dose_max_ml",
        "dose_max_blotter",
        "dose_max_drop",
        "dose_max_pill",
        "dose_max_capsule",
        "dose_max_count",
    ]:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def zscore(series: pd.Series) -> pd.Series:
    std = series.std()
    if not std or math.isnan(std):
        return series * 0
    return (series - series.mean()) / std


def fit_logistic(df: pd.DataFrame, outcome: str, predictors: list[str]) -> pd.DataFrame:
    model_df = df[[outcome, *predictors]].dropna().copy()
    y = model_df[outcome].astype(float)
    x = model_df[predictors].astype(float)
    x = sm.add_constant(x, has_constant="add")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = sm.GLM(y, x, family=sm.families.Binomial()).fit(maxiter=200)

    conf = result.conf_int()
    rows = []
    for term in result.params.index:
        if term == "const":
            continue
        estimate = result.params[term]
        rows.append(
            {
                "term": term,
                "odds_ratio": math.exp(estimate),
                "ci_low": math.exp(conf.loc[term, 0]),
                "ci_high": math.exp(conf.loc[term, 1]),
                "p_value": result.pvalues[term],
                "n": int(result.nobs),
                "outcome_rate": float(y.mean()),
            }
        )
    return pd.DataFrame(rows)


def write_model_table(path: Path, table: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rounded = table.copy()
    for column in ["odds_ratio", "ci_low", "ci_high", "p_value", "outcome_rate"]:
        rounded[column] = rounded[column].astype(float).round(4)
    rounded.to_csv(path, index=False)


def group_predictors() -> list[str]:
    return [f"group__{group}" for group in TARGET_GROUPS]


def run_core_models(df: pd.DataFrame, output_dir: Path) -> dict[str, pd.DataFrame]:
    groups = group_predictors()
    models = {
        "fear_of_death": [
            "interoceptive_threat",
            "loss_of_control",
            "derealization_depersonalization",
            *groups,
            *CONTROL_COLUMNS,
        ],
        "acceptance_surrender": [
            "fear_of_death",
            "interoceptive_threat",
            "loss_of_control",
            "derealization_depersonalization",
            "social_support",
            "medical_intervention",
            *groups,
            *CONTROL_COLUMNS,
        ],
        "integration_positive_afterwards": [
            "acceptance_surrender",
            "fear_of_death",
            "social_support",
            "medical_intervention",
            *groups,
            *CONTROL_COLUMNS,
        ],
        "medical_intervention": [
            "fear_of_death",
            "interoceptive_threat",
            "loss_of_control",
            *groups,
            *CONTROL_COLUMNS,
        ],
    }

    tables = {}
    for outcome, predictors in models.items():
        table = fit_logistic(df, outcome, predictors)
        tables[outcome] = table
        write_model_table(output_dir / f"model_{outcome}_odds_ratios.csv", table)
    return tables


def prevalence_rate(df: pd.DataFrame, mask: pd.Series, outcome: str) -> float:
    subset = df.loc[mask, outcome]
    if subset.empty:
        return float("nan")
    return float(subset.mean() * 100)


def write_let_go_pathway(path: Path, df: pd.DataFrame) -> None:
    rows = []
    comparisons = [
        ("fear_of_death_present", df["fear_of_death"] == 1),
        ("fear_of_death_absent", df["fear_of_death"] == 0),
        ("interoceptive_threat_present", df["interoceptive_threat"] == 1),
        ("loss_of_control_present", df["loss_of_control"] == 1),
        ("derealization_present", df["derealization_depersonalization"] == 1),
        ("social_support_present", df["social_support"] == 1),
        ("medical_intervention_present", df["medical_intervention"] == 1),
    ]
    for label, mask in comparisons:
        rows.append(
            {
                "group": label,
                "n": int(mask.sum()),
                "acceptance_surrender_pct": prevalence_rate(df, mask, "acceptance_surrender"),
                "integration_positive_pct": prevalence_rate(df, mask, "integration_positive_afterwards"),
                "fear_of_death_pct": prevalence_rate(df, mask, "fear_of_death"),
            }
        )

    for group in TARGET_GROUPS:
        column = f"group__{group}"
        mask = df[column] == 1
        if int(mask.sum()) < 100:
            continue
        rows.append(
            {
                "group": group,
                "n": int(mask.sum()),
                "acceptance_surrender_pct": prevalence_rate(df, mask, "acceptance_surrender"),
                "integration_positive_pct": prevalence_rate(df, mask, "integration_positive_afterwards"),
                "fear_of_death_pct": prevalence_rate(df, mask, "fear_of_death"),
            }
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).round(2).to_csv(path, index=False)


def run_dose_response_screen(df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    candidates = [
        ("psilocybin_mushrooms", "dose_max_g"),
        ("lsd_lysergamides", "dose_max_ug"),
        ("lsd_lysergamides", "dose_max_blotter"),
        ("lsd_lysergamides", "dose_max_drop"),
        ("mdma_entactogens", "dose_max_mg"),
        ("mdma_entactogens", "dose_max_pill"),
        ("amphetamine_like_stimulants", "dose_max_mg"),
        ("cannabis_natural", "dose_max_g"),
        ("synthetic_cannabinoids", "dose_max_mg"),
        ("synthetic_cannabinoids", "dose_max_drop"),
        ("dxm", "dose_max_mg"),
        ("ketamine_pcp_arylcyclohexylamines", "dose_max_mg"),
    ]
    outcomes = ["fear_of_death", "acceptance_surrender", "integration_positive_afterwards", "medical_intervention"]
    rows = []

    for group, dose_column in candidates:
        if dose_column not in df:
            continue
        group_column = f"group__{group}"
        group_df = df[(df[group_column] == 1) & df[dose_column].notna() & (df[dose_column] > 0)].copy()
        group_df = group_df[group_df[dose_column] <= group_df[dose_column].quantile(0.99)]
        if len(group_df) < 80:
            continue
        group_df["log_dose"] = np.log1p(group_df[dose_column])
        group_df["log_word_count"] = np.log1p(group_df["word_count"].fillna(group_df["word_count"].median()))
        for outcome in outcomes:
            try:
                table = fit_logistic(group_df, outcome, ["log_dose", "log_word_count", "multi_target_group"])
            except Exception:
                continue
            dose_row = table[table["term"] == "log_dose"].iloc[0].to_dict()
            dose_row.update(
                {
                    "target_group": group,
                    "dose_column": dose_column,
                    "outcome": outcome,
                    "dose_n": len(group_df),
                    "dose_median": float(group_df[dose_column].median()),
                }
            )
            rows.append(dose_row)

    table = pd.DataFrame(rows)
    if not table.empty:
        columns = [
            "target_group",
            "dose_column",
            "outcome",
            "dose_n",
            "dose_median",
            "odds_ratio",
            "ci_low",
            "ci_high",
            "p_value",
        ]
        table = table[columns]
        table.round(4).to_csv(output_dir / "dose_response_screen.csv", index=False)
    else:
        with (output_dir / "dose_response_screen.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["target_group", "dose_column", "outcome", "dose_n", "note"])
            writer.writerow(["", "", "", 0, "No group/unit combination had enough parseable dose values."])
    return table


def write_analysis_table(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.drop(columns=[], errors="ignore").to_csv(path, index=False)


def run_all_models(
    report_codes_path: Path,
    covariates_path: Path,
    doses_path: Path,
    analysis_table_path: Path,
    output_dir: Path,
) -> dict[str, pd.DataFrame]:
    df = prepare_analysis_table(report_codes_path, covariates_path, doses_path)
    write_analysis_table(analysis_table_path, df)
    tables = run_core_models(df, output_dir)
    write_let_go_pathway(output_dir / "let_go_pathway_summary.csv", df)
    dose_table = run_dose_response_screen(df, output_dir)
    tables["dose_response_screen"] = dose_table
    return tables


def dose_plot_specs() -> list[tuple[str, str, str, str]]:
    return [
        ("psilocybin_mushrooms", "dose_max_g", "fear_of_death", "Psilocybin mushrooms: death fear"),
        ("psilocybin_mushrooms", "dose_max_g", "medical_intervention", "Psilocybin mushrooms: medical intervention"),
        ("lsd_lysergamides", "dose_max_blotter", "acceptance_surrender", "LSD/lysergamides blotters: let go"),
        ("lsd_lysergamides", "dose_max_blotter", "fear_of_death", "LSD/lysergamides blotters: death fear"),
        ("mdma_entactogens", "dose_max_mg", "medical_intervention", "MDMA/entactogens mg: medical intervention"),
        ("amphetamine_like_stimulants", "dose_max_mg", "fear_of_death", "Amphetamine-like mg: death fear"),
        ("dxm", "dose_max_mg", "medical_intervention", "DXM mg: medical intervention"),
        ("ketamine_pcp_arylcyclohexylamines", "dose_max_mg", "fear_of_death", "Ketamine/PCP mg: death fear"),
    ]


def binned_prevalence(
    df: pd.DataFrame,
    dose_column: str,
    outcome: str,
    bins: int = 5,
) -> pd.DataFrame:
    plot_df = df[[dose_column, outcome]].dropna().copy()
    plot_df = plot_df[(plot_df[dose_column] > 0) & (plot_df[dose_column] <= plot_df[dose_column].quantile(0.99))]
    if len(plot_df) < 50 or plot_df[dose_column].nunique() < 4:
        return pd.DataFrame()

    quantile_bins = min(bins, plot_df[dose_column].nunique())
    plot_df["bin"] = pd.qcut(plot_df[dose_column], q=quantile_bins, duplicates="drop")
    grouped = plot_df.groupby("bin", observed=True).agg(
        dose_mid=(dose_column, "median"),
        outcome_rate=(outcome, "mean"),
        n=(outcome, "size"),
    )
    grouped["outcome_pct"] = grouped["outcome_rate"] * 100
    return grouped.reset_index(drop=True)


def logistic_curve(df: pd.DataFrame, dose_column: str, outcome: str) -> tuple[np.ndarray, np.ndarray] | None:
    model_df = df[[dose_column, outcome, "word_count", "multi_target_group"]].dropna().copy()
    model_df = model_df[(model_df[dose_column] > 0) & (model_df[dose_column] <= model_df[dose_column].quantile(0.99))]
    if len(model_df) < 80 or model_df[outcome].nunique() < 2:
        return None

    model_df["log_dose"] = np.log1p(model_df[dose_column])
    model_df["log_word_count"] = np.log1p(model_df["word_count"].fillna(model_df["word_count"].median()))
    predictors = ["log_dose", "log_word_count", "multi_target_group"]
    x = sm.add_constant(model_df[predictors].astype(float), has_constant="add")
    y = model_df[outcome].astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = sm.GLM(y, x, family=sm.families.Binomial()).fit(maxiter=200)

    dose_grid = np.linspace(model_df[dose_column].quantile(0.05), model_df[dose_column].quantile(0.95), 80)
    pred = pd.DataFrame(
        {
            "const": 1.0,
            "log_dose": np.log1p(dose_grid),
            "log_word_count": model_df["log_word_count"].median(),
            "multi_target_group": model_df["multi_target_group"].median(),
        }
    )
    return dose_grid, result.predict(pred) * 100


def plot_dose_response_panels(analysis_table_path: Path, output_path: Path) -> int:
    import matplotlib.pyplot as plt

    df = pd.read_csv(analysis_table_path)
    specs = dose_plot_specs()
    panels: list[tuple[str, pd.DataFrame, tuple[np.ndarray, np.ndarray] | None, str]] = []

    for group, dose_column, outcome, title in specs:
        group_column = f"group__{group}"
        if group_column not in df or dose_column not in df:
            continue
        sub = df[df[group_column] == 1].copy()
        binned = binned_prevalence(sub, dose_column, outcome)
        if binned.empty:
            continue
        panels.append((dose_column, binned, logistic_curve(sub, dose_column, outcome), title))

    if not panels:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("No dose-response panels had enough data.\n", encoding="utf-8")
        return 0

    cols = 2
    rows = int(np.ceil(len(panels) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(12, max(4, rows * 3.7)))
    axes_array = np.atleast_1d(axes).flatten()

    for ax, (dose_column, binned, curve, title) in zip(axes_array, panels):
        sizes = 30 + binned["n"] * 0.8
        ax.scatter(binned["dose_mid"], binned["outcome_pct"], s=sizes, alpha=0.75)
        if curve is not None:
            ax.plot(curve[0], curve[1], linewidth=2)
        ax.set_title(title)
        ax.set_xlabel(dose_column.replace("dose_max_", "dose: "))
        ax.set_ylabel("% reports")
        ax.set_ylim(0, 100)
        if binned["dose_mid"].max() / max(binned["dose_mid"].min(), 1e-9) > 20:
            ax.set_xscale("log")
        ax.grid(alpha=0.25)

    for ax in axes_array[len(panels) :]:
        ax.axis("off")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.suptitle("Exploratory dose-response panels: binned prevalence plus adjusted logistic curve", y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return len(panels)
