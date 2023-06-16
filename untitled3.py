import streamlit as st
import pandas as pd

def color_rows(row):
    color = 'green' if row['Status'] == 'Completed' else 'red'
    return ['color: %s' % color]*len(row.values)

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

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)

# Calculate the age in days
age = (age_month * 30) + (age_year * 365)

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # Sidebar for already taken vaccines
    st.sidebar.markdown(
        "**<span style='color:black'>Please select the vaccines you have already taken (You can select multiple):</span>**",
        unsafe_allow_html=True,
    )
    vaccine_selection = st.sidebar.multiselect(
        "", list(eligible_vaccines.keys()) + ["None"]
    )

    vaccines_not_taken = [
        vaccine for vaccine in eligible_vaccines.keys() if vaccine not in vaccine_selection
    ]

    # Define the data for the table of taken vaccines
    data_taken = []
    for vaccine, info in eligible_vaccines.items():
        if vaccine in vaccine_selection:
            status = "Completed"
            data_taken.append([vaccine, info["doses"], status])

    # Define the data for the table of not taken vaccines
    data_not_taken = []
    for vaccine in vaccines_not_taken:
        timeline_info = ' '.join([f"{dose}: {time}" for dose, time in vaccines[vaccine]['timeline'].items()])
        data_not_taken.append([vaccine, vaccines[vaccine]["doses"], timeline_info])

    # Create the DataFrame for taken vaccines
    df_taken = pd.DataFrame(data_taken, columns=["Vaccine Name", "Total Doses", "Status"])
    df_taken = df_taken.sort_values(by="Status", ascending=False)
    df_taken = df_taken.reset_index(drop=True)
    st.markdown("**Vaccines Status:**")
    st.table(df_taken.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))

    # Create the DataFrame for not taken vaccines
    df_not_taken = pd.DataFrame(data_not_taken, columns=["Vaccine Name", "Total Doses", "Timeline"])
    df_not_taken = df_not_taken.reset_index(drop=True)
    st.markdown("**Timeline for Remaining Vaccines:**")
    st.table(df_not_taken.style.set_properties(**{'text-align': 'center'}))

# Remaining sidebar elements
st.sidebar.markdown("**Check vaccine series completion:**", unsafe_allow_html=True)
for vaccine in vaccine_selection:
    vaccine_key = vaccine.strip()
    show_completion = st.sidebar.radio(
        f"Do you want to check if you have completed the series for {vaccine_key}?",
        ["No", "Yes"],
        index=0,
    )
    if show_completion == "Yes":
        doses_taken = st.sidebar.number_input(
            f"How many doses of {vaccine_key} have you taken?",
            min_value=0,
            value=0,
        )
        if doses_taken > 0:
            doses_needed = vaccines[vaccine_key]["doses"] - doses_taken  # Use 'vaccines' instead of 'eligible_vaccines'
            if doses_needed > 0:
                st.sidebar.write(f"You need {doses_needed} more doses of {vaccine_key}.")
            else:
                st.sidebar.write(f"You have completed the required doses for {vaccine_key}.")
