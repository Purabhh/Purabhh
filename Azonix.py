import pandas as pd
import requests
import time
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

url = "http://demo.azonix.in:15080/info"

# MySQL connection configuration
host = 'localhost'
port = 3306
database = 'sakila'
user = 'root'
password = 'griezmann7'
table_name = 'purabh'

def insert_data_to_mysql(data, cursor):
    query = f"INSERT INTO {table_name} (Version, Station_ID, Local_IP, Date_Time, Uptime, Relay_Status, Station_Status, EVSE_Status, Elapsed_Time, Amps, AC_Voltage, DC_Voltage, Temperature, Wattage, Free_Heap, Last_KWH) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.executemany(query, data)

try:
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        database='sakila',
        user='root',
        password='griezmann7',
        auth_plugin='mysql_native_password'
    )

    if conn.is_connected():
        print('Connected to MySQL database')

    cursor = conn.cursor()

    while True:
        try:
            response = requests.get(url)
            data = response.json()
            print("Data from URL:", data)

            # Print the value of 'Date_Time' before conversion
            print("Value of 'Date_Time' before conversion:", data['Date_Time'])

            # Convert 'Date_Time' to the correct format if necessary
            date_time_str = data['Date_Time']
            try:
                date_time_obj = datetime.strptime(date_time_str, '%d-%m-%YT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                data['Date_Time'] = date_time_obj
            except ValueError:
                print(f"Error parsing Date_Time: {date_time_str}")

            # Print the value of 'Date_Time' before conversion
            print("Value of 'Date_Time' after conversion:", data['Date_Time'])

            # Ensure 'Last_KWH' is in the correct format
            last_kwh_value = data['Last_KWH']
            #try:
                # Try parsing as datetime
               # last_kwh_obj = datetime.strptime(last_kwh_value, '%d-%m-%YT%H:%M:%S')
                #data['Last_KWH'] = last_kwh_obj
            #except ValueError:
            try:
                    # If not datetime, try converting to Decimal
                    data['Last_KWH'] = Decimal(last_kwh_value)
            except ValueError:
                    print(f"Error parsing Last_KWH as Decimal: {last_kwh_value}")

            # Construct DataFrame from the data
            print("Value of 'Date_Time' after conversion:", data['Date_Time'])

            df = pd.DataFrame({
               'Version': [data['Version']],
                'Station_ID': [data['Station_ID']],
                'Local_IP': [data['Local_IP']],
                'Date_Time': [data['Date_Time']],
                'Uptime': [data['Uptime']],
                'Relay_Status': [int(data['Relay_Status'])],
                'Station_Status': [data['Station_Status']],
                'EVSE_Status': [data['EVSE_Status']],
                'Elapsed_Time': [int(data['Elapsed_Time'])],
                'Amps': [Decimal(data['Amps'])],
                'AC_Voltage': [int(data['AC_Voltage'])],
                'DC_Voltage': [Decimal(data['DC_Voltage'])],
                'Temperature': [int(data['Temperature'])],
                'Wattage': [int(data['Wattage'])],
                'Free_Heap': [int(data['Free_Heap'])],
                'Last_KWH': [Decimal(data['Last_KWH'])] 
            })

            print("DataFrame:", df)

            # Convert DataFrame to list of tuples
            data_tuples = [tuple(row) for row in df.values]

            # Insert data into MySQL
            insert_data_to_mysql(data_tuples, cursor)

            # Commit the transaction
            conn.commit()

            print('Data inserted successfully')
            time.sleep(60)
        
        except KeyboardInterrupt:
            print("Data insertion stopped")
            break
        
        except Exception as e:
            print(f"Error: {e}")
            break

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print('MySQL connection closed')
