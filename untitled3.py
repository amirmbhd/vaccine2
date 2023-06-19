import streamlit as st
import pandas as pd

def read_vaccine_info(years):
    if years < 19:
        return pd.read_excel("vaccines3.xlsx")
    else:
        return pd.read_excel("adultvaccines3.xlsx")

def color_rows(row):
    if row['Status'] == 'Completed':
        color = 'green'
    elif row['Status'] == 'In Progress':
        color = 'orange'
    else: # Status is 'Pending'
        color = 'red'
    return ['color: %s' % color]*len(row.values)

months_options = list(range(13))  # 0 to 12
years_options = list(range(1000))  # 0 to 999

st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)
age = (age_month * 30) + (age_year * 365)

if age > 0:
    vaccine_df = read_vaccine_info(age_year)

    # Create the dictionary 'vaccines'
    vaccines = {}
    for _, row in vaccine_df.iterrows():
        vaccines[row['Vaccine']] = {
            '# of Doses': row['# of doses'],
            'timeline': {f'Dose {i+1}': row[f'Dose {i+1}'] for i in range(row['# of doses'])},
            'age_range': (row['Minimum Age'], row['Maximum Age']),
        }

    eligible_vaccines = {k: v for k, v in vaccines.items() if v['age_range'][0]*365 <= age <= v['age_range'][1]*365}
    vaccine_selection = st.sidebar.multiselect("Select the vaccines you have already taken:", options=list(eligible_vaccines.keys()))

    if vaccine_selection:
        st.sidebar.markdown("**Check vaccine series completion:**", unsafe_allow_html=True)
        for vaccine in vaccine_selection:
            if vaccine == "Influenza":
                flu_shot = st.sidebar.radio("Have you completed your annual influenza vaccine this year?", ["No", "Yes"])
                if flu_shot == "Yes":
                    st.sidebar.write("You have completed your series for Influenza.")
                else:
                    st.sidebar.write("You need to take one dose of Influenza vaccine to complete the series.")
            elif vaccine == "Tdap":
                tdap_shot = st.sidebar.radio("Have you received the Tdap vaccine in the past 10 years?", ["No", "Yes"])
                if tdap_shot == "Yes":
                    st.sidebar.write("You have completed your series for Tdap.")
                else:
                    st.sidebar.write("You need to take one dose of Tdap vaccine to complete the series for the next 10 years.")
            else:
                show_completion = st.sidebar.radio(f"Do you want to check if you have completed the series for {vaccine}?", ["No", "Yes"])
                if show_completion == "Yes":
                    doses_taken = st.sidebar.number_input(f"How many doses of {vaccine} have you taken?", min_value=1, value=1)
                    if doses_taken > 0:
                        doses_needed = vaccines[vaccine]['# of Doses'] - doses_taken
                        if doses_needed > 0:
                            st.sidebar.write(f"You need to take {doses_needed} more dose(s) of {vaccine} to complete the series.")
                        else:
                            st.sidebar.write("You have completed your series for this vaccine.")

    st.header("The timeline for your remaining vaccines:")
    eligible_vaccines_df = pd.DataFrame(eligible_vaccines).transpose()
    eligible_vaccines_df.drop(['timeline', 'age_range'], axis=1, inplace=True)
    eligible_vaccines_df['Status'] = eligible_vaccines_df.apply(lambda row: 'Completed' if row.name in vaccine_selection else 'Pending', axis=1)
    st.dataframe(eligible_vaccines_df.style.apply(color_rows, axis=1))
