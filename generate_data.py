"""
Smart School ERP - Realistic Dummy Data Generator
Generates 6 CSV files with 1000+ rows each:
  1. students.csv        - Student master data (1000 students)
  2. teachers.csv         - Teacher/faculty data (80 teachers)
  3. attendance.csv       - Daily attendance log (30,000+ rows)
  4. academic_records.csv - Exam/test scores (5,000+ rows)
  5. classroom_sensors.csv- IoT sensor readings (5,000+ rows)
  6. timetable.csv        - Class schedule (1,000+ rows)
"""

import csv, random, os, hashlib
from datetime import datetime, timedelta, date

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT, exist_ok=True)

# ---------- helpers ----------
FIRST_MALE = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna",
    "Ishaan","Shaurya","Atharva","Advik","Pranav","Advaith","Aarush","Kabir","Ritvik",
    "Darsh","Arnav","Dhruv","Harsh","Kunal","Manav","Nikhil","Om","Parth","Rohan",
    "Sahil","Tanmay","Utkarsh","Yash","Laksh","Dev","Rudra","Ansh","Kartik","Virat",
    "Rishi","Siddharth","Tejas","Varun","Aryan","Jay","Kian","Neel","Rahul","Soham"
]
FIRST_FEMALE = [
    "Saanvi","Aanya","Aadhya","Aaradhya","Ananya","Pari","Anika","Navya","Angel",
    "Diya","Myra","Sara","Iraa","Ahana","Kiara","Riya","Prisha","Kavya","Tara",
    "Isha","Meera","Sneha","Pooja","Nisha","Shreya","Tanvi","Avni","Zara","Siya",
    "Pihu","Mahi","Nandini","Aditi","Neha","Anjali","Divya","Khushi","Mansi","Radhika",
    "Simran","Trisha","Vedika","Anvi","Charvi","Gauri","Jiya","Lavanya","Mira","Palak"
]
LAST_NAMES = [
    "Sharma","Verma","Gupta","Singh","Kumar","Patel","Reddy","Nair","Iyer","Joshi",
    "Rao","Mishra","Pandey","Chauhan","Yadav","Jain","Shah","Mehta","Deshmukh","Kulkarni",
    "Thakur","Bhat","Pillai","Menon","Das","Mukherjee","Banerjee","Chatterjee","Sen","Ghosh",
    "Tiwari","Dubey","Saxena","Agarwal","Malhotra","Kapoor","Bhandari","Sinha","Mahajan","Deshpande",
    "Patil","Chavan","Pawar","Jadhav","More","Shinde","Gaikwad","Kadam","Bhosale","Kale"
]
SECTIONS = ["A","B","C","D"]
CLASSES = list(range(1, 13))  # Class 1-12
STREAMS_11_12 = {"Science": ["Physics","Chemistry","Biology","Mathematics","Computer Science"],
                 "Commerce": ["Accountancy","Business Studies","Economics","Mathematics","Informatics Practices"],
                 "Arts": ["History","Political Science","Geography","Economics","Sociology"]}
SUBJECTS_1_10 = ["English","Hindi","Mathematics","Science","Social Studies","Computer Science","Physical Education"]
BLOOD_GROUPS = ["A+","A-","B+","B-","O+","O-","AB+","AB-"]
CITIES = ["Delhi","Mumbai","Bangalore","Hyderabad","Chennai","Kolkata","Pune","Jaipur","Lucknow","Ahmedabad",
          "Chandigarh","Bhopal","Indore","Nagpur","Patna","Ranchi","Dehradun","Noida","Gurgaon","Faridabad"]
GUARDIAN_REL = ["Father","Mother","Guardian"]
CATEGORIES = ["General","OBC","SC","ST","EWS"]
HOUSES = ["Ganga","Yamuna","Narmada","Kaveri"]

TEACHER_SUBJECTS = ["English","Hindi","Mathematics","Physics","Chemistry","Biology",
                    "Computer Science","Social Studies","History","Geography","Economics",
                    "Accountancy","Business Studies","Political Science","Physical Education",
                    "Art","Music","Sanskrit"]
TEACHER_QUALIFICATIONS = ["B.Ed","M.Ed","M.A.","M.Sc.","M.Com.","Ph.D.","B.A. B.Ed","M.Tech"]

EXAM_TYPES = ["Unit Test 1","Unit Test 2","Mid Term","Unit Test 3","Unit Test 4","Final Exam"]

# ---- phone / email generators ----
def phone():
    return f"+91-{random.choice(['98','97','96','95','94','93','91','90','88','87','70','76','77','78','79'])}{random.randint(10000000,99999999)}"

def email(first, last, domain="gmail.com"):
    return f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{domain}"

def gen_dob(class_num):
    """Generate realistic DOB based on class (assuming academic year 2025-26)."""
    # Class 1 kid ~6 yrs old, Class 12 ~17 yrs old
    age = class_num + 5
    year = 2025 - age
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def admission_no(i):
    return f"ADM/{2020 + random.randint(0,5)}/{str(i).zfill(5)}"

def gen_rfid():
    return hashlib.md5(str(random.random()).encode()).hexdigest()[:12].upper()

# ==============================
# 1. STUDENTS (1000 rows)
# ==============================
print("Generating students.csv ...")
students = []
for i in range(1, 1001):
    gender = random.choice(["Male","Female"])
    first = random.choice(FIRST_MALE if gender == "Male" else FIRST_FEMALE)
    last = random.choice(LAST_NAMES)
    cls = random.choice(CLASSES)
    sec = random.choice(SECTIONS[:3] if cls <= 5 else SECTIONS)
    stream = random.choice(list(STREAMS_11_12.keys())) if cls >= 11 else None
    dob = gen_dob(cls)
    guardian_name = f"{random.choice(FIRST_MALE)} {last}"

    # performance bucket drives later scores
    perf = random.choices(["high","mid","low","at_risk"], weights=[25,45,20,10])[0]

    students.append({
        "student_id": f"STU{str(i).zfill(5)}",
        "admission_no": admission_no(i),
        "rfid_tag": gen_rfid(),
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "dob": dob.strftime("%Y-%m-%d"),
        "class": cls,
        "section": sec,
        "stream": stream or "",
        "roll_no": random.randint(1, 60),
        "blood_group": random.choice(BLOOD_GROUPS),
        "category": random.choices(CATEGORIES, weights=[40,30,15,10,5])[0],
        "house": random.choice(HOUSES),
        "guardian_name": guardian_name,
        "guardian_relation": random.choice(GUARDIAN_REL),
        "guardian_phone": phone(),
        "guardian_email": email(guardian_name.split()[0], last),
        "address": f"{random.randint(1,500)}, Sector {random.randint(1,80)}, {random.choice(CITIES)}",
        "city": random.choice(CITIES),
        "pincode": str(random.randint(110001, 900100)),
        "admission_date": f"{random.randint(2020,2025)}-{random.randint(4,7):02d}-{random.randint(1,28):02d}",
        "is_active": random.choices([1,0], weights=[92,8])[0],
        "performance_bucket": perf,  # internal label for AI
        "dropout_risk_score": round({"high":random.uniform(0,0.15),"mid":random.uniform(0.1,0.35),"low":random.uniform(0.25,0.55),"at_risk":random.uniform(0.5,0.95)}[perf], 3),
    })

with open(os.path.join(OUT, "students.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=students[0].keys())
    w.writeheader(); w.writerows(students)

# ==============================
# 2. TEACHERS (80 rows)
# ==============================
print("Generating teachers.csv ...")
teachers = []
for i in range(1, 81):
    gender = random.choice(["Male","Female"])
    first = random.choice(FIRST_MALE if gender == "Male" else FIRST_FEMALE)
    last = random.choice(LAST_NAMES)
    subj = random.choice(TEACHER_SUBJECTS)
    join_year = random.randint(2000, 2023)
    teachers.append({
        "teacher_id": f"TCH{str(i).zfill(4)}",
        "employee_id": f"EMP/{join_year}/{str(random.randint(1000,9999))}",
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "dob": f"{random.randint(1965,1995)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "phone": phone(),
        "email": email(first, last, "school.edu.in"),
        "subject_primary": subj,
        "subject_secondary": random.choice([s for s in TEACHER_SUBJECTS if s != subj]),
        "qualification": random.choice(TEACHER_QUALIFICATIONS),
        "experience_years": 2025 - join_year,
        "joining_date": f"{join_year}-{random.randint(4,8):02d}-{random.randint(1,28):02d}",
        "designation": random.choices(["PGT","TGT","PRT","HOD","Vice Principal","Principal"],
                                       weights=[30,30,20,10,5,2])[0],
        "assigned_classes": ",".join(str(c) for c in random.sample(CLASSES, random.randint(2,5))),
        "class_teacher_of": f"{random.choice(CLASSES)}-{random.choice(SECTIONS)}" if random.random() < 0.4 else "",
        "is_active": random.choices([1,0], weights=[95,5])[0],
    })

with open(os.path.join(OUT, "teachers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=teachers[0].keys())
    w.writeheader(); w.writerows(teachers)

# ==============================
# 3. ATTENDANCE (30,000+ rows)
# ==============================
print("Generating attendance.csv ...")
# Generate 30 school days of attendance for all 1000 students
school_days = []
d = date(2025, 7, 1)
while len(school_days) < 30:
    if d.weekday() < 6:  # Mon-Sat
        school_days.append(d)
    d += timedelta(days=1)

attendance_rows = []
aid = 1
for day in school_days:
    for stu in students:
        if stu["is_active"] == 0:
            continue
        # Attendance probability based on performance bucket
        prob = {"high": 0.96, "mid": 0.90, "low": 0.82, "at_risk": 0.65}[stu["performance_bucket"]]
        present = random.random() < prob

        if present:
            # Realistic entry time: school starts 7:30 AM
            entry_h = 7
            entry_m = random.randint(10, 45)
            if random.random() < 0.08:  # 8% late
                entry_h = 8
                entry_m = random.randint(0, 30)
            entry_time = f"{entry_h:02d}:{entry_m:02d}"
            status = "Present" if entry_h < 8 else "Late"
            exit_time = f"{random.choice([13,14,15]):02d}:{random.randint(0,59):02d}"
            method = random.choices(["RFID","Biometric","Face Recognition"], weights=[50,30,20])[0]
        else:
            entry_time = ""
            exit_time = ""
            status = random.choices(["Absent","Medical Leave","Authorized Leave"], weights=[70,20,10])[0]
            method = ""

        attendance_rows.append({
            "attendance_id": f"ATT{str(aid).zfill(7)}",
            "student_id": stu["student_id"],
            "date": day.strftime("%Y-%m-%d"),
            "day_of_week": day.strftime("%A"),
            "class": stu["class"],
            "section": stu["section"],
            "status": status,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "capture_method": method,
            "rfid_tag": stu["rfid_tag"] if method == "RFID" else "",
            "is_anomaly": 1 if (status == "Present" and stu["performance_bucket"] == "at_risk" and random.random() < 0.3) else 0,
        })
        aid += 1

with open(os.path.join(OUT, "attendance.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=attendance_rows[0].keys())
    w.writeheader(); w.writerows(attendance_rows)
print(f"  -> {len(attendance_rows)} attendance records")

# ==============================
# 4. ACADEMIC RECORDS (6,000 rows)
# ==============================
print("Generating academic_records.csv ...")
academic = []
rid = 1
for stu in students:
    cls = stu["class"]
    subjects = STREAMS_11_12.get(stu["stream"], SUBJECTS_1_10) if cls >= 11 else SUBJECTS_1_10
    # Pick 2 random exam types per student to keep ~6000 rows
    exams = random.sample(EXAM_TYPES, 2)
    for exam in exams:
        max_marks = 100 if "Final" in exam or "Mid" in exam else 50
        for subj in subjects:
            # Marks based on performance bucket
            base = {"high": 80, "mid": 60, "low": 40, "at_risk": 25}[stu["performance_bucket"]]
            noise = random.gauss(0, 10)
            marks = max(0, min(max_marks, int((base + noise) * max_marks / 100)))

            academic.append({
                "record_id": f"REC{str(rid).zfill(7)}",
                "student_id": stu["student_id"],
                "class": cls,
                "section": stu["section"],
                "subject": subj,
                "exam_type": exam,
                "academic_year": "2025-26",
                "max_marks": max_marks,
                "marks_obtained": marks,
                "percentage": round(marks / max_marks * 100, 1),
                "grade": "A+" if marks/max_marks >= 0.9 else "A" if marks/max_marks >= 0.8 else "B+" if marks/max_marks >= 0.7 else "B" if marks/max_marks >= 0.6 else "C" if marks/max_marks >= 0.5 else "D" if marks/max_marks >= 0.33 else "F",
                "teacher_id": random.choice(teachers)["teacher_id"],
                "remarks": random.choice(["","Good","Needs improvement","Excellent","Average","Absent for exam","Retest required"]),
            })
            rid += 1

with open(os.path.join(OUT, "academic_records.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=academic[0].keys())
    w.writeheader(); w.writerows(academic)
print(f"  -> {len(academic)} academic records")

# ==============================
# 5. CLASSROOM SENSORS / IoT (5,000 rows)
# ==============================
print("Generating classroom_sensors.csv ...")
rooms = [f"Room-{floor}{str(r).zfill(2)}" for floor in ["G","1","2","3"] for r in range(1, 16)]
sensor_rows = []
sid = 1
for day in school_days[:10]:  # 10 days of sensor data
    for room in rooms:
        for hour in range(7, 16):  # 7 AM to 3 PM
            occupancy = random.randint(0, 55) if 8 <= hour <= 14 else random.randint(0, 10)
            sensor_rows.append({
                "reading_id": f"SNS{str(sid).zfill(7)}",
                "room_id": room,
                "date": day.strftime("%Y-%m-%d"),
                "time": f"{hour:02d}:00",
                "temperature_c": round(random.uniform(22, 38) if 10 <= hour <= 14 else random.uniform(20, 30), 1),
                "humidity_pct": round(random.uniform(35, 75), 1),
                "occupancy_count": occupancy,
                "max_capacity": 60,
                "utilization_pct": round(occupancy / 60 * 100, 1),
                "ac_status": "ON" if occupancy > 20 else "OFF",
                "light_status": "ON" if occupancy > 0 else "OFF",
                "projector_status": random.choice(["ON","OFF"]) if occupancy > 10 else "OFF",
                "air_quality_index": random.randint(30, 180),
            })
            sid += 1

with open(os.path.join(OUT, "classroom_sensors.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=sensor_rows[0].keys())
    w.writeheader(); w.writerows(sensor_rows)
print(f"  -> {len(sensor_rows)} sensor readings")

# ==============================
# 6. TIMETABLE (1,200+ rows)
# ==============================
print("Generating timetable.csv ...")
PERIODS = [
    ("1","07:30","08:10"), ("2","08:10","08:50"), ("3","08:50","09:30"),
    ("4","09:45","10:25"), ("5","10:25","11:05"), ("6","11:05","11:45"),
    ("7","12:00","12:40"), ("8","12:40","13:20"),
]
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

tt_rows = []
tid = 1
for cls in CLASSES:
    for sec in SECTIONS[:3] if cls <= 5 else SECTIONS:
        subjects = STREAMS_11_12.get(random.choice(list(STREAMS_11_12.keys())), SUBJECTS_1_10) if cls >= 11 else SUBJECTS_1_10
        for day in DAYS:
            for period_no, start, end in PERIODS:
                subj = random.choice(subjects)
                teacher = random.choice([t for t in teachers if t["subject_primary"] == subj] or teachers)
                room = random.choice(rooms)
                tt_rows.append({
                    "timetable_id": f"TT{str(tid).zfill(6)}",
                    "class": cls,
                    "section": sec,
                    "day": day,
                    "period": period_no,
                    "start_time": start,
                    "end_time": end,
                    "subject": subj,
                    "teacher_id": teacher["teacher_id"],
                    "teacher_name": f"{teacher['first_name']} {teacher['last_name']}",
                    "room_id": room,
                    "is_lab": 1 if subj in ["Physics","Chemistry","Biology","Computer Science"] and random.random() < 0.3 else 0,
                    "academic_year": "2025-26",
                })
                tid += 1

with open(os.path.join(OUT, "timetable.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=tt_rows[0].keys())
    w.writeheader(); w.writerows(tt_rows)
print(f"  -> {len(tt_rows)} timetable entries")

# ---------- Summary ----------
print("\nAll CSVs generated in ./data/ folder:")
for fname in ["students.csv","teachers.csv","attendance.csv","academic_records.csv","classroom_sensors.csv","timetable.csv"]:
    path = os.path.join(OUT, fname)
    with open(path, encoding="utf-8") as f:
        lines = sum(1 for _ in f) - 1
    print(f"   {fname:30s} -> {lines:,} rows")
