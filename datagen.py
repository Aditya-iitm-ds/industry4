import csv
import random
from datetime import datetime, timedelta

def create_file(filename: str, source_name: str, total_rows: int = 1000):
    start_time = datetime.utcnow()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "amount", "event_time", "source_file"])

        for i in range(1, total_rows + 1):
            event_time = (start_time + timedelta(seconds=i)).isoformat()
            writer.writerow([
                i,
                f"user_{i}",
                random.randint(100, 999),
                event_time,
                source_name
            ])

if __name__ == "__main__":
    create_file("input1.csv", "input1")
    create_file("input2.csv", "input2")
    print("Created input1.csv and input2.csv")