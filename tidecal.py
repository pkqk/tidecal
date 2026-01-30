import csv
from datetime import datetime, timedelta


# Input and output file paths
# https://static.charts.linz.govt.nz/tide-tables/maj-ports/csv/Auckland%202026.csv
CSV_FILE = 'data/2026.csv'
ICS_FILE = 'tides.ics'


# Helper to create an ICS event
def create_ics_event(dt, summary):
    dtstart = (dt - timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')
    dtend = (dt + timedelta(hours=1)).strftime('%Y%m%dT%H%M%S')
    return f"""
BEGIN:VEVENT
DTSTART;TZID=Pacific/Auckland:{dtstart}
DTEND;TZID=Pacific/Auckland:{dtend}
SUMMARY:{summary}
END:VEVENT
"""

def main():
    events = []
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Skip header/metadata lines
            if not row or not row[0].strip().isdigit():
                continue
            # Parse date
            day = int(row[0])
            month = int(row[2])
            year = int(row[3])
            # Loop through all time/height pairs in the row
            # Time/height pairs start at column 4 (0-based), then every 2 columns
            for i in range(4, len(row)-1, 2):
                time_str = row[i]
                height_str = row[i+1]
                if time_str and height_str:
                    try:
                        height = float(height_str)
                    except ValueError:
                        continue
                    if height > 2:
                        dt = datetime(year, month, day, int(time_str[:2]), int(time_str[3:5]))
                        summary = f"High Tide: {height}m"
                        events.append(create_ics_event(dt, summary))
    # Write ICS file
    with open(ICS_FILE, 'w', encoding='utf-8') as icsfile:
        icsfile.write("BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n")
        for event in events:
            icsfile.write(event)
        icsfile.write("END:VCALENDAR\n")

if __name__ == '__main__':
    main()
