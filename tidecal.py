import csv
from datetime import datetime, timedelta
import sys

# This script reads a CSV tide table and generates an ICS calendar file with high tide events.
# https://static.charts.linz.govt.nz/tide-tables/maj-ports/csv/Auckland%202026.csv


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
""".strip()


def main():
    # Get CSV file from command line argument or use default
    if len(sys.argv) > 2:
        csv_file = sys.argv[1]
        ics_file = sys.argv[2]
    else:
        print("Usage: python tidecal.py <tide_csv_file> <output_ics_file>")
        sys.exit(1)
    title = None
    events = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not title and row:
                title = row[1].strip()
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
                        summary = f"High Tide: {time_str} {height}m"
                        events.append(create_ics_event(dt, summary))

    with open(ics_file, 'w', encoding='utf-8') as ics:
        ics.write("BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n")
        ics.write(f"X-WR-CALNAME:High Tide {title}\n")
        for event in events:
            ics.write(event+"\n")
        ics.write("END:VCALENDAR\n")

if __name__ == '__main__':
    main()
