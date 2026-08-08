"""Interactive FlightPulse analytics and prediction dashboard."""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DATABASE_URL, METRICS_PATH, MODEL_PATH  # noqa: E402

st.set_page_config(page_title="FlightPulse", page_icon="✈️", layout="wide")
st.title("FlightPulse")
st.caption("Explore departure-delay patterns and estimate the risk of a 15+ minute delay.")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data
def read_flights() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM flights WHERE cancelled = 0", create_engine(DATABASE_URL))


def read_model_metrics() -> dict[str, float | int | str]:
    return json.loads(METRICS_PATH.read_text())


try:
    flights = read_flights()
except Exception:
    st.error("No analytics database found. Run `make demo`, `make load`, and `make train` first.")
    st.stop()

flight_dates = pd.to_datetime(flights["flight_date"])
st.caption(
    "Data source: U.S. Bureau of Transportation Statistics · "
    f"{flight_dates.min():%B %d, %Y}–{flight_dates.max():%B %d, %Y} · "
    "Local SQLite database"
)

st.sidebar.header("Filter historical analysis")
carrier_filter = st.sidebar.selectbox("Carrier", ["All", *sorted(flights["carrier"].unique())])
origin_filter = st.sidebar.selectbox("Origin", ["All", *sorted(flights["origin"].unique())])
destination_filter = st.sidebar.selectbox(
    "Destination", ["All", *sorted(flights["destination"].unique())]
)

filtered = flights
if carrier_filter != "All":
    filtered = filtered[filtered["carrier"] == carrier_filter]
if origin_filter != "All":
    filtered = filtered[filtered["origin"] == origin_filter]
if destination_filter != "All":
    filtered = filtered[filtered["destination"] == destination_filter]

if filtered.empty:
    st.warning("No flights match this filter combination. Change one or more filters.")
    st.stop()

total = len(filtered)
delay_rate = 100 * filtered["is_delayed"].mean()
average_delay = filtered["departure_delay_minutes"].mean()
c1, c2, c3 = st.columns(3)
c1.metric("Analyzed flights", f"{total:,}")
c2.metric("Delayed 15+ minutes", f"{delay_rate:.1f}%")
c3.metric("Average departure delay", f"{average_delay:.1f} min")

carrier = filtered.groupby("carrier", as_index=False).agg(
    flights=("is_delayed", "size"), delay_rate=("is_delayed", "mean")
)
carrier["delay_rate"] *= 100
st.plotly_chart(
    px.bar(
        carrier, x="carrier", y="delay_rate", hover_data=["flights"], title="Delay rate by carrier"
    ),
    use_container_width=True,
)

hourly = filtered.groupby("scheduled_departure_hour", as_index=False)["is_delayed"].mean()
hourly["delay_rate"] = hourly.pop("is_delayed") * 100
st.plotly_chart(
    px.line(
        hourly,
        x="scheduled_departure_hour",
        y="delay_rate",
        markers=True,
        title="Delay rate by departure hour",
    ),
    use_container_width=True,
)

routes = (
    filtered.assign(route=filtered["origin"] + " → " + filtered["destination"])
    .groupby("route", as_index=False)
    .agg(flights=("is_delayed", "size"), delay_rate=("is_delayed", "mean"))
    .query("flights >= 10")
    .nlargest(10, "delay_rate")
)
routes["delay_rate"] *= 100
st.dataframe(routes, use_container_width=True, hide_index=True)

st.header("Model performance")
if METRICS_PATH.exists():
    metrics = read_model_metrics()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
    m2.metric("Accuracy", f"{metrics['accuracy']:.1%}")
    m3.metric("Precision", f"{metrics['precision']:.1%}")
    m4.metric("Recall", f"{metrics['recall']:.1%}")
    st.caption(
        f"Chronological evaluation: trained on {metrics['train_start']} through "
        f"{metrics['train_end']}; tested on {metrics['test_start']} through "
        f"{metrics['test_end']}. Results from one month do not establish performance "
        "across seasons."
    )
else:
    st.info("Train the model with `make train` to generate evaluation metrics.")

st.header("Predict delay risk")
if not MODEL_PATH.exists():
    st.info("Train the model with `make train` to enable predictions.")
else:
    model = joblib.load(MODEL_PATH)
    with st.form("prediction"):
        carrier_input = st.selectbox("Carrier", sorted(flights["carrier"].unique()))
        origin = st.selectbox("Origin", sorted(flights["origin"].unique()))
        destination = st.selectbox("Destination", sorted(flights["destination"].unique()))
        hour = st.slider("Scheduled departure hour", 0, 23, 12)
        month = st.slider("Month", 1, 12, 6)
        day = st.selectbox("Day", DAYS)
        submitted = st.form_submit_button("Estimate risk")
    if submitted:
        row = pd.DataFrame(
            [
                {
                    "carrier": carrier_input,
                    "origin": origin,
                    "destination": destination,
                    "scheduled_departure_hour": hour,
                    "month": month,
                    "day_of_week": DAYS.index(day),
                }
            ]
        )
        probability = model.predict_proba(row)[0, 1]
        st.metric("Estimated probability of 15+ minute delay", f"{probability:.1%}")
