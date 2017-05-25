# -*- coding: utf-8 -*-
"""
Created on Wed May 17 20:30:40 2017

@author: filippo
"""

import csv
import pandas as pd
from datetime import datetime as dt

# Create schedule structure
columns=['BOOK_DATE','BOOK_TIME','EMPLOYEE','MEETING_DATE',
         'MEETING_START', 'DURATION']
schedule_df=pd.DataFrame(columns=columns)

#Input assumed to be in text file
schedule_input='./schedule_input.csv'
try:
    input_fh = open(schedule_input)
except:
    print("schedule_input.csv not found")
    raise SystemExit
input_read=csv.reader(input_fh, delimiter=' ')

# Get office hours from header
office_hours=next(input_read)
day_start_time=office_hours[0]
day_end_time=office_hours[1]
# calculate number of opening hours to be used in maximum meeting duration check

#Normalize office hours to HH:MM format:
day_start_time=day_start_time[:2]+':'+day_start_time[2:]
day_end_time=day_end_time[:2]+':'+day_end_time[2:]
#Read input bookings
for row in input_read:
    booking_request=row + next(input_read)
    schedule_df=schedule_df.append(pd.Series(booking_request, index=columns),ignore_index=True)    
input_fh.close()

#Called to calculate the meeting end time
def set_meeting_end_time(row):
    meeting_start=dt.strptime(row['MEETING_START'], '%H:%M')
    return ('%02d:%02d' % (meeting_start.hour+
                               int(row['DURATION']),
                                meeting_start.minute))
# Add meeting end time
schedule_df['MEETING_END']=schedule_df.apply(set_meeting_end_time, axis=1)

# Remove meetings that start or end outside business hours
schedule_df=schedule_df.loc[(schedule_df['MEETING_START']>=day_start_time) & 
                             (schedule_df['MEETING_END']<=day_end_time)] 
                
# process in chronological order according to booking time
schedule_df=schedule_df.sort_values( ['BOOK_DATE','BOOK_TIME'], ascending=True)
schedule_df=schedule_df.reset_index(drop=True)

# Filter overlapping meetings
confirmed_df=pd.DataFrame(columns=columns)
for index, row in schedule_df.iterrows():
    overlap=False #default
    for index2,row2 in confirmed_df.iterrows():
        if ((row['MEETING_DATE']+row['MEETING_START']>=row2['MEETING_DATE']+row2['MEETING_END'])
            or (row['MEETING_DATE']+row['MEETING_END']<= row2['MEETING_DATE']+row2['MEETING_START'])):
            continue
        else:    
            overlap=True
    if not overlap:
        confirmed_df=confirmed_df.append(row) #add meeting if no overlap
# Order in meeting chronological order        
confirmed_df=confirmed_df.sort_values( ['MEETING_DATE','MEETING_START'], ascending=True)
confirmed_df=confirmed_df.reset_index(drop=True)


prev_meeting_date='' #initialize previous meeting date
for index, row in confirmed_df.iterrows():
    #print date only once
    if (row['MEETING_DATE']!=prev_meeting_date):
        print (row['MEETING_DATE'])
    print (row['MEETING_START'], row['MEETING_END'], row['EMPLOYEE'])
    prev_meeting_date=row['MEETING_DATE']

