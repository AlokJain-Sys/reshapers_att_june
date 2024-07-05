from Home import st, face_rec
import pandas as pd
from PIL import Image
from utils import set_page_config
from datetime import datetime

st.subheader('Attendance Report Hourly')

# Retrieve log data
name = 'attendance:logs'
def load_logs(name, end=-1):
    logs_list = face_rec.r.lrange(name, start=0, end=end)
    return logs_list

logs_list = load_logs(name=name)
convert_byte_to_string = lambda x: x.decode('utf-8')
logs_list_string = list(map(convert_byte_to_string, logs_list))

# Create DataFrame from logs
logs_data = []
for log in logs_list_string:
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
logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'],format='ISO8601')
logs_df['Date'] = logs_df['Timestamp'].dt.date

def assign_shift(timestamp):
    hour = timestamp.hour
    if 6 <= hour < 14:
        return "Morning"
    elif 14 <= hour < 22:
        return "Evening"
    else:
        return "Night"

def add_shift_column(logs_df):
    logs_df["Shift"] = logs_df["Timestamp"].apply(assign_shift)
    return logs_df

logs_df = add_shift_column(logs_df)

# Generate reports
daily_report = logs_df.groupby(['Date', 'Name', 'Role']).agg(
    In_Time=('Timestamp', 'min'),
    Out_Time=('Timestamp', 'max')
).reset_index()

hourly_in_report = logs_df.groupby(['Date', 'Shift', 'Name', pd.Grouper(key='Timestamp', freq='H')]).agg(
    In_Time=('Timestamp', 'min')
).reset_index()

hourly_out_report = logs_df.groupby(['Date', 'Shift', 'Name', pd.Grouper(key='Timestamp', freq='H')]).agg(
    Out_Time=('Timestamp', 'max')
).reset_index()

shift_wise_report = logs_df.groupby(['Date', 'Shift', 'Name', 'Role']).agg(
    In_Time=('Timestamp', 'min'),
    Out_Time=('Timestamp', 'max')
).reset_index()

shift_wise_report['Duration'] = shift_wise_report['Out_Time'] - shift_wise_report['In_Time']
shift_wise_report['In_Time'] = shift_wise_report['In_Time'].dt.strftime('%I:%M %p')
shift_wise_report['Out_Time'] = shift_wise_report['Out_Time'].dt.strftime('%I:%M %p')

# Marking attendance
all_dates = logs_df['Date'].unique()
name_role = logs_df[['Name', 'Role']].drop_duplicates().values.tolist()

date_name_role_zip = []
for dt in all_dates:
    for name, role in name_role:
        date_name_role_zip.append([dt, name, role])

date_name_role_zip_df = pd.DataFrame(date_name_role_zip, columns=['Date', 'Name', 'Role'])
date_name_role_zip_df = pd.merge(date_name_role_zip_df, daily_report, how='left', on=['Date', 'Name', 'Role'])

date_name_role_zip_df['Duration'] = date_name_role_zip_df['Out_Time'] - date_name_role_zip_df['In_Time']
date_name_role_zip_df['Duration_seconds'] = date_name_role_zip_df['Duration'].dt.total_seconds()
date_name_role_zip_df['Duration_hours'] = date_name_role_zip_df['Duration_seconds'] / (60*60)

date_name_role_zip_df['Duration'] = date_name_role_zip_df['Duration'].fillna(pd.Timedelta(seconds=0))
date_name_role_zip_df['Duration'] = date_name_role_zip_df['Duration'].apply(lambda x: f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}")

def status_marker(x):
    if pd.isnull(x):
        return 'Absent'
    elif x >= 0 and x < 1:
        return "Absent(Less than 1 hr)"
    elif x >= 1 and x < 4:
        return 'Half Day(less than 4 Hr)'
    elif x >= 4 and x < 8:
        return 'Half Day'
    else:
        return 'Present'

date_name_role_zip_df['Status'] = date_name_role_zip_df['Duration_hours'].apply(status_marker)

# Display and download
if not date_name_role_zip_df.empty:
    date_name_role_zip_df['Date'] = pd.to_datetime(date_name_role_zip_df['Date']).dt.strftime('%d/%b/%Y')
    st.dataframe(date_name_role_zip_df[['Name', 'Role', 'Date', 'In_Time', 'Out_Time', 'Duration', 'Status']])

    st.write("## Daily Summary:")
    st.dataframe(daily_report)

    st.write("## Shift-Wise Hourly Summary:")
    st.dataframe(shift_wise_report)

    st.write("## Hourly In-Time Breakdown:")
    st.dataframe(hourly_in_report)

    st.write("## Hourly Out-Time Breakdown:")
    st.dataframe(hourly_out_report)

    csv = date_name_role_zip_df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="attendance_report.csv",
        mime="text/csv",
    )
else:
    st.warning("No data found for the selected filter.")