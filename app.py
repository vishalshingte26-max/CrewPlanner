import streamlit as st
import pandas as pd
import numpy as np

st.title("CrewPlanner")
st.subheader("Airline Crew Planning Tool")

st.sidebar.header("Inputs")

aircraft = st.sidebar.number_input("Number of Aircraft", 1, 1000, 430)
flights_per_aircraft = st.sidebar.slider("Flights per Aircraft", 1, 10, 6)
flight_hours = st.sidebar.slider("Average Flight Hours", 1.0, 5.0, 2.0)

pilot_max_hours = st.sidebar.slider("Pilot Max Hours (DGCA)", 6, 12, 8)
buffer = st.sidebar.slider("Reserve Buffer %", 0.05, 0.25, 0.15)

total_flights = aircraft * flights_per_aircraft
total_hours = total_flights * flight_hours

pilots_needed = total_hours / pilot_max_hours
pilots_needed = pilots_needed * (1 + buffer)

cabin_needed = total_flights * 4
cabin_needed = cabin_needed * (1 + buffer)

ground_needed = total_flights * 8
ground_needed = ground_needed * (1 + buffer)

st.header("Optimal Crew Required")

data = {
    "Role": ["Pilots", "Cabin Crew", "Ground Staff"],
    "Required": [int(pilots_needed), int(cabin_needed), int(ground_needed)]
}

df = pd.DataFrame(data)

st.table(df)