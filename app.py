import streamlit as st
from auth import authenticator
from auth import MultiPage


# Create an instance of the app 
app = MultiPage()

# Title of the main page
st.title("Multi-page App with Authentication")

# Add all your applications (pages) here
app.add_page("Home", "Home.py")
app.add_page("1_Real_Time_Prediction", ".\pages\1_Real_Time_Prediction.py")
app.add_page("1_Real_Time_Prediction_old", ".\pages\1_Real_Time_Prediction_old.py")
app.add_page("2_Registration_form", ".\pages\2_Registration_form.py")
app.add_page("3A_Reports", "\pages\3A_Reports.py")
app.add_page("3B_Reports", "\pages\3B_Reports.py")
app.add_page("3C_Report_Time", "\pages\3C_Report_Time.py")
app.add_page("Report", "\pages\3_Report.py")
app.add_page("Registerd Members Managment", "\pages\4_Registerd_members_Managment.py")
app.add_page("Mobile Modification", "\pages\Mobile Modification.py")


# 1_Real_Time_Prediction.py
# 1_Real_Time_Prediction_old.py
# 2_Registration_form.py
# 3A_Reports.py
# 3B_Reports.py
# 3C_Report_Time.py
# 3_Report.py
# 4_Registerd_members_Managment.py
# Mobile Modification.py

# The main app
app.run()