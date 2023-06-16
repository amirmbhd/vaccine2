import streamlit as st
import pandas as pd

def color_rows(row):
    if row['Status'] == 'Completed':
        color = 'green'
    elif row['Status'] == 'Pending':
        color = 'red'
    else:  # for 'In Progress' status
        color = 'orange'
    return ['color: %s' % color]*len(row.values)

vaccine_df = pd.read_excel("vaccines3.xlsx")

vaccines = {}
for _, row in vaccine_df.iterrows():
    vaccine = row["Vaccine"]
    doses = row["# of doses"]
    age_range = range(row["Minimum Age"], row["Maximum Age"] + 1)
    doses_info = {}
    timeline = {}
    for i in range(1, 6):  
        if row[f"Dose {i}"] != 'X':  
            dose_min = row[f"Dose {i} Min"]
            dose_max = row[f"Dose {i} Max"]
            doses_info[f"Dose {i}"] = {"min": dose_min, "max": dose_max}
            timeline[f"Dose {i}"] = row[f"Dose {i}"]
    vaccines[vaccine] = {"ages": age_range, "doses": doses, "doses_info": doses_info, "timeline": timeline}

months_options = list(range(13))  
years_options = list(range(19))  

st.title("Vaccine Recommendation Program")

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)

age = (age_month * 30) + (age_year * 365)

if age > 0:
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}
    if (
        "Pneumococcal conjugate (PCV13, PCV15, PPSV23)" in eligible_vaccines
        and "Pneumococcal conjugate (PCV13, PCV15)" in eligible_vaccines
    ):
        eligible_vaccines.pop("Pneumococcal conjugate (PCV13, PCV15)")

    interchangeable_vaccines = [
        "Meningococcal ACWY-D",
        "Meningococcal ACWY-CRM",
        "Meningococcal ACWY-TT",
        "Meningococcal B",
    ]
    interchangeable_vaccines_eligible = [
        vaccine for vaccine in interchangeable_vaccines if vaccine in eligible_vaccines
    ]
    meningococcal_note = False
    if len(interchangeable_vaccines_eligible) > 1:
        for vaccine in interchangeable_vaccines_eligible:
            eligible_vaccines.pop(vaccine)
        closest_vaccine = min(
            interchangeable_vaccines_eligible,
            key=lambda vaccine: abs(min(vaccines[vaccine]["ages"]) - age),
        )
        eligible_vaccines[f"Meningococcal: {closest_vaccine}"] = vaccines[closest_vaccine]
        meningococcal_note = True
    data = []
    for vaccine_key, vaccine_value in eligible_vaccines.items():
        data.append([vaccine_key, vaccine_value['doses'], 'Pending'])
    
    df = pd.DataFrame(data, columns=["Vaccine Name", "Total Doses", "Status"])
    df = df.sort_values(by="Status", ascending=False)
    df = df.reset_index(drop=True)
    
    st.header("Your Vaccine Eligibility")
    st.markdown("Based on the information provided, here are the vaccines that you are eligible for, along with the number of doses needed to complete the series. The vaccines are grouped based on whether you have completed the series, have the series in progress, or haven't started the series.")
    st.table(df.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))

    show_completion = st.sidebar.selectbox(
        "Would you like to check if you have completed a vaccine series?",
        ["No", "Yes"],
    )
    if show_completion == "Yes":
        vaccine_key = st.sidebar.selectbox("Select a vaccine:", list(eligible_vaccines.keys()))
        doses_taken = st.sidebar.number_input(
            f"How many doses of {vaccine_key} have you taken?",
            min_value=0,
            value=1,
        )
        if doses_taken > 0:
            doses_needed = vaccines[vaccine_key]["doses"] - doses_taken
            if doses_needed > 0:
                st.sidebar.write(f"You need {doses_needed} more doses of {vaccine_key}.")
                df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'In Progress'
            else:
                st.sidebar.write(f"You have completed the required doses for {vaccine_key}.")
        else:
            df.loc[df['Vaccine Name'] == vaccine_key, 'Status'] = 'Pending'

        st.table(df.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))
        vaccine_timeline = vaccines[vaccine_key]["timeline"]
        st.sidebar.markdown("### The timeline for remaining vaccines:")
        st.sidebar.table(pd.DataFrame.from_dict(vaccine_timeline, orient='index', columns=['Timeline']))
else:
    st.write("Please enter a valid age.")
