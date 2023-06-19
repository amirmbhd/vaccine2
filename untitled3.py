import streamlit as st
import pandas as pd

def color_rows(row):
    if row['Status'] == 'Completed':
        color = 'green'
    elif row['Status'] == 'In Progress':
        color = 'orange'
    else: # Status is 'Pending'
        color = 'red'
    return ['color: %s' % color]*len(row.values)

# Read the vaccine information from the Excel file
def read_vaccine_info(age_year):
    if age_year >= 19:
        vaccine_df = pd.read_excel("adultvaccines3.xlsx")
    else:
        vaccine_df = pd.read_excel("vaccines3.xlsx")
    return vaccine_df

# Define the months and years options
months_options = list(range(13))  # 0 to 12
years_options = list(range(1000))  # 0 to 999

st.title("Vaccine Recommendation Program")

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_year = st.sidebar.number_input("Years:", min_value=0, max_value=999, value=0, step=1)
age_month = st.sidebar.selectbox("Months:", months_options)

# Calculate the age in days
age = (age_month * 30) + (age_year * 365)

if age > 0:
    vaccine_df = read_vaccine_info(age_year)

    # Convert the DataFrame to a dictionary
    vaccines = {}
    for _, row in vaccine_df.iterrows():
        # ... the rest of the code is the same as before ...

    st.sidebar.markdown("**Check vaccine series completion:**", unsafe_allow_html=True)
    for vaccine in vaccine_selection:
        vaccine_key = vaccine.strip()

        if vaccine_key == 'Influenza' and age_year >= 19:
            influenza_done = st.sidebar.radio(
                f"Have you completed your annual influenza vaccine this year?",
                ["No", "Yes"],
                index=0,
            )
            if influenza_done == 'Yes':
                st.sidebar.write(f"You have completed the required doses for {vaccine_key}.")
                df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'Completed'
            else:
                st.sidebar.write(f"You need 1 more dose of {vaccine_key}.")
                df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'In Progress'
        elif vaccine_key == 'Tdap' and age_year >= 19:
            tdap_done = st.sidebar.radio(
                f"Have you received the Tdap vaccine in the past 10 years?",
                ["No", "Yes"],
                index=0,
            )
            if tdap_done == 'Yes':
                st.sidebar.write(f"You have completed the required doses for {vaccine_key}.")
                df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'Completed'
            else:
                st.sidebar.write(f"You need 1 more dose of {vaccine_key} to complete the series for the next 10 years.")
                df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'In Progress'
        else:
            show_completion = st.sidebar.radio(
                f"Do you want to check if you have completed the series for {vaccine_key}?",
                ["No", "Yes"],
                index=0,
            )
            if show_completion == "Yes":
                # ... the rest of the code is the same as before ...

