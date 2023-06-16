import streamlit as st
import pandas as pd

def color_rows(row):
    if row['Status'] == 'Completed':
        return ['color: green']*len(row.values)
    elif row['Status'] == 'In progress':
        return ['color: yellow']*len(row.values)
    else:
        return ['color: red']*len(row.values)

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

    # Define the data for the table
    data = []
    for vaccine, info in eligible_vaccines.items():
        status = "Completed" if vaccine in vaccine_selection else "Pending"
        data.append([vaccine, info["doses"], status])

    # Create the DataFrame
    df = pd.DataFrame(data, columns=["Vaccine Name", "Total Doses", "Status"])
    df = df.sort_values(by="Status", ascending=False)
    df = df.reset_index(drop=True)

    st.checkbox("Use container width for the table", value=False, key="use_container_width_table")
    st.dataframe(df.style.apply(color_rows, axis=1), use_container_width=st.session_state.use_container_width_table)

    check_vaccine_completion = st.sidebar.checkbox("Check vaccine series completion")

    if check_vaccine_completion:
        selected_vaccine = st.sidebar.selectbox("Select a vaccine:", vaccine_selection)
        doses_taken = st.sidebar.slider("Number of doses taken:", 0, vaccines[selected_vaccine]['doses'])

        if doses_taken == 0:
            df.loc[df['Vaccine Name'] == selected_vaccine, 'Status'] = 'Pending'
        elif doses_taken < vaccines[selected_vaccine]['doses']:
            df.loc[df['Vaccine Name'] == selected_vaccine, 'Status'] = 'In progress'
        else:
            df.loc[df['Vaccine Name'] == selected_vaccine, 'Status'] = 'Completed'

        st.dataframe(df.style.apply(color_rows, axis=1), use_container_width=st.session_state.use_container_width_table)
