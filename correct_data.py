import re
import csv
from pathlib import Path

input_path = Path("imu_content_spiral.csv")
output_path = Path("imu_content_spiral_corrected.csv")

# Three decimal floats followed by a timestamp.
# The first three values are parsed using their decimal points and signs.
row_pattern = re.compile(
    r"^"
    r"(?P<x>-?\d+\.\d+)"
    r"(?P<y>-?\d+\.\d+)"
    r"(?P<th>-?\d+\.\d+)"
    r"(?P<stamp>1791406\d+)"
    r"$"
)

failed_lines = []

with input_path.open("r") as infile, \
     output_path.open("w", newline="") as outfile:

    writer = csv.writer(outfile)
    writer.writerow(["x", "y", "th", "stamp"])

    for line_num, line in enumerate(infile, start=1):
        line = line.strip()

        if not line or line.startswith("x"):
            continue

        match = row_pattern.fullmatch(line)

        if match:
            writer.writerow([
                match.group("x"),
                match.group("y"),
                match.group("th"),
                match.group("stamp"),
            ])
        else:
            failed_lines.append((line_num, line))

print(f"Saved recovered CSV to {output_path}")
print(f"Rows that could not be parsed: {len(failed_lines)}")

for line_num, line in failed_lines:
    print(f"Could not parse line {line_num}: {line}")