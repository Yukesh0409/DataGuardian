import pandas as pd

def load_data(file_path):
    """Load the CSV file into a pandas DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df, None
    except Exception as e:
        return None, str(e)

def remove_unwanted_columns(df):
    """Remove unwanted columns from the DataFrame."""
    columns_to_keep = [
        'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime', 
        'passenger_count', 'trip_distance', 'PULocationID', 'DOLocationID', 
        'fare_amount', 'total_amount'
    ]
    try:
        df = df[columns_to_keep]
        return df, None
    except Exception as e:
        return None, str(e)

def validate_data(df):
    """Perform data validation."""
    errors = []
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        errors.append(("Missing values", missing_values.to_dict()))

    # Ensure correct data types
    try:
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')
        df['VendorID'] = df['VendorID'].astype(int)
        df['passenger_count'] = df['passenger_count'].astype(int)
        df['trip_distance'] = df['trip_distance'].astype(float)
        df['PULocationID'] = df['PULocationID'].astype(int)
        df['DOLocationID'] = df['DOLocationID'].astype(int)
        df['fare_amount'] = df['fare_amount'].astype(float)
        df['total_amount'] = df['total_amount'].astype(float)
    except Exception as e:
        errors.append(("Type conversion error", str(e)))
    
    return df, errors

def generate_new_columns(df):
    """Generate eight new columns."""
    errors = []
    
    try:
        df['trip_duration_minutes'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
    except Exception as e:
        errors.append(("Trip duration calculation error", str(e)))

    try:
        df['average_speed_mph'] = df['trip_distance'] / (df['trip_duration_minutes'] / 60)
    except Exception as e:
        errors.append(("Average speed calculation error", str(e)))

    try:
        df['is_short_trip'] = df['trip_distance'].apply(lambda x: 1 if x < 1 else 0)
    except Exception as e:
        errors.append(("Short trip flag error", str(e)))

    try:
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    except Exception as e:
        errors.append(("Pickup hour extraction error", str(e)))

    try:
        df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
    except Exception as e:
        errors.append(("Pickup day of week extraction error", str(e)))

    try:
        df['is_weekend'] = df['pickup_day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    except Exception as e:
        errors.append(("Weekend flag error", str(e)))

    try:
        df['tip_percentage'] = ((df['total_amount'] - df['fare_amount']) / df['fare_amount']) * 100
    except Exception as e:
        errors.append(("Tip percentage calculation error", str(e)))

    try:
        def categorize_distance(distance):
            if distance < 1:
                return 'short'
            elif distance < 5:
                return 'medium'
            else:
                return 'long'
        df['trip_distance_category'] = df['trip_distance'].apply(categorize_distance)
    except Exception as e:
        errors.append(("Trip distance category error", str(e)))
    
    return df, errors

def rename_columns(df):
    """Rename columns to more descriptive names."""
    try:
        df.rename(columns={
            'VendorID': 'vendor_id',
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'passenger_count': 'num_passengers',
            'trip_distance': 'trip_distance_miles',
            'PULocationID': 'pickup_location_id',
            'DOLocationID': 'dropoff_location_id',
            'fare_amount': 'fare_amount_usd',
            'total_amount': 'total_amount_usd'
        }, inplace=True)
        return df, None
    except Exception as e:
        return None, str(e)

def main(file_path):
    df, error = load_data(file_path)
    if error:
        error_df = pd.DataFrame({'row': [None], 'error': [error]})
        print(error_df)
        return

    df, error = remove_unwanted_columns(df)
    if error:
        error_df = pd.DataFrame({'row': [None], 'error': [error]})
        print(error_df)
        return

    df, validation_errors = validate_data(df)
    if validation_errors:
        error_df = pd.DataFrame(validation_errors, columns=['row', 'error'])
        print(error_df)
        return

    df, column_errors = generate_new_columns(df)
    if column_errors:
        error_df = pd.DataFrame(column_errors, columns=['row', 'error'])
        print(error_df)
        return

    df, error = rename_columns(df)
    if error:
        error_df = pd.DataFrame({'row': [None], 'error': [error]})
        print(error_df)
        return

    # Display the updated DataFrame
    print(df.head())

# Call the main function with the file path
file_path = 'temp.csv'
main(file_path)
