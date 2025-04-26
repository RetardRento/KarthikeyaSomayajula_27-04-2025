from datetime import timedelta
import pandas as pd

def calculate_time_windows(current_time):
    """Calculate time windows for report generation."""
    last_hour = current_time - timedelta(hours=1)
    last_day = current_time - timedelta(days=1)
    last_week = current_time - timedelta(days=7)
    return [last_hour, last_day, last_week]

def compute_metrics_optimized(group, current_time, time_windows):
    results = []
    for start_time in time_windows:
        df = group[(group['timestamp_utc'] >= start_time) & (group['timestamp_utc'] <= current_time)].copy()
        if df.empty:
            # Assume active status if no data exists
            total_duration = (current_time - start_time).total_seconds() / 60
            results.append((total_duration, 0))
            continue
        
        need_start_pad = df.iloc[0]['timestamp_utc'] > start_time
        need_end_pad = df.iloc[-1]['timestamp_utc'] < current_time
        
        timestamps = list(df['timestamp_utc'])
        statuses = list(df['status'])
        
        if need_start_pad:
            prev = group[group['timestamp_utc'] < start_time]
            initial_status = prev.iloc[-1]['status'] if not prev.empty else 'active'
            timestamps.insert(0, start_time)
            statuses.insert(0, initial_status)
        
        if need_end_pad:
            final_status = df.iloc[-1]['status']
            timestamps.append(current_time)
            statuses.append(final_status)
        
        padded_df = pd.DataFrame({'timestamp_utc': timestamps, 'status': statuses}).sort_values('timestamp_utc').reset_index(drop=True)
        padded_df['next_timestamp'] = padded_df['timestamp_utc'].shift(-1)
        padded_df['duration'] = (padded_df['next_timestamp'] - padded_df['timestamp_utc']).dt.total_seconds() / 60
        padded_df = padded_df.dropna()
        
        uptime = padded_df.loc[padded_df['status'] == 'active', 'duration'].sum()
        downtime = padded_df.loc[padded_df['status'] == 'inactive', 'duration'].sum()
        results.append((uptime, downtime))
    return results
