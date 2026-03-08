import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.title("CrewPlanner")
st.caption("Airline Crew Planning, Forecasting & Rostering Tool")

# =====================================================
# SECTION 1 — USER INPUTS
# =====================================================

st.sidebar.header("INPUT SECTION")

st.sidebar.subheader("Aircraft Operations")

aircraft = st.sidebar.number_input(
"INPUT: Total Aircraft in Fleet",
1,1000,430)

flights_per_aircraft = st.sidebar.slider(
"INPUT: Flights per Aircraft per Day",
1,10,6)

avg_flight_hours = st.sidebar.slider(
"INPUT: Average Flight Duration (Hours)",
1.0,5.0,2.0)

st.sidebar.subheader("Aircraft Capacity")

seats = st.sidebar.number_input(
"INPUT: Seats per Aircraft",
50,300,180)

load_factor = st.sidebar.slider(
"INPUT: Expected Load Factor",
0.5,1.0,0.85)

st.sidebar.subheader("DGCA Rules")

pilot_max_hours = st.sidebar.slider(
"INPUT: Max Pilot Flying Hours per Day (DGCA)",
6,12,8)

reserve_buffer = st.sidebar.slider(
"INPUT: Reserve Crew Buffer %",
0.05,0.25,0.15)

st.sidebar.subheader("Existing Workforce")

existing_pilots = st.sidebar.number_input(
"INPUT: Current Number of Pilots",
100,10000,5000)

existing_cabin = st.sidebar.number_input(
"INPUT: Current Cabin Crew",
100,20000,9000)

pilot_training = st.sidebar.slider(
"INPUT: Pilot Training Duration (Months)",
1,12,5)

# =====================================================
# SECTION 2 — DEMAND FORECAST
# =====================================================

st.header("1️⃣ Demand Forecast")

st.write("INPUT: Enter historical passenger demand.")

months = st.number_input("Number of Historical Months",3,24,12)

demand_data = []

for i in range(months):
    value = st.number_input(
        f"INPUT: Passengers Month {i+1}",
        100000,20000000,1000000
    )
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

st.success(f"Forecast Passengers Next Month: {int(forecast):,}")

fig,ax = plt.subplots()
ax.plot(df["month"],df["passengers"],label="Historical")
ax.scatter(future_month,forecast,color="red",label="Forecast")
ax.legend()
st.pyplot(fig)

# =====================================================
# SECTION 3 — FLIGHTS REQUIRED
# =====================================================

st.header("2️⃣ Flights Required")

st.write("Formula Used:")

st.code("""
Flights Required =
Passenger Demand / (Seats × Load Factor)
""")

flights_required = forecast / (seats * load_factor)

st.write(f"Flights Required per Month: {int(flights_required)}")

daily_flights = flights_required / 30

st.write(f"Flights Required per Day: {int(daily_flights)}")

# =====================================================
# SECTION 4 — TOTAL FLIGHT HOURS
# =====================================================

st.header("3️⃣ Total Flight Hours")

st.write("Formula Used:")

st.code("""
Total Flight Hours =
Daily Flights × Average Flight Duration
""")

total_flight_hours = daily_flights * avg_flight_hours

st.write(f"Total Flight Hours Needed Per Day: {round(total_flight_hours,2)}")

# =====================================================
# SECTION 5 — CREW PER FLIGHT RULE
# =====================================================

st.header("4️⃣ Crew Requirement per Flight")

st.write("""
Each commercial flight requires:

• **2 Pilots (Pilot Pair)**  
• **4 Cabin Crew**  
• **8 Ground Staff**
""")

pilots_per_flight = 2
cabin_per_flight = 4
ground_per_flight = 8

pilot_pair_requirement = daily_flights * pilots_per_flight
cabin_requirement = daily_flights * cabin_per_flight
ground_requirement = daily_flights * ground_per_flight

# =====================================================
# SECTION 6 — PILOT DUTY CONSTRAINT
# =====================================================

st.header("5️⃣ DGCA Duty Constraint")

st.write("Formula Used:")

st.code("""
Pilot Requirement based on Duty Hours =
Total Flight Hours / Max Pilot Flying Hours
""")

pilot_hour_requirement = total_flight_hours / pilot_max_hours

st.write(f"Pilot Requirement Based on Duty Hours: {round(pilot_hour_requirement,2)}")

# =====================================================
# SECTION 7 — FINAL PILOT REQUIREMENT
# =====================================================

st.header("6️⃣ Final Pilot Requirement")

st.write("""
Final pilots required must satisfy BOTH:

1. Pilot Pair Requirement  
2. Duty Hour Requirement
""")

pilots_needed = max(pilot_pair_requirement, pilot_hour_requirement)

pilots_needed = pilots_needed * (1 + reserve_buffer)

cabin_needed = cabin_requirement * (1 + reserve_buffer)
ground_needed = ground_requirement * (1 + reserve_buffer)

crew_table = pd.DataFrame({
"Role":["Pilots","Cabin Crew","Ground Staff"],
"Required":[int(pilots_needed),int(cabin_needed),int(ground_needed)]
})

st.table(crew_table)

# =====================================================
# SECTION 8 — EXISTING CREW UTILIZATION
# =====================================================

st.header("7️⃣ Existing Crew Utilization")

st.write("Formula Used:")

st.code("""
Pilot Utilization =
Total Flight Hours /
(Existing Pilots × Max Pilot Hours)
""")

pilot_utilization = total_flight_hours / (existing_pilots * pilot_max_hours)

st.write(f"Pilot Utilization: {round(pilot_utilization*100,2)}%")

if pilot_utilization > 0.9:
    st.error("High Delay Risk")
elif pilot_utilization > 0.8:
    st.warning("Moderate Risk")
else:
    st.success("Operations Stable")

# =====================================================
# SECTION 9 — AIRCRAFT PER PILOT
# =====================================================

st.header("8️⃣ Aircraft per Pilot Ratio")

aircraft_per_pilot = aircraft / existing_pilots

st.write(f"Aircraft per Pilot: {round(aircraft_per_pilot,3)}")

# =====================================================
# SECTION 10 — HIRING PLAN
# =====================================================

st.header("9️⃣ Hiring Requirement")

pilot_shortage = pilots_needed - existing_pilots

if pilot_shortage > 0:
    st.write(f"Pilots to Hire: {int(pilot_shortage)}")
    st.write(f"Pilot Training Duration: {pilot_training} months")
else:
    st.write("Current pilot workforce sufficient")

# =====================================================
# SECTION 11 — CREW ROSTERING
# =====================================================

st.header("🔟 Simple Crew Rostering")

st.write("""
Crew divided into 3 operational shifts:

• Morning  
• Afternoon  
• Night
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

# =====================================================
# SECTION 12 — CONSULTANT INSIGHT
# =====================================================

st.header("Consultant Insight")

st.write("""
Recommended operating conditions:

• Maintain pilot utilization between **70%–85%**

• Maintain **10–15% reserve crew buffer**

• Start pilot training **4–6 months before demand increase**

• Avoid utilization above **90%** to reduce delay risk
""")
