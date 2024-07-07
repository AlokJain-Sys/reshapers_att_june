import streamlit as st
import face_rec  # Assuming you have a module named face_rec for face recognition functions
import pandas as pd
import datetime
from datetime import  timedelta,date
import schedule
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Set up page configuration
st.set_page_config(page_title="Shift-Wise Attendance Summary", page_icon="")

st.subheader('Shift-Wise Attendance Summary Report')


# Function to retrieve log data
def load_logs(name, end=-1):
    """Loads attendance logs from Redis."""
    logs_list = face_rec.r.lrange(name, start=0, end=end)
    return [log.decode('utf-8') for log in logs_list]


def main():
    name = 'attendance:logs'

    # Retrieve logs
    logs_list = load_logs(name)

    # Process logs into a DataFrame
    logs_data = []
    for log in logs_list:
        try:
            name, role, timestamp = log.split('@')
            logs_data.append({
                'Name': name.strip(),
                'Role': role.strip(),
                'Timestamp': timestamp.strip()
            })
        except ValueError:
            st.warning(f"Skipping invalid log entry: {log}")

    logs_df = pd.DataFrame(logs_data)

    # Ensure required columns exist
    required_columns = ['Timestamp', 'Name', 'Role']
    for col in required_columns:
        if col not in logs_df.columns:
            st.error(f"Required column '{col}' not found in log data.")
            st.stop()

    # Convert Timestamp to datetime
    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'], format='ISO8601')
    logs_df['Date'] = logs_df['Timestamp'].dt.date

    # Define function to assign shift based on timestamp
    def assign_shift(timestamp):
        hour = timestamp.hour
        if 6 <= hour < 14:
            return "Morning"
        elif 14 <= hour < 22:
            return "Evening"
        else:
            return "Night"

    # Add shift column to DataFrame
    def add_shift_column(logs_df):
        logs_df["Shift"] = logs_df["Timestamp"].apply(assign_shift)
        return logs_df

    logs_df = add_shift_column(logs_df)
        # Filter data for the current date
    today = datetime.date.today()  # Corrected line
    filtered_df = logs_df[logs_df['Date'] == today]
    # Filter data for the current date
    # current_date = datetime.now().date()
    # filtered_df = logs_df[logs_df['Date'] == current_date]

    # Generate daily summary report
    daily_summary = filtered_df.groupby(['Name', 'Role', 'Shift']).agg(
        In_Time=('Timestamp', 'min'),
        Out_Time=('Timestamp', 'max')
    ).reset_index()

    # Calculate duration for daily summary
    daily_summary['Duration'] = daily_summary['Out_Time'] - daily_summary['In_Time']

    # Calculate duration in hours
    daily_summary['Duration_hours'] = daily_summary['Duration'].dt.total_seconds() / 3600

    # Determine presence based on duration_hours
    daily_summary['Present'] = daily_summary['Duration_hours'] >= 0

    # Generate shift-wise summary
    shift_summary = daily_summary.groupby(['Shift', 'Role']).agg(
        Total_Present=('Present', 'sum')
    ).reset_index()

    # Pivot the shift summary for better display
    shift_summary_pivot = shift_summary.pivot(index='Shift', columns='Role', values='Total_Present').fillna(0).astype(int)
    shift_summary_pivot = shift_summary_pivot.reset_index().rename_axis(None, axis=1)

    # Function to convert DataFrame to HTML table
    def dataframe_to_html(df):
        return df.to_html(classes='table table-striped', index=False)

    # Function to send email notification
    def send_email(subject, sender, recipients, html_content):
        # Create message container with proper formatting
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)

        # Create text and HTML parts for email body
        part1 = MIMEText(f"See attached report for details.", 'plain')
        part2 = MIMEText(html_content, 'html')

        # Attach parts to message container
        msg.attach(part1)
        msg.attach(part2)

        # Send email via SMTP server
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, "@#Master789")  # Replace with your email password
                server.sendmail(sender, recipients, msg.as_string())
        except Exception as e:
            print(f"Error: {e}")

    # Get current date for scheduling
    today = datetime.date.today()
    today = today.strftime('%Y-%m-%d')

    # Example DataFrame (replace with actual data retrieval if needed)
    df = pd.DataFrame(shift_summary_pivot)

    # Convert DataFrame to HTML for email attachment
    html_table = dataframe_to_html(df)

    # Email details
    subject = "Shift-Wise Attendance Summary Report"
    sender = "jainallo@gmail.com"  # Replace with your email address
    recipients = ["shapers,gym.bhl@gmail.com"]  # Add email addresses for recipients

    html_content = f"""
    <html>
        <body>
            <h2>Shift-Wise Attendance Summary Report - {today}</h2>
            {html_table}
        </body>
    </html>
    """

    # Send email (uncomment for actual email sending)
    # send_email(subject, sender, recipients, html_content)

    # Schedule email sending for a specific time (replace with your desired time)
    schedule.every().day.at("11:00").do(send_email, today, sender, recipients, html_content)

    # Streamlit app layout and user interface
    st.title("Daily Attendance Summary")

    # Display the shift-wise attendance summary report
    if not shift_summary_pivot.empty:
        st.dataframe(shift_summary_pivot)
    else:
        st.warning("No data found for the current date.")

    # Placeholder for additional app functionalities (optional)

    # Keep the app running and check for pending scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)  # Replace with actual app logic (remove for deployment)

if __name__ == "__main__":
    main()
