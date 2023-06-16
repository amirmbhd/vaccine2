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

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)

# Calculate the age in days
age = (age_month * 30) + (age_year * 365)

def color_rows(row):
    if row['Status'] == 'Completed':
        color = 'green'
    elif row['Status'] == 'Pending':
        color = 'red'
    else:  # for 'In Progress' status
        color = 'orange'
    return ['color: %s' % color]*len(row.values)

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # Special condition for similar vaccines
    if (
        "Pneumococcal conjugate (PCV13, PCV15, PPSV23)" in eligible_vaccines
        and "Pneumococcal conjugate (PCV13, PCV15)" in eligible_vaccines
    ):
        eligible_vaccines.pop("Pneumococcal conjugate (PCV13, PCV15)")

    # Sidebar for already taken vaccines
    st.sidebar.markdown(
        "**<span style='color:black'>Please select the vaccines you have already taken (You can select multiple):</span>**",
        unsafe_allow_html=True,
    )
    vaccine_selection = st.sidebar.multiselect(
        "", list(eligible_vaccines.keys()) + ["None"]
    )

    # Define the data for the table
    data = []
    for vaccine_key, vaccine_value in eligible_vaccines.items():
        status = "Completed" if vaccine_key in vaccine_selection else "Pending"
        data.append([vaccine_key, vaccine_value["doses"], status])
    
    # Create the DataFrame
    df = pd.DataFrame(data, columns=["Vaccine Name", "Total Doses", "Status"])
    df = df.sort_values(by="Status", ascending=False)
    df = df.reset_index(drop=True)

    # Check completion
    st.sidebar.markdown("**Check vaccine series completion:**")
    vaccine_key = st.sidebar.selectbox("Select a vaccine:", df['Vaccine Name'].tolist())
    show_completion = st.sidebar.radio("Would you like to check if you have completed the series for this vaccine?", ("Yes", "No"))
    
    if show_completion == "Yes":
        doses_taken = st.sidebar.number_input(
            f"How many doses of {vaccine_key} have you taken?",
            min_value=1,
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
    
    # Display the table
    st.subheader("Vaccine Eligibility")
    st.table(df.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))

    # Show the remaining vaccines timeline
    if vaccine_selection != ["None"]:
        st.subheader("The timeline for remaining vaccines:")
        for selected_vaccine in vaccine_selection:
            if selected_vaccine in vaccines.keys():
                timeline = vaccines[selected_vaccine]["timeline"]
                timeline_df = pd.DataFrame(timeline.items(), columns=["Dose", "Time"])
                timeline_df.set_index('Dose', inplace=True)
                st.table(timeline_df)

else:
    st.write("Please enter a valid age to see the vaccine recommendations.")
