import streamlit as st
import pandas as pd

# Read the vaccine information from the Excel file
vaccine_df = pd.read_excel("vaccinedic1.xlsx")

# Convert the DataFrame to a dictionary
vaccines = {}
for _, row in vaccine_df.iterrows():
    vaccine = row["Vaccine"]
    doses = row["# of doses"]
    age_range = range(row["Minimum Age"], row["Maximum Age"] + 1)
    doses_info = {}
    for i in range(1, doses + 1):
        dose_min = row[f"Dose {i} Min"]
        dose_max = row[f"Dose {i} Max"]
        doses_info[f"Dose {i}"] = {"min": dose_min, "max": dose_max}
    vaccines[vaccine] = {"ages": age_range, "doses": doses, "doses_info": doses_info}

# Define the months and years options
months_options = list(range(13))  # 0 to 12
years_options = list(range(19))  # 0 to 18

# Welcome message and program description
st.title("Vaccine Recommendation Program")
st.write("Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses.")

# Ask the user for their age
age_month = st.selectbox("Select your age (months):", months_options)
age_year = st.selectbox("Select your age (years):", years_options)

# Calculate the age in months
age = age_month + age_year * 12

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # If the user is not eligible for any vaccines, print a message and exit
    if not eligible_vaccines:
        st.write("You are not currently eligible for any vaccines.")
    else:
        # Otherwise, print the eligible vaccines
        st.write("You are eligible for the following vaccines:")
        for vaccine, info in eligible_vaccines.items():
            st.write(f"{vaccine}: {info['doses']} doses")

        # Ask the user which vaccines they have already taken
        vaccine_selection = st.multiselect("Select the vaccines you have already taken:", list(eligible_vaccines.keys()))

        # For each vaccine the user has taken, check if they need any more doses
        for vaccine in vaccine_selection:
            vaccine_key = vaccine.strip()
            show_completion = st.checkbox(f"Do you want to check if you have completed the series for {vaccine_key}?")
            if show_completion:
                doses_taken = st.number_input(f"How many doses of {vaccine_key} have you taken?", min_value=0, value=0)
                if doses_taken > 0:
                    doses_needed = eligible_vaccines[vaccine_key]["doses"] - doses_taken
                    if doses_needed > 0:
                        st.write(f"You need {doses_needed} more doses of {vaccine_key}.")
                    else:
                        st.write(f"You have completed the required doses for {vaccine_key}.")
