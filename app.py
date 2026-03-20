import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(layout="wide")


# =====================================
# LOAD DATA
# =====================================
model = joblib.load("hvac_forecast_model.pkl")
features = joblib.load("hvac_model_features.pkl")
df = pd.read_csv("plant_data.csv", index_col=0, parse_dates=True)


# =====================================
# FORECAST
# =====================================
last_row = df.iloc[-1]
last_time = df.index[-1]

X_last = last_row[features].values.reshape(1, -1)

forecast_kw = model.predict(X_last)[0]
forecast_time = last_time + pd.Timedelta(hours=1)

connected_load = 1449.6
tower_capacity_kw = 8800

kw_last = last_row["CH4_Total_Plant_Room_Consumption_kW"]
tr_last = last_row["CH4_Total_Plant_Room_Tonnage_TR"]

plant_status = "Operating" if last_row["ANY_CH_ON"] == 1 and tr_last > 15 else "Idle"

plant_util = (forecast_kw / connected_load) * 100

eff_last = kw_last / tr_last if tr_last > 15 else None
derived_TR = forecast_kw / eff_last if eff_last else None

Qreject = (derived_TR * 3.517 + forecast_kw) if derived_TR else None
tower_util = (Qreject / tower_capacity_kw) * 100 if Qreject else None


# =====================================
# HEADER
# =====================================
st.markdown("<h2 style='text-align:center;'>ENERGY – NEXT HOUR</h2>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align:center;'>Upcoming Hour Forecast</h5>", unsafe_allow_html=True)

# ✅ SPACE ADDED
st.markdown("<br>", unsafe_allow_html=True)


# =====================================
# LOCATION (INDIA ONLY)
# =====================================
location = st.selectbox(
    "Select Location",
    ["Kochi", "Chennai", "Delhi", "Mumbai", "Bangalore"]
)


# =====================================
# COMMON INFO
# =====================================
st.write(f"**Plant Status:** {plant_status}")
st.write(f"**Upcoming Hour:** {forecast_time.strftime('%d-%b-%Y %H:%M')}")


# ✅ ADD SPACE HERE
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
# =====================================
# TABS
# =====================================
tab1, tab2, tab3 = st.tabs([
    "⚡ Electrical Load Forecast",
    "❄ Cooling Demand Forecast",
    "🌡 Condenser System Forecast"
])


# =====================================
# 🔷 TAB 1
# =====================================
with tab1:

    col1, col2 = st.columns([1.2,1])

    with col1:
        st.write("### Electrical Load Forecast")
        st.write(f"Forecasted Plant Power : {forecast_kw:.2f} kW")
        st.write(f"Expected Plant Utilization : {plant_util:.2f} %")
        st.write(f"Projected Energy (Next Hour) : {forecast_kw:.2f} kWh")

    with col2:
        df_last = df.tail(24)

        fig, ax = plt.subplots(figsize=(6,3))

        ax.plot(df_last.index, df_last["CH4_Total_Plant_Room_Consumption_kW"], marker='o')

        ax.scatter(forecast_time, forecast_kw, color='orange', s=80)

        ax.plot(
            [df_last.index[-1], forecast_time],
            [df_last.iloc[-1]["CH4_Total_Plant_Room_Consumption_kW"], forecast_kw],
            linestyle='--', color='orange'
        )

        # ✅ CLEAN X AXIS
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b\n%H:%M'))
        plt.setp(ax.get_xticklabels(), rotation=0)

        ax.annotate(
            forecast_time.strftime("%d-%b %H:%M"),
            (forecast_time, forecast_kw),
            xytext=(0,25),
            textcoords='offset points',
            ha='center',
            fontsize=9
        )

        ax.set_title("Plant Power Trend + Forecast (Last 24 Hours)")
        ax.grid(True)

        st.pyplot(fig)


# =====================================
# 🔷 TAB 2
# =====================================
with tab2:

    col1, col2 = st.columns([1.2,1])

    with col1:
        st.write("### Cooling Demand Forecast")
        st.write(f"Current Plant Efficiency : {round(eff_last,3) if eff_last else 0} kW/TR")
        st.write(f"Expected Cooling Load (Next Hour) : {round(derived_TR,2) if derived_TR else 0} TR")

    with col2:
        df_last = df.tail(24)

        fig, ax = plt.subplots(figsize=(6,3))

        ax.plot(df_last.index, df_last["CH4_Total_Plant_Room_Tonnage_TR"], marker='o')

        if derived_TR:
            ax.scatter(forecast_time, derived_TR, color='orange', s=80)

            ax.annotate(
                forecast_time.strftime("%d-%b %H:%M"),
                (forecast_time, derived_TR),
                xytext=(0,25),
                textcoords='offset points',
                ha='center',
                fontsize=9
            )

        # ✅ CLEAN X AXIS
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b\n%H:%M'))
        plt.setp(ax.get_xticklabels(), rotation=0)

        # ✅ TITLE FIXED
        ax.set_title("Plant TR Trend (Last 24 Hours)")
        ax.grid(True)

        st.pyplot(fig)


# =====================================
# 🔷 TAB 3
# =====================================
with tab3:

    col1, col2 = st.columns([1.2,1])

    with col1:
        st.write("### Condenser System Forecast")
        st.write(f"Expected Cooling Tower Thermal Load : {round(Qreject/1000,2) if Qreject else 0} MW")
        st.write(f"Expected Cooling Tower Utilization : {round(tower_util,2) if tower_util else 0} %")

        status = "LOW" if tower_util and tower_util < 30 else "NORMAL" if tower_util and tower_util < 80 else "HIGH"
        st.write(f"Tower Load Status : {status}")

    with col2:
        color = "green" if status=="LOW" else "orange" if status=="NORMAL" else "red"

        st.markdown(
            f"""
            <div style="
                background-color:{color}33;
                padding:40px;
                text-align:center;
                border-radius:10px;">
                <h2 style="color:{color};">{status} LOAD</h2>
                <p>Cooling Tower Condition</p>
            </div>
            """,
            unsafe_allow_html=True
        )