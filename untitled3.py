import streamlit as st

# Define the vaccines and their information
vaccines = {
    "Hib": {"ages": range(2, 16), "doses": 3, "name": "Haemophilus influenzae type b"},
    "HepA": {"ages": range(12, 24), "doses": 2, "name": "Hepatitis A"},
    "HPV": {"ages": range(9, 19), "doses": 2, "name": "Human papillomavirus"},
    "Influenza": {"ages": range(6, 200), "doses": 1, "name": "Influenza"}
}

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

# Determine which vaccines the user is eligible for
eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

# If the user is not eligible for any vaccines, print a message and exit
if not eligible_vaccines:
    st.write("You are not currently eligible for any vaccines.")
else:
    # Otherwise, print the eligible vaccines
    st.write("You are eligible for the following vaccines:")
    vaccine_options = [f"{k}: {v['name']}" for k, v in eligible_vaccines.items()]
    for i, option in enumerate(vaccine_options, start=1):
        st.write(f"{i}. {option}")

    # Ask the user which vaccines they have already taken
    vaccine_selection = st.multiselect("Select the vaccines you have already taken:", vaccine_options)

    # For each vaccine the user has taken, check if they need any more doses
    for vaccine in vaccine_selection:
        vaccine_key = vaccine.split(":")[0].strip()
        doses_taken = st.number_input(f"How many doses of {vaccine_key} have you taken?", min_value=0, value=0)
        if doses_taken < eligible_vaccines[vaccine_key]["doses"]:
            st.write(f"You need {eligible_vaccines[vaccine_key]['doses'] - doses_taken} more doses of {vaccine_key}.")
        else:
            st.write(f"You have completed the required doses for {vaccine_key}.")
