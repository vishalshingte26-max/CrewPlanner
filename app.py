import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.optimize import linprog

st.title("CrewPlanner")
st.caption("Airline Operations Crew Planning Tool")

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------

st.sidebar.header("Operational Inputs")

aircraft = st.sidebar.number_input("Number of Aircraft",1,1000,430)
flights_per_aircraft = st.sidebar.slider("Flights per Aircraft per Day",1,10,6)
avg_flight_hours = st.sidebar.slider("Average Flight Hours",1.0,5.0,2.0)

seats = st.sidebar.number_input("Seats per Aircraft",50,300,180)
load_factor = st.sidebar.slider("Load Factor",0.5,1.0,0.85)

pilot_max_hours = st.sidebar.slider("Pilot Max Hours (DGCA)",6,12,8)
reserve_buffer = st.sidebar.slider("Reserve Crew Buffer %",0.05,0.25,0.15)

pilot_training = st.sidebar.slider("Pilot Training Months",1,12,5)
cabin_training = st.sidebar.slider("Cabin Crew Training Months",1,6,2)

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
ax.set_xlabel("Month")
ax.set_ylabel("Passengers")
ax.legend()
st.pyplot(fig)

# -----------------------------
# FLIGHT CAPACITY
# -----------------------------

st.header("2️⃣ Flights Required")

flights_required = forecast / (seats * load_factor)

st.write(f"Flights Required per Month: **{int(flights_required):,}**")

daily_flights = flights_required / 30

# -----------------------------
# CREW REQUIREMENT
# -----------------------------

st.header("3️⃣ Crew Requirement")

total_flight_hours = daily_flights * avg_flight_hours

pilot_shifts = total_flight_hours / pilot_max_hours
pilots_needed = pilot_shifts * (1 + reserve_buffer)

cabin_needed = daily_flights * 4
cabin_needed = cabin_needed * (1 + reserve_buffer)

ground_needed = daily_flights * 8
ground_needed = ground_needed * (1 + reserve_buffer)

crew_df = pd.DataFrame({
    "Role":["Pilots","Cabin Crew","Ground Staff"],
    "Required":[int(pilots_needed),int(cabin_needed),int(ground_needed)]
})

st.table(crew_df)

# -----------------------------
# SOLVER OPTIMIZATION
# -----------------------------

st.header("4️⃣ Crew Optimization (Solver)")

# minimize crew
c = [1,1,1]

A = [
    [-pilot_max_hours,0,0],
    [0,-1,0],
    [0,0,-1]
]

b = [
    -total_flight_hours,
    -cabin_needed,
    -ground_needed
]

result = linprog(c,A_ub=A,b_ub=b,bounds=(0,None))

if result.success:
    st.success("Optimization Successful")
else:
    st.error("Optimization Failed")

# -----------------------------
# TRAINING PIPELINE
# -----------------------------

st.header("5️⃣ Hiring & Training Plan")

pilot_hire = int(pilots_needed/6)
cabin_hire = int(cabin_needed/6)

st.write(f"Pilots to Hire: **{pilot_hire}**")
st.write(f"Cabin Crew to Hire: **{cabin_hire}**")

st.write(f"Pilot Training Duration: **{pilot_training} months**")
st.write(f"Cabin Training Duration: **{cabin_training} months**")

# -----------------------------
# ROSTERING
# -----------------------------

st.header("6️⃣ Crew Rostering")

shifts = 3

pilots_shift = int(pilots_needed / shifts)
cabin_shift = int(cabin_needed / shifts)

roster_df = pd.DataFrame({
    "Shift":["Morning","Afternoon","Night"],
    "Pilots":[pilots_shift]*3,
    "Cabin Crew":[cabin_shift]*3
})

st.table(roster_df)

# -----------------------------
# UTILIZATION RISK
# -----------------------------

st.header("7️⃣ Operational Risk")

available_hours = pilots_needed * pilot_max_hours
utilization = total_flight_hours / available_hours

st.write(f"Crew Utilization: **{round(utilization*100,2)}%**")

if utilization > 0.9:
    st.error("High Delay Risk")
elif utilization > 0.8:
    st.warning("Moderate Risk")
else:
    st.success("Operationally Stable")

# -----------------------------
# CONSULTANT RECOMMENDATION
# -----------------------------

st.header("Consultant Recommendation")

st.write("""
Maintain crew utilization between **70% and 85%**.

Increase reserve buffer if utilization exceeds **90%**.

Plan training at least **4–6 months before demand increase** to avoid crew shortages.
""")
