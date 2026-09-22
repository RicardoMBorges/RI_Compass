"""Streamlit GC retention index calculator for alkane standards and feature tables."""
from __future__ import annotations

import io
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GC Retention Index Calculator", layout="wide")


@st.cache_data(show_spinner=False)
def read_csv_bytes(raw):
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            result = pd.read_csv(io.BytesIO(raw), sep=None, engine="python", encoding=encoding)
            if len(result.columns) < 2:
                continue
            result = result.loc[:, ~result.columns.astype(str).str.match(r"^Unnamed: \d+$")]
            return result
        except (UnicodeError, pd.errors.ParserError):
            pass
    raise ValueError("Could not read CSV. Check encoding and field separator.")


def read_csv(upload):
    return read_csv_bytes(upload.getvalue())


@st.cache_data(show_spinner=False)
def read_reference_file(path, modified_ns):
    return pd.read_csv(path, dtype={"source_record_id": "string"}).fillna("")


def guess(columns, candidates):
    for candidate in candidates:
        for col in columns:
            if str(col).lower().strip() == candidate:
                return col
    return columns[0]


def numeric(series):
    # Accept decimal commas in otherwise numeric CSV columns.
    return pd.to_numeric(series.astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")


def retention_indices(peak_rt, alkane_rt, carbons, method="Linear (temperature programmed)", dead_time=0):
    """Interpolate between consecutive n-alkanes; outside standards returns NaN."""
    peak_rt = np.asarray(peak_rt, dtype=float)
    alkane_rt = np.asarray(alkane_rt, dtype=float)
    carbons = np.asarray(carbons, dtype=float)
    positions = np.searchsorted(alkane_rt, peak_rt, side="right") - 1
    positions = np.clip(positions, 0, len(alkane_rt) - 2)
    lower, upper = alkane_rt[positions], alkane_rt[positions + 1]
    if method == "Logarithmic (isothermal Kovats)":
        fraction = (np.log(peak_rt - dead_time) - np.log(lower - dead_time)) / (
            np.log(upper - dead_time) - np.log(lower - dead_time)
        )
    else:
        fraction = (peak_rt - lower) / (upper - lower)
    index = 100 * (carbons[positions] + fraction * (carbons[positions + 1] - carbons[positions]))
    valid = np.isfinite(peak_rt) & (peak_rt >= alkane_rt[0]) & (peak_rt <= alkane_rt[-1])
    return np.where(valid, index, np.nan), positions, valid


st.title("RI Compass")
st.caption("Calibrate with an n-alkane series and append retention indices to a GC–MS feature table.")
with st.expander("Calculation and interpretation", expanded=False):
    st.markdown("""
    **Temperature-programmed GC:** linear retention index (van den Dool–Kratz),
    `RI = 100 × [n + (tR(x) − tR(n)) / (tR(n+1) − tR(n))]`.

    **Isothermal GC:** logarithmic Kovats index using adjusted retention times
    `tR' = tR − tM`. Select this only for an isothermal run with a known dead time.
    Both datasets must come from the same chromatographic method and compatible runs.
    A single consensus feature retention time gives an approximate RI; use sample-specific
    retention times when precision across runs matters.
    """)

with st.sidebar:
    logo_path = Path(__file__).resolve().parent / "static" / "LAABio.png"
    if logo_path.is_file():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.caption("LAABio")
    kovats_logo_path = Path(__file__).resolve().parent / "static" / "KOVATS.png"
    if kovats_logo_path.is_file():
        st.image(str(kovats_logo_path), use_container_width=True)
    else:
        st.markdown("<div style=\"height:84px;display:flex;align-items:center;justify-content:center;border:1px dashed #888;border-radius:8px;color:#777;\">KOVATS logo</div>", unsafe_allow_html=True)
    st.caption("by Ricardo M Borges (IPPN-UFRJ)")
    st.divider()
    st.header("Import data")
    standards_file = st.file_uploader("n-Alkane calibration CSV (carbon number and RT)", type="csv", key="standards", help="Upload the known alkane series, e.g. KOVATS_from_MZMine2.53.csv: Carbon_Number = 8–30 and RT in seconds. Each row represents one alkane; this file is not the deconvoluted sample feature table.")
    features_file = st.file_uploader("Feature table CSV (retention time)", type="csv", key="features", help="Upload deconvoluted features, e.g. Resultados_GilbertoCOPPE_2_quant.csv: one row per feature, 'row retention time' in minutes, and sample 'Peak area' columns. For a standard check, upload features from the standard injection here.")
    extra_files = st.file_uploader("Additional RI reference tables (CSV or TSV)", type=["csv", "tsv", "txt"], accept_multiple_files=True, key="references", help="Optional candidate library with one compound per row and at least a compound name and numeric reference RI. The consolidated RI library in resources/ is loaded automatically. Do not upload the alkane calibration or feature table here.")
    with st.expander("Tutorial · which file goes where", expanded=False):
        st.markdown("""
        | Import | Required content | Example |
        | --- | --- | --- |
        | **n-Alkane calibration** | One row per known alkane; `Carbon_Number` and its `RT` | `KOVATS_from_MZMine2.53.csv` (RT in **seconds**) |
        | **Feature table** | One row per deconvoluted signal; feature RT and optional sample `Peak area` columns | `Resultados_GilbertoCOPPE_2_quant.csv` (RT in **minutes**) |
        | **Additional RI references** | Names and published or measured reference RI values | Optional; the built-in consolidated library loads automatically |

        Upload the **same alkane calibration** whether you analyze study samples or check the standard injection. Select the feature table according to what you want to annotate; do not swap its position with the calibration file.
        """)
    with st.expander("Tutorial · column mapping and acquisition", expanded=False):
        st.markdown("""
        Set **Alkane carbon number** to `Carbon_Number` (C8–C30), **Alkane retention time** to `RT`, and **Feature retention time** to `row retention time` for the example files. Select **seconds** for the alkane RT and **minutes** for the feature RT; both are converted to minutes internally.

        Choose **Linear (temperature programmed)** for a programmed oven. The logarithmic Kovats option requires an isothermal run and a measured dead time `tM`. Only features between the first and last alkane receive an RI. Check the displayed calibration range before clicking **Run analysis**.
        """)
    with st.expander("Tutorial · reference import and interpreting results", expanded=False):
        st.markdown("""
        The built-in `resources/GC_RI_reference_consolidated.csv` loads automatically. For an extra library, map its **reference RI**, **compound name**, and, when available, **stationary phase** and **RI type**. Missing phase information reduces support; it is not treated as a confirmed column match.

        Select **Study samples** to rank candidates from RI references. Select **n-Alkane standard mixture** only when the feature table contains deconvoluted peaks from the known alkane injection; the app then checks their RT against the calibration and labels matched standards. Since those RTs created the calibration, this is a consistency check, not independent identification.

        Click **Run analysis** after changes to uploads, mappings, or filters. **Ranked candidates** lists multiple alternatives per feature; its sample intensities repeat across those alternatives. `ri_support` measures RI agreement and column metadata, not spectral identification. Review blank/standard areas and EI spectra before assigning a chemical identity.
        """)
    with st.expander("Tutorial · chromatogram CSV import", expanded=False):
        st.markdown("""
        Open the **Chromatograms** tab and upload one or more CSV/TSV files with a time column and a signal column. For `MPRM 100ul_10-09-2026.CDF.csv`, map **Time column** to `RT`, **Intensity column** to `I`, and **Time unit** to `minutes`. Choose **Overlay** or **Stacked**, filter the RI support classes, then click **Plot chromatograms**.

        Chromatogram uploads draw the signals; annotations come from the latest **Run analysis** on the feature table. The chart can be zoomed and downloaded as interactive HTML. Its marked RT windows indicate RI candidates and do not establish peak boundaries or chemical identity.
        """)
if not standards_file or not features_file:
    st.info("Upload both CSV files to begin. Example columns: Carbon_Number, RT; row retention time.")
    st.stop()
try:
    standards = read_csv(standards_file)
    features = read_csv(features_file)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.header("Column mapping")
    carbon_col = st.selectbox("Alkane carbon number", standards.columns, index=standards.columns.get_loc(guess(standards.columns, ["carbon_number", "carbon number", "carbon"])), help="Choose the integer carbon count of each known n-alkane, e.g. Carbon_Number containing 8–30. Row ID, m/z, and RT are not carbon numbers.")
    alkane_col = st.selectbox("Alkane retention time", standards.columns, index=standards.columns.get_loc(guess(standards.columns, ["rt", "retention time", "retention_time"])), help="Choose the observed RT of the alkane standards, e.g. RT. Set its unit below; the example calibration is in seconds.")
    feature_col = st.selectbox("Feature retention time", features.columns, index=features.columns.get_loc(guess(features.columns, ["row retention time", "retention time", "rt"])), help="Choose the RT of deconvoluted features, e.g. row retention time. Set its unit below; the example feature table is in minutes.")
    st.header("Acquisition")
    method = st.selectbox("Index calculation", ["Linear (temperature programmed)", "Logarithmic (isothermal Kovats)"])
    alkane_unit = st.selectbox("Alkane RT unit", ["seconds", "minutes"], index=0, help="Unit of the selected alkane RT column only. KOVATS_from_MZMine2.53.csv uses seconds.")
    feature_unit = st.selectbox("Feature RT unit", ["minutes", "seconds"], index=0, help="Unit of the selected feature RT column only. Resultados_GilbertoCOPPE_2_quant.csv uses minutes.")
    dead_time = st.number_input("Dead time tM (minutes)", min_value=0.0, value=0.0, step=0.01, disabled=method != "Logarithmic (isothermal Kovats)")

carbon = numeric(standards[carbon_col])
alkane_rt = numeric(standards[alkane_col]) / (60 if alkane_unit == "seconds" else 1)
feature_rt = numeric(features[feature_col]) / (60 if feature_unit == "seconds" else 1)
cal = pd.DataFrame({"Carbon number": carbon, "RT (min)": alkane_rt}).dropna().sort_values("Carbon number")
if len(cal) and (not np.all(np.isclose(cal["Carbon number"], np.round(cal["Carbon number"]))) or
                 cal["Carbon number"].min() < 5 or cal["Carbon number"].max() > 60):
    st.error("Invalid n-alkane calibration: carbon numbers must be integers from C5 to C60. Select the Carbon_Number column from your C8–C30 calibration CSV; do not select row ID or retention time as the carbon number.")
    st.stop()
if len(cal) < 2 or cal["Carbon number"].duplicated().any() or cal["RT (min)"].duplicated().any():
    st.error("Calibration requires at least two standards with unique carbon numbers and retention times.")
    st.stop()
if not np.all(np.diff(cal["Carbon number"]) == 1) or not np.all(np.diff(cal["RT (min)"]) > 0):
    st.error("Standards must have consecutive carbon numbers and strictly increasing retention times.")
    st.stop()
if method == "Logarithmic (isothermal Kovats)" and (dead_time <= 0 or dead_time >= cal["RT (min)"].min()):
    st.error("Enter a measured positive dead time smaller than the first alkane RT.")
    st.stop()

rt = cal["RT (min)"].to_numpy()
carbons = cal["Carbon number"].to_numpy()
ri, pos, valid = retention_indices(feature_rt.to_numpy(), rt, carbons, method, dead_time)
out = features.copy()
out["retention_index"] = pd.Series(ri, index=out.index).round(2)
out["ri_status"] = np.select(
    [feature_rt.isna().to_numpy(), feature_rt.to_numpy() < rt[0], feature_rt.to_numpy() > rt[-1]],
    ["invalid RT", "before first alkane", "after last alkane"],
    default="within calibration range",
)
out["lower_alkane_C"] = np.where(valid, carbons[pos], np.nan)
out["upper_alkane_C"] = np.where(valid, carbons[pos + 1], np.nan)

c1, c2, c3 = st.columns(3)
c1.metric("Alkane standards", len(cal))
c2.metric("Features indexed", int(valid.sum()))
c3.metric("Outside range or invalid", int((~valid).sum()))
st.info(f"Calibration: C{int(carbons[0])}–C{int(carbons[-1])}, {rt[0]:.3f}–{rt[-1]:.3f} min. Feature RTs converted to minutes before calculation.")
st.subheader("Alkane calibration")
st.dataframe(cal, hide_index=True)
st.line_chart(cal.set_index("RT (min)")["Carbon number"] * 100, x_label="Retention time (min)", y_label="Retention index")

st.subheader("Reference libraries and annotation settings")
reference_path = Path(__file__).resolve().parent / "resources" / "GC_RI_reference_consolidated.csv"
if reference_path.is_file():
    built_in = read_reference_file(str(reference_path), reference_path.stat().st_mtime_ns)
else:
    built_in = pd.DataFrame()
    st.warning("Built-in reference missing. Place GC_RI_reference_consolidated.csv in resources/.")

extra = []
for j, uploaded in enumerate(extra_files):
    try:
        incoming = read_csv(uploaded)
    except ValueError as exc:
        st.error(f"{uploaded.name}: {exc}")
        continue
    with st.expander(f"Map columns: {uploaded.name}"):
        ri_col = st.selectbox("Reference RI column", incoming.columns, index=incoming.columns.get_loc(guess(incoming.columns, ["reference_ri", "retention_index", "ri", "kovats_index"])), key=f"ri_{j}", help="Select a numeric reference retention index, e.g. 1000 for an RI of 1000. This is not a retention time in seconds or minutes.")
        name_col = st.selectbox("Compound name column", incoming.columns, index=incoming.columns.get_loc(guess(incoming.columns, ["compound_name", "common name", "name", "compound"])), key=f"name_{j}", help="Select the chemical name associated with each reference RI.")
        optional = ["(not provided)"] + list(incoming.columns)
        phase_col = st.selectbox("Stationary phase / column (optional)", optional, index=optional.index(guess(incoming.columns, ["stationary_phase", "column_name", "column"])) if any(str(c).lower() in ("stationary_phase", "column_name", "column") for c in incoming.columns) else 0, key=f"phase_{j}", help="Select column or stationary-phase metadata (for example DB-5 or 5% phenyl) when present; otherwise leave '(not provided)'.")
        index_col = st.selectbox("RI type / temperature program (optional)", optional, index=optional.index(guess(incoming.columns, ["index_type", "ri_type", "temperature_program"])) if any(str(c).lower() in ("index_type", "ri_type", "temperature_program") for c in incoming.columns) else 0, key=f"type_{j}", help="Select a description of how the published RI was determined, when available. The app records this metadata for review.")
    mapped = pd.DataFrame({
        "reference_ri": numeric(incoming[ri_col]), "compound_name": incoming[name_col].astype(str).str.strip(),
        "source_database": uploaded.name,
        "source_record_id": [f"{uploaded.name}:{n}" for n in range(2, len(incoming) + 2)],
        "stationary_phase": incoming[phase_col].astype(str) if phase_col != "(not provided)" else "",
        "index_type": incoming[index_col].astype(str) if index_col != "(not provided)" else "",
    })
    rejected = mapped["reference_ri"].isna() | mapped["compound_name"].isin(["", "nan", "None"])
    if rejected.any():
        st.warning(f"{uploaded.name}: skipped {int(rejected.sum())} rows with invalid RI or missing compound name.")
    extra.append(mapped.loc[~rejected])

references = pd.concat([built_in, *extra], ignore_index=True) if (len(built_in) or extra) else pd.DataFrame()
if references.empty:
    st.info("Add a reference library to show candidate annotations.")
    st.dataframe(out, hide_index=True)
    st.stop()
references["reference_ri"] = numeric(references["reference_ri"])
references = references.dropna(subset=["reference_ri", "compound_name"])
references = references[references["compound_name"].astype(str).str.strip().ne("")].copy()
for field in ["stationary_phase", "column_name", "index_type", "source_database", "source_record_id", "literature_reference", "inchikey"]:
    if field not in references:
        references[field] = ""
    references[field] = references[field].fillna("").astype(str)

with st.sidebar:
    st.header("Candidate filtering")
    max_delta = st.slider("Maximum |ΔRI|", 5, 100, 20, 5)
    good_delta = st.slider("Close RI threshold", 1, max_delta, min(10, max_delta))
    source_options = sorted(references["source_database"].unique())
    selected_sources = st.multiselect("Sources", source_options, default=source_options)
    phase_policy = st.selectbox("Phase metadata", ["All, flag unknown", "Known compatible only"])
    top_n = st.slider("Top candidates per feature", 1, 20, 5)
    min_sample_count = st.slider("Minimum detected samples", 0, max(0, sum(str(c).endswith(' Peak area') for c in features.columns)), 0)
    feature_role = st.selectbox("Feature table type", ["Study samples", "n-Alkane standard mixture"], index=1 if "alkane" in features_file.name.lower() else 0, help="Use the standard mixture option when the feature table was extracted from the same alkane injection used for calibration.")
    standard_rt_tolerance = st.number_input("Standard RT tolerance (min)", min_value=0.001, max_value=1.0, value=0.03, step=0.01, disabled=feature_role != "n-Alkane standard mixture")

with st.sidebar:
    run_analysis = st.button("▶ Run analysis", type="primary", use_container_width=True)
    st.caption("Settings and uploads are applied only when you click Run analysis.")

if run_analysis:
    with st.spinner("Calculating RI and searching the reference library..."):
        area_cols = [c for c in features.columns if str(c).endswith(" Peak area") and not any(token in str(c).lower() for token in ["branco", "blank", "padrao hidroc", "alkane"])]
        areas = features[area_cols].apply(numeric).fillna(0) if area_cols else pd.DataFrame(index=features.index)
        detections = (areas > 0).sum(axis=1).to_numpy()
        out["detected_samples"] = detections
        compatible = references["stationary_phase"].str.contains(r"5% diphenyl|5% phenyl|db.?5|hp.?5|rtx.?5", case=False, regex=True) | references["column_name"].str.contains(r"db.?5|hp.?5|rtx.?5", case=False, regex=True)
        references["phase_match"] = np.where(compatible, "comparable 5%-phenyl phase", "unknown or other phase")
        references = references[references["source_database"].isin(selected_sources)]
        if phase_policy == "Known compatible only":
            references = references[references["phase_match"] == "comparable 5%-phenyl phase"]
        references = references.sort_values("reference_ri").reset_index(drop=True)
        reference_values = references["reference_ri"].to_numpy(dtype=float)

        hits = []
        for idx, observed in enumerate(ri):
            if not np.isfinite(observed) or detections[idx] < min_sample_count or not len(references):
                continue
            lower = np.searchsorted(reference_values, observed - max_delta, side="left")
            upper = np.searchsorted(reference_values, observed + max_delta, side="right")
            for ref_idx in range(lower, upper):
                record = references.iloc[ref_idx]
                delta = float(observed - reference_values[ref_idx])
                phase_ok = record["phase_match"] == "comparable 5%-phenyl phase"
                proximity = max(0, 1 - abs(delta) / max_delta)
                score = round(100 * (0.85 * proximity + 0.15 * int(phase_ok)), 1)
                support = "strong RI support" if abs(delta) <= good_delta and phase_ok else ("moderate RI support" if abs(delta) <= good_delta or (phase_ok and abs(delta) <= max_delta / 2) else "weak RI support")
                hits.append({
                    "feature_row": idx + 1, "feature_id": features.iloc[idx]["row ID"] if "row ID" in features else idx + 1,
                    "observed_ri": round(float(observed), 2), "feature_rt_min": round(float(feature_rt.iloc[idx]), 5), "compound_name": record["compound_name"],
                    "reference_ri": reference_values[ref_idx], "delta_ri": round(delta, 2),
                    "abs_delta_ri": round(abs(delta), 2), "ri_rank_score": score,
                    "ri_support": support, "identification_confidence": "RI only: unconfirmed",
                    "phase_match": record["phase_match"], "source_database": record["source_database"],
                    "source_record_id": record["source_record_id"], "index_type": record["index_type"],
                    "column_name": record["column_name"], "literature_reference": record["literature_reference"],
                    "inchikey": record["inchikey"], "detected_samples": int(detections[idx]),
                })

        if feature_role == "n-Alkane standard mixture":
            # In a known mixture, the calibration table provides the expected
            # substances. Generic RI references cannot establish their identity.
            hits = []
            feature_times = feature_rt.to_numpy(dtype=float)
            used_features = set()
            for carbon_number, standard_time in zip(carbons, rt):
                candidates = np.flatnonzero(np.isfinite(feature_times) & (np.abs(feature_times - standard_time) <= standard_rt_tolerance))
                candidates = sorted(candidates, key=lambda i: (abs(feature_times[i] - standard_time), i))
                chosen = next((i for i in candidates if i not in used_features), None)
                if chosen is None:
                    continue
                used_features.add(chosen)
                name = f"{int(carbon_number)}-carbon n-alkane (C{int(carbon_number)})"
                if "Compound_Name" in standards.columns:
                    known = standards.loc[numeric(standards[carbon_col]) == carbon_number, "Compound_Name"].dropna()
                    if len(known) and str(known.iloc[0]).strip():
                        name = str(known.iloc[0]).strip()
                hits.append({"feature_row": chosen + 1, "feature_id": features.iloc[chosen]["row ID"] if "row ID" in features else chosen + 1,
                    "observed_ri": round(float(ri[chosen]), 2), "feature_rt_min": round(float(feature_times[chosen]), 5),
                    "compound_name": name, "reference_ri": 100 * carbon_number,
                    "delta_ri": round(float(ri[chosen] - 100 * carbon_number), 2), "abs_delta_ri": round(float(abs(ri[chosen] - 100 * carbon_number)), 2),
                    "ri_rank_score": 100.0, "ri_support": "strong RI support", "identification_confidence": "Known standard mixture: RT match; spectrum not verified",
                    "phase_match": "same calibration run", "source_database": "Uploaded n-alkane calibration", "source_record_id": f"C{int(carbon_number)}",
                    "index_type": "calibration RT check", "column_name": "", "literature_reference": "", "inchikey": "", "detected_samples": 1})
        all_hits = pd.DataFrame(hits)
        # Preserve every uploaded intensity column, including blank and
        # standard injections, with its original name and unmodified values.
        intensity_columns = [col for col in features.columns if str(col).endswith(" Peak area")]
        if not all_hits.empty:
            positions = all_hits["feature_row"].to_numpy(dtype=int) - 1
            for col in intensity_columns:
                all_hits[col] = features[col].to_numpy()[positions]
        else:
            for col in intensity_columns:
                all_hits[col] = pd.Series(dtype=features[col].dtype)
        summary = {"reference_records": len(carbons) if feature_role == "n-Alkane standard mixture" else len(references), "matched_features": 0, "ambiguous_features": 0}
        if all_hits.empty:
            out["candidate_count"] = 0
            top = all_hits.copy()
        else:
            all_hits["_measured_alkane_source"] = all_hits["source_database"].eq("IPPN-UFRJ measured n-alkane standards")
            all_hits = all_hits.sort_values(["feature_row", "ri_rank_score", "abs_delta_ri", "_measured_alkane_source"], ascending=[True, False, True, False]).drop(columns="_measured_alkane_source").reset_index(drop=True)
            all_hits["rank"] = all_hits.groupby("feature_row").cumcount() + 1
            top = all_hits[all_hits["rank"] <= top_n].copy()
            count = all_hits.groupby("feature_row").size()
            out["candidate_count"] = [int(count.get(idx + 1, 0)) for idx in range(len(out))]
            best = all_hits.drop_duplicates("feature_row").set_index("feature_row")
            out["top_candidate"] = [best.at[i + 1, "compound_name"] if i + 1 in best.index else "" for i in range(len(out))]
            out["top_abs_delta_ri"] = [best.at[i + 1, "abs_delta_ri"] if i + 1 in best.index else np.nan for i in range(len(out))]
            out["top_ri_support"] = [best.at[i + 1, "ri_support"] if i + 1 in best.index else "" for i in range(len(out))]
            out["identification_confidence"] = [best.at[i + 1, "identification_confidence"] if i + 1 in best.index else "no candidate" for i in range(len(out))]
            competitors = all_hits.groupby("feature_row")["compound_name"].nunique()
            out["distinct_candidate_names"] = [int(competitors.get(i + 1, 0)) for i in range(len(out))]
            summary["matched_features"] = len(best)
            summary["ambiguous_features"] = int((competitors > 1).sum())
        st.session_state["ri_analysis_result"] = {
            "annotated": out.copy(), "all_hits": all_hits.copy(), "top": top.copy(),
            "calibration": cal.copy(), "summary": summary,
            "inputs": (standards_file.name, standards_file.size, features_file.name, features_file.size, tuple((f.name, f.size) for f in extra_files)),
            "settings": (str(carbon_col), str(alkane_col), str(feature_col), method, alkane_unit, feature_unit, dead_time, max_delta, good_delta, tuple(selected_sources), phase_policy, top_n, min_sample_count, feature_role, standard_rt_tolerance),
        }

result = st.session_state.get("ri_analysis_result")
analysis_tab, chromatogram_tab = st.tabs(["RI annotations", "Chromatograms"])
with analysis_tab:
    if result is None:
        st.info("Configure the data and settings, then click **Run analysis** in the sidebar.")
    else:
        current_inputs = (standards_file.name, standards_file.size, features_file.name, features_file.size, tuple((f.name, f.size) for f in extra_files))
        current_settings = (str(carbon_col), str(alkane_col), str(feature_col), method, alkane_unit, feature_unit, dead_time, max_delta, good_delta, tuple(selected_sources), phase_policy, top_n, min_sample_count, feature_role, standard_rt_tolerance)
        if current_inputs != result["inputs"] or current_settings != result["settings"]:
            st.warning("Inputs or settings have changed. Displayed results are from the previous run; click Run analysis to update them.")
        st.caption("Displayed results remain unchanged until Run analysis is clicked again.")
        annotated, all_hits, top = result["annotated"], result["all_hits"], result["top"]
        summary = result["summary"]
        a, b, c = st.columns(3)
        a.metric("Calibration alkanes" if result["settings"][-2] == "n-Alkane standard mixture" else "Reference records", summary["reference_records"])
        b.metric("Features with candidates", summary["matched_features"])
        c.metric("Ambiguous features (>1 name)", summary["ambiguous_features"])
        if all_hits.empty:
            st.info("No candidates passed the filters used in this analysis.")
        else:
            st.subheader("Ranked candidates")
            st.dataframe(top, hide_index=True)
            st.download_button("Download all candidate observations (CSV)", all_hits.to_csv(index=False).encode("utf-8-sig"), file_name="RI_all_candidates.csv", mime="text/csv")
            st.download_button("Download displayed top candidates (CSV)", top.to_csv(index=False).encode("utf-8-sig"), file_name="RI_top_candidates.csv", mime="text/csv")
        if result["settings"][-2] == "n-Alkane standard mixture":
            st.info("Known standard mixture: alkane labels come from the uploaded calibration and match by RT within the chosen tolerance. RI is calculated from the same calibration, so this is an RT assignment check, not independent chemical confirmation. Inspect spectra to verify peak identities.")
        else:
            st.caption("Quality checks: |ΔRI|, column compatibility, source and reference RI metadata, alternative names, and detection across samples. An RI-only match cannot establish identity. Rank scores are heuristic, not probabilities.")
        st.subheader("Annotated feature table")
        st.dataframe(annotated, hide_index=True)
        st.download_button("Download annotated features (CSV)", annotated.to_csv(index=False).encode("utf-8-sig"), file_name="GCMS_annotated_features.csv", mime="text/csv")
        st.download_button("Download calibration (CSV)", result["calibration"].to_csv(index=False).encode("utf-8-sig"), file_name="alkane_calibration_minutes.csv", mime="text/csv")


def chromatogram_traces(frame, file_label, time_col, intensity_col, group_col, time_unit):
    """Parse either long (time, intensity, sample) or wide (time, one column per sample)."""
    time = numeric(frame[time_col]) / (60 if time_unit == "seconds" else 1)
    outputs = []
    if intensity_col != "All numeric columns":
        intensity = numeric(frame[intensity_col])
        groups = frame[group_col].astype(str) if group_col != "(no group column)" else pd.Series(file_label, index=frame.index)
        for group in groups.dropna().unique():
            mask = groups == group
            trace = pd.DataFrame({"time_min": time[mask], "intensity": intensity[mask]}).replace([np.inf, -np.inf], np.nan).dropna()
            trace = trace.groupby("time_min", as_index=False)["intensity"].mean().sort_values("time_min")
            if len(trace) > 1:
                outputs.append((f"{file_label} / {group}" if group != file_label else file_label, trace))
    else:
        for col in frame.columns:
            if col == time_col or col == group_col:
                continue
            intensity = numeric(frame[col])
            if intensity.notna().sum() < max(2, len(frame) * 0.8):
                continue
            trace = pd.DataFrame({"time_min": time, "intensity": intensity}).replace([np.inf, -np.inf], np.nan).dropna()
            trace = trace.groupby("time_min", as_index=False)["intensity"].mean().sort_values("time_min")
            if len(trace) > 1:
                outputs.append((f"{file_label} / {col}", trace))
    return outputs


with chromatogram_tab:
    st.subheader("Chromatogram viewer")
    st.caption("Upload chromatogram CSV/TSV files with retention time and signal intensity. Marked regions follow the RI candidate results from the latest Run analysis.")
    with st.expander("Chart guide · shaded bands and colored markers", expanded=False):
        st.markdown("""
        **Shaded, hatched bands** mark retention-time windows around features that have an RI candidate in the selected support classes. Their width is set by **Annotation band half-width**. A band highlights where to inspect the chromatogram; it does not define chromatographic peak boundaries or prove the compound is present.

        **Colored diamond markers** indicate the candidate position at the feature retention time. Their height follows the strongest signal in that window on the first displayed chromatogram; this is a visual anchor, not a measured compound intensity. Hover over a marker to see `compound_name`, feature ID, observed and reference RI, and |ΔRI|. The first few names are also printed above the markers.

        **Colors reflect `ri_support`:** green = strong, amber = moderate, red = weak. RI support measures agreement with the reference retention index and column metadata. Compound identity remains unconfirmed without additional evidence such as a mass spectrum and an authentic standard.
        """)
    chrom_files = st.file_uploader("Chromatogram files", type=["csv", "tsv", "txt"], accept_multiple_files=True, key="chrom_files", help="Upload TIC or other signal traces with RT and intensity, e.g. a CSV with columns RT and I. These files draw the chromatograms; candidate annotations use the latest Run analysis.")
    parsed = []
    if chrom_files:
        for number, chrom_file in enumerate(chrom_files):
            try:
                frame = read_csv(chrom_file)
                parsed.append((chrom_file, frame))
            except ValueError as exc:
                st.error(f"{chrom_file.name}: {exc}")
    with st.form("chromatogram_form"):
        layout = st.radio("Display", ["Overlay", "Stacked"], horizontal=True)
        signal_scale = st.selectbox("Signal scale", ["Normalize each chromatogram to its maximum", "Original intensity"])
        strengths = st.multiselect("Hatched RI support classes", ["strong RI support", "moderate RI support", "weak RI support"], default=["strong RI support"], format_func=lambda text: text.replace(" RI support", "").capitalize())
        half_window = st.number_input("Annotation band half-width (min)", min_value=0.01, max_value=2.0, value=0.08, step=0.01)
        max_bands = st.slider("Maximum annotation bands", 20, 500, 200, step=20)
        label_limit = st.slider("Compound labels shown on chart", 0, 50, 12, step=1)
        mappings = []
        for number, (chrom_file, frame) in enumerate(parsed):
            with st.expander(f"Columns: {chrom_file.name}", expanded=True):
                columns = list(frame.columns)
                default_time = next((c for c in columns if any(token in str(c).lower() for token in ["retention time", "time", "rt"])), columns[0])
                time_col = st.selectbox("Time column", columns, index=columns.index(default_time), key=f"chrom_time_{number}", help="Select scan retention time. For the supplied chromatogram CSV, choose RT.")
                intensity_choices = ["All numeric columns"] + [c for c in columns if c != time_col]
                default_signal = next((c for c in intensity_choices[1:] if str(c).strip().lower() in ("i", "int", "counts") or any(token in str(c).lower() for token in ["intensity", "tic", "signal", "abundance"])), intensity_choices[0])
                intensity_col = st.selectbox("Intensity column (or wide table)", intensity_choices, index=intensity_choices.index(default_signal), key=f"chrom_signal_{number}", help="Select I for a two-column RT/I chromatogram, or All numeric columns if each signal has a separate column.")
                groups = ["(no group column)"] + [c for c in columns if c not in (time_col, intensity_col)]
                group_col = st.selectbox("Sample/group column for long format", groups, key=f"chrom_group_{number}", disabled=intensity_col == "All numeric columns", help="Use only if one file contains several samples distinguished by a sample/group column; otherwise leave (no group column).")
                time_unit = st.selectbox("Time unit", ["minutes", "seconds"], key=f"chrom_unit_{number}", help="Choose the unit of the chromatogram time column. The supplied RT/I example is in minutes.")
                mappings.append((time_col, intensity_col, group_col, time_unit))
        render_chart = st.form_submit_button("Plot chromatograms", type="primary", disabled=not bool(parsed))

    if render_chart:
        traces = []
        for (chrom_file, frame), mapping in zip(parsed, mappings):
            traces.extend(chromatogram_traces(frame, chrom_file.name, *mapping))
        if not traces:
            st.error("No chromatogram could be parsed. Map a time column and an intensity column, or choose all numeric columns for a wide table.")
        else:
            import plotly.graph_objects as go
            import plotly.io as pio
            from html import escape

            figure = go.Figure()
            max_values = [max(1e-12, float(np.nanmax(np.maximum(data["intensity"].to_numpy(), 0)))) for _, data in traces]
            biggest = max(max_values)
            plotted = []
            for trace_index, ((name, data), peak_max) in enumerate(zip(traces, max_values)):
                time_values = data["time_min"].to_numpy()
                signal_values = np.maximum(0, data["intensity"].to_numpy())
                scaled = signal_values / peak_max if signal_scale.startswith("Normalize") else signal_values / biggest
                offset = trace_index * 1.25 if layout == "Stacked" else 0
                y_values = scaled + offset
                plotted.append((time_values, y_values))
                figure.add_trace(go.Scattergl(x=time_values, y=y_values, mode="lines", name=name, line={"width": 1}, hovertemplate="RT: %{x:.3f} min<br>Signal: %{y:.3f}<extra>%{fullData.name}</extra>"))
            ytop = (len(traces) - 1) * 1.25 + 1.12 if layout == "Stacked" else 1.12
            xmin = min(float(data["time_min"].min()) for _, data in traces)
            xmax = max(float(data["time_min"].max()) for _, data in traces)
            colors = {"strong RI support": "#198754", "moderate RI support": "#d99a21", "weak RI support": "#bf5b5b"}
            marks = pd.DataFrame()
            if result is not None and not result["all_hits"].empty and strengths:
                marks = result["all_hits"]
                marks = marks[marks["ri_support"].isin(strengths)].sort_values(["abs_delta_ri", "feature_row"]).drop_duplicates("feature_row").copy()
                if "feature_rt_min" not in marks:
                    # Compatibility with results generated before the chromatogram feature was added.
                    old = result["annotated"]
                    old_col = next((c for c in old.columns if str(c).lower() == "row retention time"), None)
                    if old_col is not None:
                        old_units = result["settings"][5] if "settings" in result else "minutes"
                        marks["feature_rt_min"] = numeric(old[old_col]).iloc[marks["feature_row"].astype(int).to_numpy() - 1].to_numpy() / (60 if old_units == "seconds" else 1)
                    else:
                        marks["feature_rt_min"] = np.nan
                marks["feature_rt_min"] = numeric(marks["feature_rt_min"])
                marks = marks[marks["feature_rt_min"].between(xmin, xmax)]
                eligible_count = len(marks)
                marks = marks.sort_values(["abs_delta_ri", "feature_row"]).head(max_bands)
                marker_x, marker_y, marker_text, marker_colors, display_text = [], [], [], [], []
                anchor_x, anchor_y = plotted[0]
                shapes = []
                for rank_index, (_, mark) in enumerate(marks.iterrows()):
                    rt_value = float(mark["feature_rt_min"])
                    support = mark["ri_support"]
                    color = colors[support]
                    left, right = max(xmin, rt_value - half_window), min(xmax, rt_value + half_window)
                    # Translucent band plus diagonal lines; shapes retain their position during zoom.
                    shapes.append(dict(type="rect", x0=left, x1=right, y0=0, y1=1, xref="x", yref="paper", line={"color": color, "width": 0.6}, fillcolor=color, opacity=0.09, layer="below"))
                    for fraction in (0.0, 0.38, 0.76):
                        x_start = left + fraction * (right - left)
                        shapes.append(dict(type="line", x0=x_start, x1=min(right, x_start + (right - left) * 0.25), y0=0, y1=1, xref="x", yref="paper", line={"color": color, "width": 0.55, "dash": "dot"}, opacity=0.35, layer="below"))
                    nearby = np.flatnonzero((anchor_x >= left) & (anchor_x <= right))
                    closest = int(nearby[np.argmax(anchor_y[nearby])]) if len(nearby) else int(np.argmin(np.abs(anchor_x - rt_value)))
                    marker_x.append(rt_value)
                    marker_y.append(float(anchor_y[closest]))
                    marker_colors.append(color)
                    safe_name = escape(str(mark["compound_name"]))
                    marker_text.append(f"<b>{safe_name}</b><br>Feature: {mark['feature_id']}<br>RT: {rt_value:.3f} min<br>Observed RI: {mark['observed_ri']}<br>Reference RI: {mark['reference_ri']}<br>|ΔRI|: {mark['abs_delta_ri']}<br>{escape(support)}<br>{escape(str(mark['identification_confidence']))}")
                    display_text.append(str(mark["compound_name"]) if rank_index < label_limit else "")
                figure.update_layout(shapes=shapes)
                if marker_x:
                    figure.add_trace(go.Scatter(x=marker_x, y=marker_y, mode="markers+text", text=display_text, textposition="top center", textfont={"size": 9}, marker={"symbol": "diamond", "size": 8, "color": marker_colors, "line": {"color": "white", "width": 0.5}}, customdata=marker_text, hovertemplate="%{customdata}<extra></extra>", name="RI candidates", showlegend=True))
            else:
                eligible_count = 0
            figure.update_layout(title="GC–MS chromatograms and RI candidate positions", xaxis_title="Retention time (min)", yaxis_title="Relative intensity" + (" + offset" if layout == "Stacked" else ""), template="plotly_white", hovermode="closest", height=max(500, min(1050, len(traces) * 85 + 350)), legend={"orientation": "h", "y": -0.18}, margin={"t": 70, "b": 85})
            figure.update_xaxes(range=[xmin, xmax], rangeslider_visible=True)
            figure.update_yaxes(range=[-0.04, ytop])
            html = pio.to_html(figure, full_html=True, include_plotlyjs=True, config={"scrollZoom": True, "displaylogo": False})
            st.session_state["chromatogram_render"] = {"figure": figure, "html": html, "count": len(traces), "marked": len(marks), "eligible": eligible_count, "marked_table": marks[["feature_id", "feature_rt_min", "compound_name", "abs_delta_ri", "ri_support", "identification_confidence"]].copy() if len(marks) else pd.DataFrame()}
    rendered = st.session_state.get("chromatogram_render")
    # Streamlit preserves session state when the app code changes. Earlier chart
    # versions stored a Matplotlib image instead of an interactive Plotly figure.
    if rendered is not None and (not isinstance(rendered, dict) or not all(
        key in rendered for key in ("figure", "html", "count", "marked", "eligible", "marked_table")
    )):
        st.session_state.pop("chromatogram_render", None)
        rendered = None
        st.info("A previous chart was cleared after the app update. Click Plot chromatograms to create the interactive chart.")
    if rendered is not None:
        st.plotly_chart(rendered["figure"], use_container_width=True, config={"scrollZoom": True, "displaylogo": False})
        st.caption(f"{rendered['count']} chromatograms · {rendered['marked']} annotated regions of {rendered['eligible']} eligible features. Hover on a diamond to inspect compound_name and RI evidence. The first chromatogram anchors marker heights; retention positions are consensus feature times. RI support does not confirm identity.")
        if result is None or result["all_hits"].empty:
            st.warning("No RI annotations are available. Click Run analysis in the sidebar, then Plot chromatograms again.")
        elif rendered["eligible"] == 0:
            st.warning("No RI annotations passed the selected support classes within the plotted time range. Check the RI filters and click Plot chromatograms again.")
        if rendered["eligible"] > rendered["marked"]:
            st.info("The band limit was reached; the smallest |ΔRI| values were drawn first. Increase Maximum annotation bands to show more.")
        if not rendered["marked_table"].empty:
            with st.expander("Hatched region details", expanded=False):
                st.dataframe(rendered["marked_table"], hide_index=True)
                st.download_button("Download plotted annotations (CSV)", rendered["marked_table"].to_csv(index=False).encode("utf-8-sig"), file_name="RI_Compass_plotted_annotations.csv", mime="text/csv")
        st.download_button("Download interactive chromatogram (HTML)", rendered["html"].encode("utf-8"), file_name="RI_Compass_chromatograms.html", mime="text/html")
    elif not parsed:
        st.info("Upload chromatogram CSV/TSV files to plot them.")
