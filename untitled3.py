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

st.title("Vaccine Recommendation Program")

st.markdown("Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses.")

st.sidebar.markdown("**Please enter your age:**", unsafe_allow_html=True)
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)

# Calculate the age in days
age = (age_month * 30) + (age_year * 365)

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # Special condition for similar vaccines
    if "Pneumococcal conjugate (PCV13, PCV15, PPSV23)" in eligible_vaccines and "Pneumococcal conjugate (PCV13, PCV15)" in eligible_vaccines:
        eligible_vaccines.pop("Pneumococcal conjugate (PCV13, PCV15)")

    # If the user is not eligible for any vaccines, print a message and exit
    if not eligible_vaccines:
        st.write("You are not currently eligible for any vaccines.")
    else:
        st.markdown("**You are eligible for the following vaccines:**", unsafe_allow_html=True)
        for vaccine, info in eligible_vaccines.items():
            st.write(f"{vaccine}: {info['doses']} doses")

        st.markdown("**<span style='color:#000080'>Select the vaccines you have already taken:</span>**", unsafe_allow_html=True)
        st.markdown("<i>(You can select more than one. This will display the timeline of the vaccines you need to take and allow you to check if you have completed the series for the vaccines already taken.)</i>", unsafe_allow_html=True)
        vaccine_selection = st.multiselect("", ["None"] + list(eligible_vaccines.keys()))

        # Vaccines user hasn't taken yet
        vaccines_not_taken = [vaccine for vaccine in eligible_vaccines.keys() if vaccine not in vaccine_selection]

        if vaccine_selection and "None" not in vaccine_selection and vaccines_not_taken:
            st.markdown("**<span style='color:#708090'>The timeline for your vaccines:</span>**", unsafe_allow_html=True)
            for vaccine in vaccines_not_taken:
                st.markdown(f"**<span style='color:#708090'>{vaccine}:</span>**", unsafe_allow_html=True)
                for dose, time in eligible_vaccines[vaccine]["timeline"].items():
                    st.write(f"{dose}: {time}")

            st.markdown("**<span style='color:#000080'>Would you like to know if you have completed the series for the vaccines already taken?</span>**", unsafe_allow_html=True)
            show_completion = st.radio("", ["Yes", "No"], index=1)
            if show_completion == "Yes":
                for vaccine in vaccine_selection:
                    if vaccine != "None":
                        st.markdown(f"**<span style='color:#708090'>How many doses of {vaccine} have you taken?</span>**", unsafe_allow_html=True)
                        doses_taken = st.number_input("", min_value=0, value=0, key=f"{vaccine}_doses_taken")
                        if doses_taken > 0:
                            doses_needed = eligible_vaccines[vaccine]["doses"] - doses_taken
                            if doses_needed > 0:
                                st.write(f"You need {doses_needed} more doses of {vaccine}.")
                            else:
                                st.write(f"You have completed the required doses for {vaccine}.")
