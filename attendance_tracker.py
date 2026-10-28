
"""Student Attendance Tracker with secure reporting and ERP integration."""

import csv
import os
import ssl
import tarfile
from datetime import date
from pathlib import Path

import requests


# Application configuration
students = {}
attendance_register = {}

ERP_URL = os.getenv("ERP_URL", "")
ERP_API_KEY = os.getenv("ERP_API_KEY", "")
MIN_ATTENDANCE = 75
VALID_STATUSES = {"P", "A", "L", "H"}


def add_student(roll_no, name, section="A"):
    """Add a student to the attendance register."""
    if not roll_no or not name:
        raise ValueError("Roll number and name are required.")

    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def mark_attendance(roll_no, attendance_date, status, register=None):
    """Record attendance after validating the student, date, and status."""
    if roll_no not in students:
        raise ValueError(f"Unknown student roll number: {roll_no}")

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}. "
            f"Allowed statuses: {', '.join(sorted(VALID_STATUSES))}"
        )

    try:
        parsed_date = date.fromisoformat(attendance_date)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Date must use the YYYY-MM-DD format."
        ) from exc

    if parsed_date.isoformat() != attendance_date:
        raise ValueError("Date must use the YYYY-MM-DD format.")

    if parsed_date > date.today():
        raise ValueError("Future attendance dates are not allowed.")

    if register is None:
        register = attendance_register

    register.setdefault(attendance_date, []).append(roll_no)
    students[roll_no]["records"].append((attendance_date, status))
    return register


def attendance_percentage(roll_no):
    """Calculate the percentage of recorded sessions marked present."""
    records = students[roll_no]["records"]
    total = len(records)

    if total == 0:
        return 0

    present = sum(status == "P" for _, status in records)
    return int(present / total * 100)


def is_eligible(percentage):
    """Return whether a student meets the minimum attendance threshold."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return students who do not meet the minimum attendance threshold."""
    return [
        roll_no
        for roll_no in students
        if not is_eligible(attendance_percentage(roll_no))
    ]


def has_long_absence(roll_no, days=3):
    """Check for a consecutive sequence of absences in recorded sessions."""
    if days < 1:
        raise ValueError("Days must be at least 1.")

    statuses = [
        status for _, status in students[roll_no]["records"]
    ]

    return any(
        all(status == "A" for status in statuses[index:index + days])
        for index in range(len(statuses) - days + 1)
    )


def latest_date(roll_no):
    """Return the latest attendance date, or None if no records exist."""
    records = students[roll_no]["records"]

    if not records:
        return None

    return max(attendance_date for attendance_date, _ in records)


def _safe_csv_value(value):
    """Prevent spreadsheet formula execution for untrusted CSV values."""
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def export_csv(path="attendance.csv"):
    """Export student attendance percentages to a UTF-8 CSV file."""
    output_path = Path(path)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            writer.writerow([
                _safe_csv_value(roll_no),
                _safe_csv_value(student["name"]),
                attendance_percentage(roll_no),
            ])

    return str(output_path)


def sync_to_erp(roll_no):
    """Send attendance to the ERP only when credentials are configured."""
    if not ERP_URL or not ERP_API_KEY:
        print("ERP sync skipped: ERP_URL and ERP_API_KEY are not configured.")
        return None

    if roll_no not in students:
        raise ValueError(f"Unknown student roll number: {roll_no}")

    payload = {
        "roll_no": roll_no,
        "pct": attendance_percentage(roll_no),
    }

    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=10,
    )
    response.raise_for_status()
    return response.status_code


def backup_reports():
    """Create a compressed archive of CSV reports in the current directory."""
    backup_path = Path("reports_backup.tgz")
    csv_files = sorted(Path.cwd().glob("*.csv"))

    with tarfile.open(backup_path, mode="w:gz") as archive:
        for csv_file in csv_files:
            if csv_file.is_file():
                archive.add(csv_file, arcname=csv_file.name)

    return str(backup_path)


def legacy_channel():
    """Return a secure TLS context using the platform's default settings."""
    return ssl.create_default_context()


def run_job(command):
    """Represent a reminder job without executing an operating-system shell."""
    if not isinstance(command, str) or not command.strip():
        raise ValueError("A non-empty command description is required.")

    return {"command": command, "shell": False}


def schedule_reminders():
    """Prepare the attendance reminder job without executing it."""
    return run_job("send_sms --shortage")


def main():
    """Run a demonstration of the attendance tracker."""
    students.clear()
    attendance_register.clear()

    add_student("R01", "Aditi")
    add_student("R02", '=HYPERLINK("http://evil.example","Bharat")')

    r01_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "A"),
        ("2026-09-04", "P"),
        ("2026-09-05", "A"),
    ]

    r02_records = [
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-09-05", "P"),
    ]

    for attendance_date, status in r01_records:
        mark_attendance("R01", attendance_date, status)

    for attendance_date, status in r02_records:
        mark_attendance("R02", attendance_date, status)

    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print(
        "Register entries for 2026-09-01:",
        attendance_register["2026-09-01"],
    )
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped unless credentials are configured.")


if __name__ == "__main__":
    main()
