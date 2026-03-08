import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.title("CrewPlanner")
st.caption("Airline Crew Planning, Forecasting & Rostering Tool")

# -----------------------------
# USER INPUT SECTION
# -----------------------------

st.sidebar.header("INPUTS")

st.sidebar.subheader("Aircraft Operations")

aircraft = st.sidebar.number_input(
"INPUT: Number of Aircraft",
1,1000,430)

flights_per_aircraft = st.sidebar.slider(
"INPUT: Flights per Aircraft per Day",
1,10,6)

avg_flight_hours = st.sidebar.slider(
"INPUT: Average Flight Duration (hours)",
1.0,5.0,2.0)

st.sidebar.subheader("Aircraft Capacity")

seats = st.sidebar.number_input(
"INPUT: Seats per Aircraft",
50,300,180)

load_factor = st.sidebar.slider(
"INPUT: Load Factor",
0.5,1.0,0.85)

st.sidebar.subheader("DGCA Rules")

pilot_max_hours = st.sidebar.slider(
"INPUT: Max Pilot Flying Hours per Day",
6,12,8)

reserve_buffer = st.sidebar.slider(
"INPUT: Reserve Crew Buffer",
0.05,0.25,0.15)

st.sidebar.subheader("Existing Workforce")

existing_pilots = st.sidebar.number_input(
"INPUT: Existing Pilots",
100,10000,5000)

existing_cabin = st.sidebar.number_input(
"INPUT: Existing Cabin Crew",
100,20000,9000)

pilot_training_months = st.sidebar.slider(
"INPUT: Pilot Training Duration (months)",
1,12,5)

# -----------------------------
# DEMAND FORECAST
# -----------------------------

st.header("1️⃣ Demand Forecast")

st.write("INPUT: Enter historical passenger demand")

months = st.number_input("Number of Historical Months",3,24,12)

demand_data = []

for i in range(months):
    value = st.number_input(
        f"Passengers Month {i+1}",
        100000,20000000,1000000)
    demand_data.append(value)

df = pd.DataFrame({
"month":np.arange(len(demand_data)),
"passengers":demand_data
})

X = df["month"].values.reshape(-1,1)
y = df["passengers"].values

model = LinearRegression()
model.fit(X,y)

future_month = len(demand_data)
forecast = model.predict([[future_month]])[0]

st.success(f"Forecast Passenger Demand: {int(forecast):,}")

fig,ax = plt.subplots()
ax.plot(df["month"],df["passengers"],label="Historical")
ax.scatter(future_month,forecast,color="red",label="Forecast")
ax.legend()
st.pyplot(fig)

# -----------------------------
# FLIGHTS REQUIRED
# -----------------------------

st.header("2️⃣ Flights Required")

st.code("""
Flights Required =
Passenger Demand / (Seats × Load Factor)
""")

flights_required = forecast / (seats * load_factor)

daily_flights = flights_required / 30

st.write(f"Flights per Month: {int(flights_required)}")
st.write(f"Flights per Day: {int(daily_flights)}")

# -----------------------------
# TOTAL FLIGHT HOURS
# -----------------------------

st.header("3️⃣ Total Flight Hours")

st.code("""
Total Flight Hours =
Flights per Day × Average Flight Duration
""")

total_flight_hours = daily_flights * avg_flight_hours

st.write(f"Total Flight Hours per Day: {round(total_flight_hours,2)}")

# -----------------------------
# CREW REQUIREMENT
# -----------------------------

st.header("4️⃣ Crew Requirement Logic")

st.write("""
Each flight typically requires:

• 2 pilots (Captain + First Officer)  
• 4 cabin crew  
• ~8 ground staff for turnaround
""")

# Pilot calculation based on duty hours

st.subheader("Pilot Calculation")

st.code("""
Pilots Needed =
Total Flight Hours / Max Pilot Flying Hours
""")

pilots_needed = total_flight_hours / pilot_max_hours

pilot_pairs = pilots_needed / 2

# Add buffer
pilots_needed = pilots_needed * (1 + reserve_buffer)

# Cabin crew based on flights
cabin_needed = daily_flights * 4
cabin_needed = cabin_needed * (1 + reserve_buffer)

# Ground staff
ground_needed = daily_flights * 8
ground_needed = ground_needed * (1 + reserve_buffer)

crew_table = pd.DataFrame({
"Role":["Pilots","Pilot Pairs","Cabin Crew","Ground Staff"],
"Required":[int(pilots_needed),int(pilot_pairs),int(cabin_needed),int(ground_needed)]
})

st.table(crew_table)

# -----------------------------
# CREW UTILIZATION
# -----------------------------

st.header("5️⃣ Pilot Utilization")

st.code("""
Pilot Utilization =
Total Flight Hours /
(Existing Pilots × Max Pilot Hours)
""")

pilot_utilization = total_flight_hours / (existing_pilots * pilot_max_hours)

st.write(f"Pilot Utilization: {round(pilot_utilization*100,2)} %")

if pilot_utilization < 0.7:
    st.warning("Under-utilization: More pilots than needed")
elif pilot_utilization <= 0.85:
    st.success("Optimal Utilization")
else:
    st.error("Over-utilization: Risk of delays")

# -----------------------------
# AIRCRAFT PER PILOT
# -----------------------------

st.header("6️⃣ Aircraft per Pilot")

aircraft_per_pilot = aircraft / existing_pilots

st.write(f"Aircraft per Pilot Ratio: {round(aircraft_per_pilot,3)}")

# -----------------------------
# HIRING REQUIREMENT
# -----------------------------

st.header("7️⃣ Hiring Requirement")

pilot_shortage = pilots_needed - existing_pilots

if pilot_shortage > 0:
    st.write(f"Pilots to Hire: {int(pilot_shortage)}")
    st.write(f"Pilot Training Time: {pilot_training_months} months")
else:
    st.write("No additional pilots required")

# -----------------------------
# CREW ROSTERING
# -----------------------------

st.header("8️⃣ Crew Rostering")

st.write("""
Crew divided into three shifts:

Morning  
Afternoon  
Night
""")

shifts = 3

pilot_shift = int(pilots_needed / shifts)
cabin_shift = int(cabin_needed / shifts)

roster = pd.DataFrame({
"Shift":["Morning","Afternoon","Night"],
"Pilots":[pilot_shift]*3,
"Cabin Crew":[cabin_shift]*3
})

st.table(roster)

# -----------------------------
# CONSULTANT INSIGHT
# -----------------------------

st.header("Consultant Insight")

st.write("""
Recommended operating conditions:

• Maintain pilot utilization between **70%–85%**

• Maintain **10–15% reserve crew**

• Begin pilot training **4–6 months before expected demand increase**

• Avoid utilization above **90%** to reduce operational delays
""")
