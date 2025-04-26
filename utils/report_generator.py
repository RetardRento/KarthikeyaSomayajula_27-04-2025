import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import timedelta
from pytz import timezone, utc
import time
import datetime
from utils.error_message import DB_URL_MISSING

# Load environment variables
load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
DB_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
if not DB_URL:
    raise ValueError(DB_URL_MISSING)

engine = create_engine(DB_URL)
reports = {}

def generate_report(report_id: str):
    start_time = time.time()
    print(f"[{datetime.datetime.now()}] Report generation started for report_id={report_id}")
    BATCH_SIZE = 50000

    with engine.connect() as conn:
        # Fetch all required data in fewer queries
        current_time = pd.read_sql("SELECT MAX(timestamp_utc) as max_time FROM store_status", conn)['max_time'][0]
        current_time = pd.to_datetime(current_time)
        last_hour, last_day, last_week = current_time - timedelta(hours=1), current_time - timedelta(days=1), current_time - timedelta(days=7)

        store_status = pd.read_sql(
            f"""SELECT store_id, status, timestamp_utc 
                FROM store_status 
                WHERE timestamp_utc >= '{last_week}'""", conn
        )
        store_status['timestamp_utc'] = pd.to_datetime(store_status['timestamp_utc'])
        store_status['status'] = store_status['status'].str.lower()

        timezones = pd.read_sql("SELECT * FROM timezones", conn)
        business_hours = pd.read_sql("SELECT * FROM menu_hours", conn)

    # Precompute business hours for all stores
    business_hours['start_time_local'] = pd.to_datetime(business_hours['start_time_local'], format="%H:%M:%S").dt.time
    business_hours['end_time_local'] = pd.to_datetime(business_hours['end_time_local'], format="%H:%M:%S").dt.time

    # Merge timezone info
    store_status = store_status.merge(timezones, on='store_id', how='left').fillna({'timezone_str': 'America/Chicago'})

    # Convert timestamps to local time in bulk
    store_status['local_time'] = store_status.apply(
        lambda row: row['timestamp_utc'].astimezone(timezone(row['timezone_str'])), axis=1
    )

    report_rows = []
    for store_id, group in store_status.groupby('store_id'):
        group = group.sort_values('timestamp_utc')

        # Filter business hours in bulk
        hours = business_hours[business_hours['store_id'] == store_id]
        if not hours.empty:
            group['within_hours'] = group['local_time'].apply(
                lambda local_dt: any(
                    hr['start_time_local'] <= local_dt.time() <= hr['end_time_local']
                    for _, hr in hours.iterrows()
                    if hr['dayofweek'] == local_dt.weekday()
                )
            )
            group = group[group['within_hours']]

        # Compute metrics
        metrics = compute_metrics_optimized(group, current_time, [last_hour, last_day, last_week])
        report_rows.append({
            "store_id": store_id,
            "uptime_last_hour": metrics[0][0],
            "uptime_last_day": round(metrics[1][0] / 60, 2),
            "uptime_last_week": round(metrics[2][0] / 60, 2),
            "downtime_last_hour": metrics[0][1],
            "downtime_last_day": round(metrics[1][1] / 60, 2),
            "downtime_last_week": round(metrics[2][1] / 60, 2)
        })

    # Save report
    df_out = pd.DataFrame(report_rows)
    file_path = f"report_{report_id}.csv"
    df_out.to_csv(file_path, index=False)
    reports[report_id] = file_path
    print(f"[{datetime.datetime.now()}] Report finished for {report_id}. Time taken: {time.time() - start_time:.2f}s")

def compute_metrics_optimized(group, current_time, time_windows):
    results = []

    for start_time in time_windows:
        df = group[(group['timestamp_utc'] >= start_time) & (group['timestamp_utc'] <= current_time)].copy()
        if df.empty:
            prev = group[group['timestamp_utc'] < start_time]
            if not prev.empty:
                last_known = prev.iloc[-1]
                status = last_known['status']
                duration = (current_time - start_time).total_seconds() / 60
                results.append((duration if status == 'active' else 0, duration if status != 'active' else 0))
            else:
                results.append((0, 0))
            continue

        need_start_pad = df.iloc[0]['timestamp_utc'] > start_time
        need_end_pad = df.iloc[-1]['timestamp_utc'] < current_time

        timestamps = list(df['timestamp_utc'])
        statuses = list(df['status'])

        if need_start_pad:
            prev = group[group['timestamp_utc'] < start_time]
            initial_status = prev.iloc[-1]['status'] if not prev.empty else df.iloc[0]['status']
            timestamps.insert(0, start_time)
            statuses.insert(0, initial_status)

        if need_end_pad:
            final_status = df.iloc[-1]['status']
            timestamps.append(current_time)
            statuses.append(final_status)

        padded_df = pd.DataFrame({
            'timestamp_utc': timestamps,
            'status': statuses
        }).sort_values('timestamp_utc').reset_index(drop=True)

        padded_df['next_timestamp'] = padded_df['timestamp_utc'].shift(-1)
        padded_df['duration'] = (padded_df['next_timestamp'] - padded_df['timestamp_utc']).dt.total_seconds() / 60
        padded_df = padded_df.dropna()

        uptime = padded_df.loc[padded_df['status'] == 'active', 'duration'].sum()
        downtime = padded_df.loc[padded_df['status'] == 'inactive', 'duration'].sum()
        results.append((uptime, downtime))

    return results
