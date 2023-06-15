# Define the `vaccine_selection` variable
vaccine_selection = st.sidebar.multiselect("", list(eligible_vaccines.keys()) + ["None"])

# Check if the user has completed the required number of doses for each vaccine
for vaccine in vaccine_selection:
    vaccine_key = vaccine.strip()
    show_completion = st.radio(f"Do you want to check if you have completed the series for {vaccine_key}?", ["No", "Yes"], index=0)
    if show_completion == "Yes":
        doses_taken = st.number_input(f"How many doses of {vaccine_key} have you taken?", min_value=0, value=0)
        if doses_taken > 0:
            if check_series_completion(vaccine_key, doses_taken):
                st.write(f"You have completed the required doses for {vaccine_key}.")
            else:
                st.write(f"You need {doses_needed} more doses of {vaccine_key}.")
