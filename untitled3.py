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

def read_vaccine_info(age_year):
    if age_year >= 19:
        vaccine_df = pd.read_excel("adultvaccines3.xlsx")
    else:
        vaccine_df = pd.read_excel("vaccines3.xlsx")
    return vaccine_df

months_options = list(range(13))  # 0 to 12
years_options = list(range(1000))  # 0 to 999

st.title("Vaccine Recommendation Program")

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_year = st.sidebar.number_input("Years:", min_value=0, max_value=999, value=0, step=1)
age_month = st.sidebar.selectbox("Months:", months_options)

age = (age_month * 30) + (age_year * 365)

if age > 0:
    vaccine_df = read_vaccine_info(age_year)

    # Convert the DataFrame to a dictionary
    vaccines = {}
    for _, row in vaccine_df.iterrows():
        # ... the rest of the code for reading the vaccines is the same ...

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
                doses_taken = st.sidebar.number_input(
                    f"How many doses of {vaccine_key} have you taken?",
                    min_value=1,
                    value=1,
                )
                if doses_taken > 0:
                    doses_needed = vaccines[vaccine_key]["doses"] - doses_taken  # Use 'vaccines' instead of 'eligible_vaccines'
                    if doses_needed > 0:
                        st.sidebar.write(f"You need {doses_needed} more doses of {vaccine_key}.")
                        df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'In Progress'
                    else:
                        st.sidebar.write(f"You have completed the required doses for {vaccine_key}.")
                else:
                    df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'Pending'
        
    if vaccines_not_taken:
        st.markdown(
            "**<span style='color:#708090'>The timeline for your remaining vaccines:</span>**",
            unsafe_allow_html=True,
        )

    st.table(df.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))
    
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    
    for vaccine in vaccines_not_taken:
        st.markdown(
            f"**<span style='color:#708090'>{vaccine}:</span>**", unsafe_allow_html=True
        )
        timeline_data = []
        for dose, time in eligible_vaccines[vaccine]["timeline"].items():
            timeline_data.append([dose, time])
        timeline_df = pd.DataFrame(timeline_data, columns=["Dose", "Time"])
        st.table(timeline_df)
