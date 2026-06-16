import pandas as pd
from datetime import datetime, timedelta
import random

pass_list = pd.read_csv("csv_files/orbit_samples.csv")
log = open("moveLog.txt", "a")

pass_list["Timestamp"] = pd.to_datetime(pass_list["Timestamp (UTC)"])
target_list = []
processed = 0

while not pass_list.empty:
    selection = pass_list.sort_values(by="Timestamp")

    time_stamp1 = selection.iloc[0]["Timestamp"]

    choices = pass_list[pass_list['Timestamp'] == time_stamp1]
    selection = random.randint(0, len(choices) - 1)
    satellite = choices.iloc[selection]["Satellite"]

    

    curr_time = time_stamp1
    for index, row in pass_list.iterrows():
        
        if row["Satellite"] == satellite and curr_time + timedelta(seconds=1) == row["Timestamp"]:
            target_list.append(row)
            curr_time = row["Timestamp"]
            processed += 1
            print("satellites processed: " + str(processed))
        
    pass_list = pass_list[pass_list['Timestamp'] >= curr_time + timedelta(seconds=5)]

movement_list = pd.DataFrame(target_list)


movement_list.to_csv("target_list.csv", index=False)
