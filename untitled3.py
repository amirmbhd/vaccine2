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


# Define the months and years options
months_options = list(range(13))  # 0 to 12
years_options = list(range(120))  # 0 to 18

st.title("Vaccine Recommendation Program")

st.markdown(
    "Welcome to the Vaccine Recommendation Program! This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. **Enter the information in the sidebar to get started.**"
)

st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.selectbox("Years:", years_options)

# Calculate the age in days
age = (age_month * 30) + (age_year * 365)

if age_year < 18:
    sheet = "peds"
else:
    sheet = "adults"

# Read the vaccine information from the Excel file
vaccine_df = pd.read_excel("vaccinesfull.xlsx", sheet_name=sheet)


# Convert the DataFrame to a dictionary
vaccines = {}
for _, row in vaccine_df.iterrows():
    vaccine = row["Vaccine"]
    doses = row["# of doses"]
    age_range = range(row["Minimum Age"], row["Maximum Age"] + 1)
    doses_info = {}
    timeline = {}
    condition_1 = row.get("condition 1", "")  # Added condition 1
    condition_2 = row.get("condition 2", "")  # Added condition 2
    for i in range(1, 6):  # Adjusted to include Dose 1 to Dose 5
        if row[f"Dose {i}"] != 'X':  # If the cell is not 'X'
            dose_min = row[f"Dose {i} Min"]
            dose_max = row[f"Dose {i} Max"]
            doses_info[f"Dose {i}"] = {"min": dose_min, "max": dose_max}
            timeline[f"Dose {i}"] = row[f"Dose {i}"]
    vaccines[vaccine] = {"ages": age_range, "doses": doses, "doses_info": doses_info, "timeline": timeline, "condition 1": condition_1, "condition 2": condition_2} # Added condition 1 and condition 2 to the dictionary

# Initialize vaccine_selection as an empty list
vaccine_selection = []

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # (Remaining part of the code...)

    # Sidebar for already taken vaccines
    st.sidebar.markdown(
        "**<span style='color:black'>Please select the vaccines you have already taken (You can select multiple):</span>**",
        unsafe_allow_html=True,
    )
    vaccine_selection = st.sidebar.multiselect(
        "", list(eligible_vaccines.keys()) + ["None"]
    )

    # (Remaining part of the code...)

vaccines_not_taken = [
    vaccine for vaccine in eligible_vaccines.keys() if vaccine not in vaccine_selection or df[df['Vaccine Name'] == vaccine]['Status'].values[0] == 'In Progress'
]

# (Remaining part of the code...)


    st.table(df.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))

    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    if len(vaccines_not_taken) > 0:
        st.markdown(
            "**<span style='color:#708090'>The timeline for your remaining vaccines:</span>**",
            unsafe_allow_html=True,
        )
        for vaccine in vaccines_not_taken:
            st.markdown(
                f"**<span style='color:#708090'>{vaccine}:</span>**", unsafe_allow_html=True
            )
            timeline_data = []
            for dose, time in eligible_vaccines[vaccine]["timeline"].items():
                timeline_data.append([dose, time])
            timeline_df = pd.DataFrame(timeline_data, columns=["Dose", "Time"])
            st.table(timeline_df)

            # Print conditions if they exist and the status is not 'Completed'
            vaccine_dict = vaccines[vaccine]
            if vaccine_dict["condition 1"]:
                st.write("Condition 1: " + vaccine_dict["condition 1"])
            if vaccine_dict["condition 2"]:
                st.write("Condition 2: " + vaccine_dict["condition 2"])
