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

if age > 0:
    # Determine which vaccines the user is eligible for
    eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

    # Special condition for similar vaccines
    if (
        "Pneumococcal conjugate (PCV13, PCV15, PPSV23)" in eligible_vaccines
        and "Pneumococcal conjugate (PCV13, PCV15)" in eligible_vaccines
    ):
        eligible_vaccines.pop("Pneumococcal conjugate (PCV13, PCV15)")

    # Special condition for interchangeable vaccines
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
        # Replace all the interchangeable vaccines with "Meningococcal"
        for vaccine in interchangeable_vaccines_eligible:
            eligible_vaccines.pop(vaccine)
        closest_vaccine = min(
            interchangeable_vaccines_eligible,
            key=lambda vaccine: abs(min(vaccines[vaccine]["ages"]) - age),
        )
        eligible_vaccines[f"Meningococcal: {closest_vaccine}"] = vaccines[closest_vaccine]
        meningococcal_note = True

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
    for vaccine, info in eligible_vaccines.items():
        status = "Completed" if vaccine in vaccine_selection else "Pending"
        data.append([vaccine, info["doses"], status])

    # Create the DataFrame
    df = pd.DataFrame(data, columns=["Vaccine Name", "Total Doses", "Status"])
    df = df.sort_values(by="Status", ascending=False)

    # Display the table
    df_styled = df.style.hide().set_properties(**{"text-align": "center"}).apply(color_rows, axis=1).\
                set_table_styles([{'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]}])
    st.table(df_styled)

    # The timeline for your remaining vaccines:
    st.markdown(
        "**<span style='color:#708090'>The timeline for your remaining vaccines:</span>**",
        unsafe_allow_html=True,
    )
    vaccines_not_taken = [
        vaccine for vaccine in eligible_vaccines.keys() if vaccine not in vaccine_selection
    ]
    for vaccine in vaccines_not_taken:
        vaccine_timeline = eligible_vaccines[vaccine]["timeline"]
        vaccine_timeline_df = pd.DataFrame(vaccine_timeline.items(), columns=["Dose", "Timeline"])
        st.table(vaccine_timeline_df.style.hide_index().set_properties(**{"text-align": "center"}).\
                 set_table_styles([{'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]}]))

        if vaccine.startswith("Meningococcal:") and meningococcal_note:
            st.markdown(
                "<span style='color:#708090'>(Note: You are eligible for multiple types of Meningococcal vaccines. The timeline displayed is specific to the type closest to your age, but you may be eligible for others with different schedules.)</span>",
                unsafe_allow_html=True,
            )

    # Check vaccine series completion
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
else:
    st.write(" ")
