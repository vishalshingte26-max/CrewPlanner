import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.title("CrewPlanner")
st.caption("Airline Crew Planning, Optimization & Rostering Tool")

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------

st.sidebar.header("Airline Operations")

aircraft = st.sidebar.number_input("Number of Aircraft",1,1000,430)
flights_per_aircraft = st.sidebar.slider("Flights per Aircraft per Day",1,10,6)
avg_flight_hours = st.sidebar.slider("Average Flight Hours",1.0,5.0,2.0)

seats = st.sidebar.number_input("Seats per Aircraft",50,300,180)
load_factor = st.sidebar.slider("Load Factor",0.5,1.0,0.85)

pilot_max_hours = st.sidebar.slider("Pilot Max Flying Hours (DGCA)",6,12,8)
reserve_buffer = st.sidebar.slider("Reserve Buffer %",0.05,0.25,0.15)

st.sidebar.header("Existing Crew")

existing_pilots = st.sidebar.number_input("Existing Pilots",100,10000,5000)
existing_cabin = st.sidebar.number_input("Existing Cabin Crew",100,20000,9000)

pilot_training_months = st.sidebar.slider("Pilot Training Months",1,12,5)

# -----------------------------
# DEMAND FORECAST
# -----------------------------

st.header("1️⃣ Demand Forecast")

months = st.number_input("Historical Months",3,24,12)

data = []
for i in range(months):
    value = st.number_input(f"Passengers Month {i+1}",100000,20000000,1000000)
    data.append(value)

df = pd.DataFrame({
    "month": np.arange(len(data)),
    "passengers": data
})

X = df["month"].values.reshape(-1,1)
y = df["passengers"].values

model = LinearRegression()
model.fit(X,y)

future_month = len(data)
forecast = model.predict([[future_month]])[0]

st.write(f"Forecast Passengers Next Month: **{int(forecast):,}**")

fig,ax = plt.subplots()
ax.plot(df["month"],df["passengers"],label="Historical")
ax.scatter(future_month,forecast,color="red",label="Forecast")
ax.legend()
ax.set_xlabel("Month")
ax.set_ylabel("Passengers")
st.pyplot(fig)

# -----------------------------
# FLIGHTS REQUIRED
# -----------------------------

st.header("2️⃣ Flights Required")

flights_required = forecast / (seats * load_factor)

st.write("Calculation:")

st.code("""
Flights = Forecast Demand / (Aircraft Seats × Load Factor)
""")

st.write(f"Flights required per month: **{int(flights_required)}**")

daily_flights = flights_required / 30

# -----------------------------
# FLIGHT HOURS
# -----------------------------

st.header("3️⃣ Total Flight Hours")

total_flight_hours = daily_flights * avg_flight_hours

st.write("Calculation:")

st.code("""
Total Flight Hours = Daily Flights × Average Flight Time
""")

st.write(f"Total Flight Hours Needed per Day: **{round(total_flight_hours,2)} hours**")

# -----------------------------
# CREW REQUIREMENT
# -----------------------------

st.header("4️⃣ Required Crew (Before Optimization)")

pilot_shifts = total_flight_hours / pilot_max_hours

pilots_required = pilot_shifts * (1 + reserve_buffer)
cabin_required = daily_flights * 4 * (1 + reserve_buffer)
ground_required = daily_flights * 8 * (1 + reserve_buffer)

st.write("Calculation:")

st.code("""
Pilots Needed = Total Flight Hours / Pilot Max Hours
Cabin Crew = Flights × 4
Ground Staff = Flights × 8
Reserve Buffer Added
""")

crew_df = pd.DataFrame({
    "Role":["Pilots","Cabin Crew","Ground Staff"],
    "Required":[int(pilots_required),int(cabin_required),int(ground_required)]
})

st.table(crew_df)

# -----------------------------
# EXISTING CREW UTILIZATION
# -----------------------------

st.header("5️⃣ Existing Crew Utilization")

pilot_utilization = total_flight_hours / (existing_pilots * pilot_max_hours)

st.write(f"Existing Pilots: **{existing_pilots}**")

st.write(f"Pilot Utilization: **{round(pilot_utilization*100,2)}%**")

if existing_pilots >= pilots_required:
    st.success("Current pilots are sufficient")
else:
    st.error("Pilot shortage detected")

# -----------------------------
# AIRCRAFT PER PILOT
# -----------------------------

st.header("6️⃣ Aircraft Allocation")

aircraft_per_pilot = aircraft / existing_pilots

st.write(f"Aircraft per Pilot Ratio: **{round(aircraft_per_pilot,3)}**")

st.write("This indicates how many aircraft each pilot supports operationally.")

# -----------------------------
# HIRING REQUIREMENT
# -----------------------------

st.header("7️⃣ Hiring Requirement")

pilot_shortage = int(pilots_required - existing_pilots)

if pilot_shortage > 0:
    st.write(f"Pilots to Hire: **{pilot_shortage}**")
    st.write(f"Pilot Training Time: **{pilot_training_months} months**")
else:
    st.write("No additional pilots required")

# -----------------------------
# ROSTERING
# -----------------------------

st.header("8️⃣ Crew Rostering")

shifts = 3

pilot_shift = int(pilots_required / shifts)
cabin_shift = int(cabin_required / shifts)

roster_df = pd.DataFrame({
    "Shift":["Morning","Afternoon","Night"],
    "Pilots":[pilot_shift]*3,
    "Cabin Crew":[cabin_shift]*3
})

st.table(roster_df)

# -----------------------------
# RISK INDICATOR
# -----------------------------

st.header("9️⃣ Operational Risk Indicator")

if pilot_utilization > 0.9:
    st.error("High Delay Risk")
elif pilot_utilization > 0.8:
    st.warning("Moderate Operational Risk")
else:
    st.success("Operations Stable")

# -----------------------------
# CONSULTANT INSIGHT
# -----------------------------

st.header("Consultant Recommendation")

st.write("""
• Maintain pilot utilization between **70% and 85%**

• Maintain **10-15% reserve crew**

• Start training **4-6 months before expected demand increase**

• Avoid utilization above **90%** to reduce operational delays
""")
