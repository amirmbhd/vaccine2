import streamlit as st
import pandas as pd

# Read the vaccine information from the Excel file
vaccine_df = pd.read_excel("vaccines3.xlsx")

# Convert the DataFrame to a dictionary
vaccines = {}
for _, row in vaccine_df.iterrows():
    vaccine = row["Vaccine"]
    doses = row["# of doses"]
    age_range = range(row["Minimum Age"], row["Maximum Age"] + 1)
    doses_info = {}
    timeline = {}
    for i in range(1, 6):  # Adjusted to include Dose 1 to Dose 5
        if row[f"Dose {i}"] != 'X':  # If the cell is not 'X'
            dose_min = row[f"Dose {i} Min"]
            dose_max = row[f"Dose {i} Max"]
            doses_info[f"Dose {i}"] = {"min": dose_min, "max": dose_max}
            timeline[f"Dose {i}"] = row[f"Dose {i}"]
    vaccines[vaccine] = {"ages": age_range, "doses": doses, "doses_info": doses_info, "timeline": timeline}

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
        vaccine_selection = st.multiselect("Select the vaccines you have already taken:", ["None"] + list(eligible_vaccines.keys()))

        # If user selected at least one option
        if vaccine_selection:
            # Show timeline for eligible vaccines not taken yet
            if "None" in vaccine_selection:
                vaccine_selection = []
            st.write("Here is the timeline for the vaccines:")
            for vaccine, info in eligible_vaccines.items():
                if vaccine not in vaccine_selection:
                    st.markdown(f"**{vaccine}**")
                    for dose, time in info["timeline"].items():
                        st.write(f"{dose}: {time}")
    
            # Ask if user wants to check if they have completed the series for taken vaccines
            default_value = "No"
            show_completion_key = "show_completion"
            if show_completion_key not in st.session_state:
                st.session_state[show_completion_key] = default_value
            show_completion = st.radio("Would you like to know if you have completed the series for the vaccines already taken?", ["Yes", "No"], key=show_completion_key)
            if show_completion == "Yes":
                for vaccine in vaccine_selection:
                    if vaccine != "None":
                        doses_taken = st.number_input(f"How many doses of {vaccine} have you taken?", min_value=0, value=0)
                        if doses_taken > 0:
                            doses_needed = eligible_vaccines[vaccine]["doses"] - doses_taken
                            if doses_needed > 0:
                                st.write(f"You need {doses_needed} more doses of {vaccine}.")
                            else:
                                st.write(f"You have completed the required doses for {vaccine}.")
