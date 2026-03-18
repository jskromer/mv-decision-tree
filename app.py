import streamlit as st
import graphviz

# --- Page Config & Warm Cream Theme ---
st.set_page_config(page_title="M&V Planning Decision Tree — Counterfactual Designs", layout="wide")

st.markdown("""
<style>
    /* Warm cream background matching CfDesigns branding */
    .stApp {
        background-color: #faf6f1;
    }
    .stMainBlockContainer {
        background-color: #faf6f1;
    }
    section[data-testid="stSidebar"] {
        background-color: #f5ede3;
    }
    h1, h2, h3 {
        color: #3d3229;
    }
    .stMarkdown p, .stMarkdown li {
        color: #4a3f35;
    }
    /* Accent borders for recommendation cards */
    .design-card {
        background: #fff9f2;
        border-left: 4px solid #b8860b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("M&V Planning Decision Tree")
st.caption(
    "Counterfactual Designs framework — design your M&V approach by choosing a "
    "measurement **Boundary**, **Model Form**, and **Duration**."
)
st.markdown(
    "*The core question: What would energy use have been without the intervention?*"
)

# ─── Sidebar: Project Context Inputs ─────────────────────────────────────────

st.sidebar.header("Project Context")
st.sidebar.markdown("Answer these questions to receive a counterfactual design recommendation.")

num_ecms = st.sidebar.radio(
    "How many energy conservation measures (ECMs)?",
    ["Single ECM", "Multiple ECMs with interactive effects"],
)

boundary_access = st.sidebar.radio(
    "Measurement boundary access?",
    [
        "Sub-meter available on affected equipment/system",
        "Whole-building meter only (utility bills)",
        "Calibrated simulation model available or feasible",
    ],
)

load_variability = st.sidebar.radio(
    "Load variability of affected system?",
    [
        "Constant or near-constant load (e.g., lighting, base-load motors)",
        "Variable — depends on weather, occupancy, or production",
    ],
)

baseline_data = st.sidebar.selectbox(
    "Baseline data availability?",
    [
        "12+ months of interval or monthly data",
        "3–11 months of data",
        "Little or no pre-intervention data",
    ],
)

independent_vars = st.sidebar.radio(
    "Key independent variables?",
    [
        "None — flat load profile",
        "Single variable (e.g., outdoor air temperature)",
        "Multiple variables (temperature, occupancy, production, etc.)",
    ],
)

savings_signal = st.sidebar.radio(
    "Expected savings relative to baseline noise?",
    [
        "Large — savings clearly exceed baseline variability (>20%)",
        "Moderate — detectable with good model (10–20%)",
        "Small — may be difficult to distinguish from noise (<10%)",
    ],
)

budget_accuracy = st.sidebar.radio(
    "Budget / accuracy priority?",
    [
        "Minimize cost — stipulated values acceptable where defensible",
        "Balanced — reasonable accuracy within practical budget",
        "High accuracy required (e.g., performance contract, ESCO guarantee)",
    ],
)


# ─── Decision Logic → Counterfactual Design Recommendation ───────────────────

def build_recommendation():
    """Return (boundary, model_form, duration, rationale_bullets) tuple."""

    # --- Boundary ---
    if boundary_access == "Calibrated simulation model available or feasible":
        boundary = "Whole-building (simulation-defined boundary)"
        boundary_note = (
            "A calibrated simulation defines the counterfactual across the entire "
            "building, even when physical sub-metering isn't practical."
        )
    elif boundary_access == "Whole-building meter only (utility bills)":
        boundary = "Whole-building meter"
        boundary_note = (
            "Only whole-building meters are available, so the measurement boundary "
            "encompasses the entire facility."
        )
    elif num_ecms == "Multiple ECMs with interactive effects":
        boundary = "Whole-building meter"
        boundary_note = (
            "Multiple interacting ECMs make equipment-level isolation impractical. "
            "A whole-building boundary captures net interactive effects."
        )
    else:
        boundary = "Equipment / system level"
        boundary_note = (
            "A single ECM with sub-metering available — draw the boundary tightly "
            "around the affected equipment to isolate savings."
        )

    # --- Model Form ---
    if (boundary_access == "Calibrated simulation model available or feasible"
            or baseline_data == "Little or no pre-intervention data"):
        model_form = "Engineering / physical simulation model"
        if boundary_access == "Calibrated simulation model available or feasible":
            model_note = (
                "Construct the counterfactual using a calibrated energy simulation "
                "(e.g., EnergyPlus, eQUEST). The model represents physics-based "
                "relationships and can handle complex interactions."
            )
        else:
            model_note = (
                "Without pre-intervention data, a statistical counterfactual has no "
                "foundation. A calibrated simulation is the recommended path — it can "
                "construct the baseline from building characteristics and physics-based "
                "relationships rather than historical metered data."
            )
        # Also update boundary when simulation is driven by data gap
        if baseline_data == "Little or no pre-intervention data" and boundary != "Whole-building (simulation-defined boundary)":
            boundary = "Whole-building (simulation-defined boundary)"
            boundary_note = (
                "Insufficient baseline data requires a simulation-based counterfactual. "
                "The simulation defines the measurement boundary across the building."
            )
    elif load_variability == "Constant or near-constant load (e.g., lighting, base-load motors)":
        if budget_accuracy == "Minimize cost — stipulated values acceptable where defensible":
            model_form = "Stipulated key-parameter model"
            model_note = (
                "For constant-load equipment, the counterfactual can be constructed by "
                "measuring the key operating parameter (e.g., runtime hours) and "
                "stipulating stable parameters (e.g., nameplate wattage). This is the "
                "simplest and lowest-cost approach when the load doesn't vary."
            )
        else:
            model_form = "Direct measurement (metered before/after comparison)"
            model_note = (
                "Constant-load equipment with sub-metering — continuously meter energy "
                "use before and after the intervention. The counterfactual is the "
                "measured baseline load profile projected into the reporting period."
            )
    elif independent_vars == "Multiple variables (temperature, occupancy, production, etc.)":
        if (num_ecms == "Multiple ECMs with interactive effects"
                or boundary == "Whole-building meter"):
            model_form = "Multivariable statistical regression or hybrid model"
            model_note = (
                "Multiple independent variables drive energy use. Use a multivariable "
                "regression (or a hybrid statistical + engineering approach) to construct "
                "the counterfactual. Consider change-point models if the relationship "
                "shifts at balance-point temperatures."
            )
        else:
            model_form = "Multivariable statistical regression"
            model_note = (
                "Energy use depends on multiple independent variables. A multivariable "
                "regression model at the equipment level constructs the counterfactual "
                "by predicting what baseline energy use would have been under "
                "reporting-period conditions."
            )
    else:
        # Single variable or none, variable load
        model_form = "Single-variable statistical regression"
        model_note = (
            "Energy use varies with a single dominant independent variable "
            "(typically outdoor air temperature). A regression model (linear or "
            "change-point) predicts baseline energy under reporting-period conditions "
            "to form the counterfactual."
        )

    # --- Duration ---
    if baseline_data == "12+ months of interval or monthly data":
        duration = "12+ month baseline, 12+ month reporting period recommended"
        duration_note = (
            "A full year of baseline data captures seasonal patterns. Match with "
            "at least 12 months of reporting-period data for robust savings estimates."
        )
    elif baseline_data == "3–11 months of data":
        duration = "Partial baseline — extend reporting period for confidence"
        duration_note = (
            "Less than a full year of baseline data means seasonal gaps. Extend the "
            "reporting period or use engineering judgment to fill gaps. Flag increased "
            "uncertainty in the savings estimate."
        )
    else:
        # Little or no baseline data — simulation is now the recommended path
        duration = "Simulation-derived baseline — reporting period data validates model"
        duration_note = (
            "With no measured baseline, the simulation model defines the "
            "counterfactual. Use reporting-period data to validate model calibration."
        )

    # --- Signal-to-noise warning ---
    signal_note = None
    if savings_signal == "Small — may be difficult to distinguish from noise (<10%)":
        if boundary == "Whole-building meter":
            signal_note = (
                "**Signal-to-noise warning:** Small savings at the whole-building level "
                "may be statistically indistinguishable from model noise. Consider "
                "tightening the measurement boundary to equipment-level if possible, "
                "or plan for a longer reporting period to accumulate detectable savings."
            )
        else:
            signal_note = (
                "**Signal-to-noise note:** Small expected savings — ensure the model's "
                "prediction uncertainty (fractional savings uncertainty at 95% CI) is "
                "smaller than the expected savings to have a meaningful result."
            )

    rationale = []
    rationale.append(f"**Boundary:** {boundary_note}")
    rationale.append(f"**Model form:** {model_note}")
    rationale.append(f"**Duration:** {duration_note}")
    if signal_note:
        rationale.append(signal_note)

    return boundary, model_form, duration, rationale


boundary_rec, model_rec, duration_rec, rationale_bullets = build_recommendation()


# ─── Decision Tree Diagram (Graphviz) ────────────────────────────────────────

dot = graphviz.Digraph(comment="CfD Decision Tree", format="svg")
dot.attr(rankdir="TB", fontname="Helvetica", bgcolor="transparent")
dot.attr("node", fontname="Helvetica", fontsize="11", style="filled", shape="box",
         color="#5c4a3a", fontcolor="white")
dot.attr("edge", fontname="Helvetica", fontsize="10", color="#8b7355")

# Color palette — warm tones
q_color = "#6b4226"     # warm brown — decision questions
term_boundary = "#b8860b"  # dark goldenrod — boundary outcomes
term_model = "#8b6914"     # darker gold — model form outcomes
term_dur = "#a0522d"       # sienna — duration notes

# ── Question nodes ──
questions = [
    ("Q1", "What measurement boundary\nis accessible?"),
    ("Q2", "Is the load constant\nor variable?"),
    ("Q3", "How many independent\nvariables drive energy use?"),
    ("Q4", "Are savings large enough\nto detect at this boundary?"),
    ("Q5", "How much baseline\ndata is available?"),
]
for nid, label in questions:
    dot.node(nid, label, fillcolor=q_color, shape="diamond", width="3", height="1.2")

# ── Terminal / design outcome nodes ──
terminals = [
    ("T_SIM", "Engineering / Physical\nSimulation Counterfactual\n(simulation-defined boundary)"),
    ("T_STIP", "Equipment-Level\nStipulated Key-Parameter\nCounterfactual"),
    ("T_DIRECT", "Equipment-Level\nDirect Measurement\nCounterfactual"),
    ("T_EQ_REG", "Equipment-Level\nStatistical Regression\nCounterfactual"),
    ("T_WB_REG", "Whole-Building\nStatistical Regression\nCounterfactual"),
    ("T_WB_MULTI", "Whole-Building\nMultivariable / Hybrid\nCounterfactual"),
    ("T_NARROW", "Consider Tightening\nBoundary to Equipment\n(small signal at WB level)"),
]
for nid, label in terminals:
    dot.node(nid, label, fillcolor=term_boundary, shape="box",
             style="filled,rounded", width="2.5", height="1")

# ── Edges ──
dot.edge("Q1", "T_SIM", label="Simulation model\navailable")
dot.edge("Q1", "Q4", label="Whole-building\nmeter only")
dot.edge("Q1", "Q2", label="Sub-meter on\naffected equipment")

dot.edge("Q2", "T_STIP", label="Constant load\n(budget-constrained)")
dot.edge("Q2", "T_DIRECT", label="Constant load\n(accuracy priority)")
dot.edge("Q2", "Q3", label="Variable load")

dot.edge("Q3", "T_EQ_REG", label="Single variable\n(e.g., temperature)")
dot.edge("Q3", "Q5", label="Multiple variables")

dot.edge("Q4", "T_WB_REG", label="Yes — savings\ndetectable")
dot.edge("Q4", "T_NARROW", label="No — signal\ntoo small")

dot.edge("Q5", "T_WB_MULTI", label="12+ months\navailable")
dot.edge("Q5", "T_EQ_REG", label="Limited data —\nsimplify model")
dot.edge("Q5", "T_SIM", label="No baseline data —\nuse simulation")

# Highlight the recommended terminal node based on model_rec
highlight_map = {
    "Engineering / physical simulation model": "T_SIM",
    "Stipulated key-parameter model": "T_STIP",
    "Direct measurement (metered before/after comparison)": "T_DIRECT",
    "Single-variable statistical regression": "T_EQ_REG",
    "Multivariable statistical regression": "T_EQ_REG",
    "Multivariable statistical regression or hybrid model": "T_WB_MULTI",
}
highlight_id = highlight_map.get(model_rec)
# Also account for boundary
if boundary_rec == "Whole-building meter" and model_rec == "Single-variable statistical regression":
    highlight_id = "T_WB_REG"
if highlight_id:
    # Re-declare the node with gold highlight border
    for nid, label in terminals:
        if nid == highlight_id:
            dot.node(nid, label, fillcolor=term_boundary, shape="box",
                     style="filled,rounded,bold", width="2.5", height="1",
                     penwidth="4", color="#facc15")
            break


# ─── Display ──────────────────────────────────────────────────────────────────

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Decision Tree")
    st.graphviz_chart(dot, use_container_width=True)

with col2:
    st.subheader("Your Counterfactual Design")
    st.markdown(
        "*Based on your project context, here is the recommended counterfactual design:*"
    )

    # Summary card
    st.markdown(f"**Boundary:** {boundary_rec}")
    st.markdown(f"**Model Form:** {model_rec}")
    st.markdown(f"**Duration:** {duration_rec}")
    st.divider()

    st.markdown("#### Why this design?")
    for bullet in rationale_bullets:
        st.markdown(bullet)

    st.divider()
    st.markdown(
        "**Savings =** Counterfactual prediction under reporting-period conditions "
        "**minus** measured reporting-period energy use."
    )
    st.markdown("Report savings in **kWh** (electricity) or **Therms** (natural gas).")


# ─── Three Dimensions Reference Table ────────────────────────────────────────

st.subheader("The Three Design Dimensions")
st.markdown("""
Every M&V counterfactual design is defined by three choices:

| Dimension | Question | Options |
|-----------|----------|---------|
| **Boundary** | What do you draw the measurement boundary around? | Equipment/system, whole building, campus/portfolio |
| **Model Form** | How do you construct the counterfactual? | Stipulated parameters, statistical regression (single/multi-variable, change-point), engineering simulation, hybrid |
| **Duration** | How much data do you need? | Baseline period length, reporting period length, data granularity (monthly bills vs. interval data) |

These three dimensions replace protocol labels (A, B, C, D) with **explicit design choices** — making the reasoning transparent and the plan defensible.
""")


# ─── Common Counterfactual Design Patterns ────────────────────────────────────

with st.expander("Common Counterfactual Design Patterns"):
    st.markdown("""
| Pattern | Boundary | Model Form | Duration | Typical Use Case |
|---------|----------|------------|----------|-----------------|
| **Equipment-level stipulated** | Equipment/system | Key parameter measured, others stipulated | Pre/post spot measurements | Lighting retrofits, constant-load motor replacements |
| **Equipment-level regression** | Equipment/system | Statistical regression on sub-metered data | 12+ month baseline, continuous reporting | VFDs, chillers, variable-load HVAC equipment |
| **Whole-building regression** | Whole building | Weather-normalized regression on utility bills | 12+ months pre & post billing data | Multi-ECM retrofits where savings > 15–20% of total |
| **Whole-building multivariable** | Whole building | Multivariable regression (weather + occupancy + production) | 12+ months interval data | Complex facilities with multiple load drivers |
| **Simulation counterfactual** | Whole building (modeled) | Calibrated energy simulation | Model calibrated to baseline; post-retrofit validation | New construction, complex interactions, no measured baseline |

These are patterns, not rigid categories. Mix dimensions as the project demands.
""")



# ─── Footer ──────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    "Built on the [Counterfactual Designs](https://counterfactual-designs.com) framework "
    "by Steve Kromer. "
    "See also: [CfDesigns interactive platform](https://cfdesigns.vercel.app) · "
    "[IPMVP-aligned course](https://mv-course.vercel.app)"
)
