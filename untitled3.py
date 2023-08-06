import streamlit as st
import pandas as pd

from PIL import Image



st.image('Banner.jpg')

def color_rows(row):
    if row['Status'] == 'Completed':
        color = 'green'
    elif row['Status'] == 'In Progress':
        color = 'orange'
    elif row['Status'] == 'Under Review':
        color = 'red'
    elif row['Status'] == 'Ineligible':
        color = 'green'
    else: # Status is 'Pending'
        color = 'red'
    return ['color: %s' % color]*len(row.values)
    


# Define the months and years options
months_options = list(range(13))  # 0 to 12
years_options = list(range(120))  # 0 to 119

st.title("Vaccine Recommendation Program")


st.markdown(
    "**Welcome to the Vaccine Recommender Program!** This program will tell you which vaccines you are eligible for based on your age. You can also enter which vaccines you have already taken, and the program will tell you if you need any more doses. You can also review normal vaccine schdeule,eligibility criteria, alternative dosing based on conditions and catch up vaccinations if applicable. **Enter the information in the sidebar to get started.**"
)




st.sidebar.markdown("© Amir Behdani & Sterling Saunders")
st.sidebar.markdown("---")


st.sidebar.markdown("**Please enter your age:**")
age_month = st.sidebar.selectbox("Months:", months_options)
age_year = st.sidebar.number_input("Years:", min_value=0, max_value=120, value=0)





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
    eligibility = row["Eligibility"] if pd.notna(row["Eligibility"]) else ""
    ineligibility = row["Ineligibility"] if pd.notna(row["Ineligibility"]) else ""
    Schedule = row["Schedule"] if pd.notna(row["Schedule"]) else "" 
    doses_info = {}
    timeline = {}
    condition_dosing = {}
    for i in range(1, 6):  # Adjusted to include Dose 1 to Dose 5
        if row[f"Dose {i}"] != 'X':  # If the cell is not 'X'
            dose_min = row[f"Dose {i} Min"]
            dose_max = row[f"Dose {i} Max"]
            doses_info[f"Dose {i}"] = {"min": dose_min, "max": dose_max}
            timeline[f"Dose {i}"] = row[f"Dose {i}"]
    # Added for conditions and alternate dosing
    condition_columns = [f"condition {i+1}" for i in range(14)]
    dosing_columns = [f"Alternate dosing {i+1}" for i in range(14)]
    for condition_column, dosing_column in zip(condition_columns, dosing_columns):
        if pd.notna(row[condition_column]) and pd.notna(row[dosing_column]):
            condition_dosing[row[condition_column]] = row[dosing_column]
    vaccines[vaccine] = {"ages": age_range, "doses": doses, "doses_info": doses_info, "timeline": timeline, "eligibility": eligibility, "ineligibility": ineligibility, "condition_dosing": condition_dosing, "Schedule": Schedule}

df_conditional = pd.DataFrame() 
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


    
    # Prompt for radio buttons before constructing the DataFrame
    eligibility_statuses = {}
    for vaccine, info in eligible_vaccines.items():
        if info.get("Schedule") == "Conditional":
            options = ["Under Review", "Eligible", "Ineligible"]
            eligibility_status = st.sidebar.radio(vaccine, options)
            eligibility_statuses[vaccine] = eligibility_status
    
    data = []
    for vaccine, info in eligible_vaccines.items():
        # Set default status as Pending
        status = "Pending"
        
        # If the vaccine is conditional, get its status from the radio buttons
        if vaccine in eligibility_statuses:
            if eligibility_statuses[vaccine] == "Under Review":
                status = "Under Review"
            elif eligibility_statuses[vaccine] == "Eligible":
                status = "Pending"
            elif eligibility_statuses[vaccine] == "Ineligible":
                status = "Ineligible"
        else:
            if vaccine in vaccine_selection:
                doses_taken = st.sidebar.number_input(
                            f"How many doses of {vaccine} have you taken?",
                            min_value=1,
                            value=1,
                        )
                if doses_taken > 0:
                    doses_needed = vaccines[vaccine]["doses"] - doses_taken  # Use 'vaccines' instead of 'eligible_vaccines'
                    if doses_needed > 0:
                        status = 'In Progress'  # directly update status
                    else:
                        status = 'Completed'  # directly update status
        data.append([vaccine, info["doses"], status, info.get("Schedule")])
    
    # ... Rest of your code ...
    
    
    
    







    

    # Add 'Schedule' to the DataFrame columns
    df = pd.DataFrame(data, columns=["Vaccine Name", "Total Doses", "Status", "Schedule"])
    df = df.sort_values(by="Status", ascending=False)
    df = df.reset_index(drop=True)
    df_conditional = df[df['Schedule'] == 'Conditional']
    df_non_conditional = df.drop(df_conditional.index)


 
    for vaccine, status in eligibility_statuses.items():
        if status == "Under Review":
            df.loc[df['Vaccine Name'] == vaccine, 'status'] = "Under Review"
        elif status == "Eligible":
            df.loc[df['Vaccine Name'] == vaccine, 'status'] = "Pending"
        elif status == "Ineligible":
            df.loc[df['Vaccine Name'] == vaccine, 'status'] = "Ineligible"
   
        # At the end of the sidebar, ask the user to review eligibility criteria 
    st.sidebar.markdown("**Please review eligibility criteria and select your eligibility status for the following vaccines:**")
       
  
    # Always Display the first table regardless of the checkbox state
    st.markdown("**<span style='color:#073863'>The following vaccines are the routine vaccines you are eligible for: </span>**", unsafe_allow_html=True)
    st.table(df_non_conditional.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))


    # Display the second table (conditional schedule) if it's not empty
    if not df_conditional.empty:
        st.markdown("**<span style='color:#073863'>The following vaccines have a 'Conditional' Schedule (Please check Eligibility and Ineligibility Criteria to determine your eligibility): </span>**", unsafe_allow_html=True)
        st.table(df_conditional.style.apply(color_rows, axis=1).set_properties(**{'text-align': 'center'}))
        

    # ... code remains same ...
    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    
    # Fetch vaccines that are not taken or are in progress
    # ...
  
                    


    
    # Define the checkboxes in the sidebar
    normal_schedule_check = st.sidebar.checkbox("Normal Vaccine schedule")
    eligibility_criteria_check = st.sidebar.checkbox("Eligibility and Ineligibility Criteria")
    
    # Set the checkbox label based on the age
    if age_year < 19:
        checkbox_label = "Catch Up Dosing"
    else:
        checkbox_label = "Conditions and Alternate Dosing"
    
    conditions_dosing_check = st.sidebar.checkbox(checkbox_label)
    

    # Fetch vaccines that are not taken or are in progress
    vaccines_not_taken = [
        vaccine for vaccine in eligible_vaccines.keys() if vaccine not in vaccine_selection or df[df['Vaccine Name'] == vaccine]['Status'].values[0] == 'In Progress'
    ]
    
    if len(vaccines_not_taken) > 0:
        if normal_schedule_check:
            st.markdown(
                "<span style='color:#254912'> ",
                unsafe_allow_html=True,
            )
        for vaccine in vaccines_not_taken:
            st.markdown(
                f"**<span style='color:black'>{vaccine}:</span>**", unsafe_allow_html=True
            )
            # Display the eligibility and ineligibility info if the corresponding checkbox is checked and data exists
            if eligibility_criteria_check:
                if eligible_vaccines[vaccine]['eligibility']:
                    st.markdown(f"**<span style='color:green'>You are eligible for {vaccine} if meeting any of these conditions/criteria:</span>** {eligible_vaccines[vaccine]['eligibility']}", unsafe_allow_html=True)
                if eligible_vaccines[vaccine]["ineligibility"]:
                    st.markdown(f"**<span style='color:red'>You are not eligible for {vaccine} if meeting any of these conditions/criteria:</span>** {eligible_vaccines[vaccine]['ineligibility']}", unsafe_allow_html=True)
            if normal_schedule_check:
                section_title1 = "Normal schedule for"
                st.markdown(
                    f"**<span style='color:#073863'>{section_title1} for {vaccine}:</span>**",
                    unsafe_allow_html=True
                )
                st.table(pd.DataFrame(eligible_vaccines[vaccine]["timeline"], index=["Timeline"]))
            condition_dosing_data = []
            for condition, dosing in eligible_vaccines[vaccine]["condition_dosing"].items():
                condition_dosing_data.append([condition, dosing])
            # Display the conditions and alternate dosing table if the corresponding checkbox is checked
            if conditions_dosing_check and len(condition_dosing_data) > 0:
                # Set the title based on the age
                if age_year < 19:
                    section_title = "Catch Up Dosing"
                else:
                    section_title = "Conditions and Alternate Dosing"
    
                st.markdown(
                    f"**<span style='color:#18b4c5'>{section_title} for {vaccine}:</span>**",
                    unsafe_allow_html=True
                )
                condition_dosing_df = pd.DataFrame(condition_dosing_data, columns=["Condition", "Alternate Dosing"])
                st.table(condition_dosing_df)
