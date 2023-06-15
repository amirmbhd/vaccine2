def check_series_completion(vaccine_key, doses_taken):
    doses_needed = eligible_vaccines[vaccine_key]["doses"] - doses_taken
    if doses_needed > 0:
        return False
    else:
        return True

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
