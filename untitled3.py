#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 18:54:19 2023

@author: amirbhd
"""

import streamlit as st

# Define the vaccines and their information
vaccines = {
    "Hib": {"ages": range(2, 16), "doses": 3, "name": "Haemophilus influenzae type b"},
    "HepA": {"ages": range(12, 24), "doses": 2, "name": "Hepatitis A"},
    "HPV": {"ages": range(9, 19), "doses": 2, "name": "Human papillomavirus"},
    "Influenza": {"ages": range(6, 200), "doses": 1, "name": "Influenza"}
}

# Ask the user for their age
age = st.number_input("Please enter your age in months:", min_value=0, value=0)

# Determine which vaccines the user is eligible for
eligible_vaccines = {k: v for k, v in vaccines.items() if age in v["ages"]}

# If the user is not eligible for any vaccines, print a message and exit
if not eligible_vaccines:
    st.write("You are not currently eligible for any vaccines.")
else:
    # Otherwise, print the eligible vaccines
    st.write("You are eligible for the following vaccines:")
    vaccine_options = [f"{k}: {v['name']}" for k, v in eligible_vaccines.items()]
    taken_vaccines = st.multiselect("Please select the vaccines you have already taken:", vaccine_options)

    # For each vaccine the user has taken, check if they need any more doses
    for vaccine in taken_vaccines:
        vaccine_key = vaccine.split(":")[0]
        doses_taken = st.number_input(f"How many doses of {vaccine_key} have you taken?", min_value=0, value=0)
        if doses_taken < eligible_vaccines[vaccine_key]["doses"]:
            st.write(f"You need {eligible_vaccines[vaccine_key]['doses'] - doses_taken} more doses of {vaccine_key}.")
        else:
            st.write(f"You have completed the required doses for {vaccine_key}.")
