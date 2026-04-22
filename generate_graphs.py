"""
Smart School ERP - Industry 4.0 Visualization Suite
Generates 8 publication-ready graphs from the dummy data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import os, warnings
warnings.filterwarnings("ignore")

DATA = os.path.join(os.path.dirname(__file__), "data")
OUT  = os.path.join(os.path.dirname(__file__), "graphs")
os.makedirs(OUT, exist_ok=True)

# Load data
students   = pd.read_csv(os.path.join(DATA, "students.csv"))
attendance = pd.read_csv(os.path.join(DATA, "attendance.csv"))
academic   = pd.read_csv(os.path.join(DATA, "academic_records.csv"))
sensors    = pd.read_csv(os.path.join(DATA, "classroom_sensors.csv"))
timetable  = pd.read_csv(os.path.join(DATA, "timetable.csv"))
teachers   = pd.read_csv(os.path.join(DATA, "teachers.csv"))

attendance["date"] = pd.to_datetime(attendance["date"])
sensors["date"]    = pd.to_datetime(sensors["date"])

# Color palette - professional dark theme
BG       = "#0f1117"
CARD_BG  = "#1a1d29"
TEXT     = "#e0e0e0"
ACCENT1  = "#00d4aa"  # teal
ACCENT2  = "#ff6b6b"  # coral
ACCENT3  = "#ffd93d"  # gold
ACCENT4  = "#6c5ce7"  # purple
ACCENT5  = "#00b4d8"  # sky blue
ACCENT6  = "#ff8c42"  # orange
GRID     = "#2a2d3a"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": CARD_BG,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "grid.color": GRID,
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 11,
})

# ================================================================
# GRAPH 1: Attendance Trends Over Time (Line + Area)
# ================================================================
print("1/8  Attendance Trends Over Time ...")
fig, ax = plt.subplots(figsize=(14, 6))

daily = attendance.groupby("date").apply(
    lambda x: pd.Series({
        "present_pct": (x["status"].isin(["Present","Late"])).mean() * 100,
        "late_pct": (x["status"] == "Late").mean() * 100,
        "absent_pct": (x["status"] == "Absent").mean() * 100,
    })
).reset_index()

ax.fill_between(daily["date"], daily["present_pct"], alpha=0.3, color=ACCENT1)
ax.plot(daily["date"], daily["present_pct"], color=ACCENT1, linewidth=2.5, marker="o", markersize=5, label="Present %")
ax.plot(daily["date"], daily["late_pct"], color=ACCENT3, linewidth=2, marker="s", markersize=4, label="Late %", linestyle="--")
ax.plot(daily["date"], daily["absent_pct"], color=ACCENT2, linewidth=2, marker="^", markersize=4, label="Absent %", linestyle="--")

# Add threshold line
ax.axhline(y=85, color=ACCENT2, linestyle=":", alpha=0.7, linewidth=1.5)
ax.text(daily["date"].iloc[0], 85.5, "  Min Threshold (85%)", color=ACCENT2, fontsize=9, alpha=0.8)

ax.set_title("Daily Attendance Trends - July 2025", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Date")
ax.set_ylabel("Percentage (%)")
ax.legend(loc="lower left", framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.set_ylim(0, 100)
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "01_attendance_trends.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 2: Subject-wise Performance (Grouped Bar + Violin)
# ================================================================
print("2/8  Subject-wise Performance ...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1.2, 1]})

# Left: Grouped bar by performance bucket
subj_perf = academic.merge(students[["student_id","performance_bucket"]], on="student_id")
pivot = subj_perf.groupby(["subject","performance_bucket"])["percentage"].mean().unstack()
pivot = pivot.reindex(columns=["high","mid","low","at_risk"])
subjects_sorted = pivot["high"].sort_values(ascending=True).index

colors_bar = [ACCENT1, ACCENT5, ACCENT3, ACCENT2]
pivot.loc[subjects_sorted].plot(kind="barh", ax=ax1, color=colors_bar, width=0.75, edgecolor="none")
ax1.set_title("Avg Score by Subject & Performance Bucket", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Average Percentage (%)")
ax1.legend(title="Bucket", framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID, fontsize=9)
ax1.grid(True, axis="x")

# Right: Violin plot for top 5 subjects
top5 = academic.groupby("subject")["percentage"].count().nlargest(5).index.tolist()
data_violin = [academic[academic["subject"] == s]["percentage"].values for s in top5]
parts = ax2.violinplot(data_violin, showmeans=True, showmedians=True)
for i, pc in enumerate(parts["bodies"]):
    pc.set_facecolor([ACCENT1, ACCENT5, ACCENT4, ACCENT3, ACCENT6][i])
    pc.set_alpha(0.7)
parts["cmeans"].set_color(ACCENT3)
parts["cmedians"].set_color(TEXT)
ax2.set_xticks(range(1, len(top5)+1))
ax2.set_xticklabels(top5, rotation=30, ha="right", fontsize=9)
ax2.set_title("Score Distribution (Top 5 Subjects)", fontsize=13, fontweight="bold", pad=10)
ax2.set_ylabel("Percentage (%)")
ax2.grid(True, axis="y")

fig.tight_layout()
fig.savefig(os.path.join(OUT, "02_subject_performance.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 3: Student Comparison Chart (Radar / Spider)
# ================================================================
print("3/8  Student Comparison Radar ...")
# Pick 4 students from different buckets
sample_ids = []
for bucket in ["high","mid","low","at_risk"]:
    sid = students[students["performance_bucket"] == bucket].iloc[0]["student_id"]
    sample_ids.append(sid)

subjects_radar = ["English","Hindi","Mathematics","Science","Social Studies","Computer Science"]
fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

angles = np.linspace(0, 2 * np.pi, len(subjects_radar), endpoint=False).tolist()
angles += angles[:1]

colors_radar = [ACCENT1, ACCENT5, ACCENT3, ACCENT2]
labels_radar = []

for idx, sid in enumerate(sample_ids):
    stu_data = academic[(academic["student_id"] == sid) & (academic["subject"].isin(subjects_radar))]
    stu_avg = stu_data.groupby("subject")["percentage"].mean()
    vals = [stu_avg.get(s, 0) for s in subjects_radar]
    vals += vals[:1]
    name = students[students["student_id"] == sid].iloc[0]
    label = f"{name['first_name']} {name['last_name']} ({name['performance_bucket']})"
    labels_radar.append(label)
    ax.plot(angles, vals, color=colors_radar[idx], linewidth=2.2, label=label)
    ax.fill(angles, vals, color=colors_radar[idx], alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(subjects_radar, fontsize=10)
ax.set_ylim(0, 100)
ax.set_title("Student Performance Comparison\n(Radar Chart - 4 Students)", fontsize=14, fontweight="bold", pad=25)
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID, fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "03_student_comparison_radar.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 4: Dropout Risk Simulation (Monte Carlo)
# ================================================================
print("4/8  Dropout Risk Simulation ...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Left: Monte Carlo simulation of dropout counts
np.random.seed(42)
n_simulations = 1000
risk_scores = students[students["is_active"] == 1]["dropout_risk_score"].values
dropout_counts = []
for _ in range(n_simulations):
    random_draws = np.random.random(len(risk_scores))
    dropouts = (random_draws < risk_scores).sum()
    dropout_counts.append(dropouts)

ax1.hist(dropout_counts, bins=40, color=ACCENT2, alpha=0.75, edgecolor=BG)
mean_d = np.mean(dropout_counts)
ax1.axvline(mean_d, color=ACCENT3, linewidth=2.5, linestyle="--", label=f"Mean = {mean_d:.0f} students")
ax1.axvline(np.percentile(dropout_counts, 95), color=ACCENT6, linewidth=2, linestyle=":", label=f"95th pctl = {np.percentile(dropout_counts, 95):.0f}")
ax1.set_title("Monte Carlo Dropout Simulation\n(1000 runs)", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Predicted Dropout Count")
ax1.set_ylabel("Frequency")
ax1.legend(framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID)
ax1.grid(True, axis="y")

# Right: Risk distribution by category
risk_by_cat = students.groupby("category")["dropout_risk_score"].agg(["mean","std"]).sort_values("mean", ascending=True)
bars = ax2.barh(risk_by_cat.index, risk_by_cat["mean"], xerr=risk_by_cat["std"],
                color=[ACCENT1, ACCENT5, ACCENT4, ACCENT3, ACCENT2][:len(risk_by_cat)],
                edgecolor="none", capsize=5, error_kw={"ecolor": TEXT, "alpha": 0.6})
ax2.set_title("Avg Dropout Risk by Category", fontsize=13, fontweight="bold", pad=10)
ax2.set_xlabel("Risk Score (0 = safe, 1 = high risk)")
ax2.grid(True, axis="x")

fig.tight_layout()
fig.savefig(os.path.join(OUT, "04_dropout_simulation.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 5: IoT Sensor Simulation - Classroom Utilization Heatmap
# ================================================================
print("5/8  IoT Classroom Utilization Heatmap ...")
fig, ax = plt.subplots(figsize=(14, 8))

sensors["hour"] = sensors["time"].str.split(":").str[0].astype(int)
pivot_heat = sensors.groupby(["room_id","hour"])["utilization_pct"].mean().unstack()
# Show top 20 rooms
top_rooms = sensors.groupby("room_id")["utilization_pct"].mean().nlargest(20).index
pivot_heat = pivot_heat.loc[pivot_heat.index.isin(top_rooms)]

cmap = LinearSegmentedColormap.from_list("custom", ["#0f1117","#1a4a5e","#00d4aa","#ffd93d","#ff6b6b"])
im = ax.imshow(pivot_heat.values, aspect="auto", cmap=cmap, interpolation="nearest")
ax.set_yticks(range(len(pivot_heat.index)))
ax.set_yticklabels(pivot_heat.index, fontsize=9)
ax.set_xticks(range(len(pivot_heat.columns)))
ax.set_xticklabels([f"{h}:00" for h in pivot_heat.columns], fontsize=9)
ax.set_title("Classroom Utilization Heatmap (IoT Sensor Data)\nTop 20 Rooms by Avg Utilization", fontsize=14, fontweight="bold", pad=15)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Room ID")
cbar = fig.colorbar(im, ax=ax, pad=0.02)
cbar.set_label("Utilization %", fontsize=11)

fig.tight_layout()
fig.savefig(os.path.join(OUT, "05_iot_classroom_heatmap.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 6: Predictive Analytics - Performance Forecast
# ================================================================
print("6/8  Performance Prediction Simulation ...")
fig, ax = plt.subplots(figsize=(14, 6))

# Simulate performance trajectory over 6 exam types
exam_order = ["Unit Test 1","Unit Test 2","Mid Term","Unit Test 3","Unit Test 4","Final Exam"]
existing_exams = academic["exam_type"].unique().tolist()

np.random.seed(123)
for bucket, color, ls in [("high", ACCENT1, "-"), ("mid", ACCENT5, "-"), ("low", ACCENT3, "-"), ("at_risk", ACCENT2, "-")]:
    bucket_students = students[students["performance_bucket"] == bucket]["student_id"]
    bucket_scores = academic[academic["student_id"].isin(bucket_students)]

    actual_means = []
    for ex in exam_order:
        subset = bucket_scores[bucket_scores["exam_type"] == ex]
        if len(subset) > 0:
            actual_means.append(subset["percentage"].mean())
        else:
            actual_means.append(None)

    # Fill actual data points
    actual_x = [i for i, v in enumerate(actual_means) if v is not None]
    actual_y = [v for v in actual_means if v is not None]

    # Predict remaining exams using simple trend
    if len(actual_y) >= 2:
        slope = (actual_y[-1] - actual_y[0]) / max(len(actual_y)-1, 1)
    else:
        slope = 0

    predicted_x = list(range(len(exam_order)))
    predicted_y = []
    last_val = actual_y[-1] if actual_y else 50
    for i in range(len(exam_order)):
        if i < len(actual_x) and i in actual_x:
            predicted_y.append(actual_means[i])
        else:
            last_val = last_val + slope + np.random.normal(0, 2)
            predicted_y.append(max(0, min(100, last_val)))

    # Plot actual
    ax.plot(actual_x, actual_y, color=color, linewidth=2.5, marker="o", markersize=7, label=f"{bucket} (actual)")
    # Plot predicted (dashed extension)
    pred_start = max(actual_x) if actual_x else 0
    pred_indices = [i for i in range(pred_start, len(exam_order))]
    pred_values = [predicted_y[i] for i in pred_indices]
    ax.plot(pred_indices, pred_values, color=color, linewidth=2, linestyle="--", alpha=0.6, marker="D", markersize=5)
    # Confidence band
    for i in pred_indices[1:]:
        spread = (i - pred_start) * 3
        ax.fill_between([i-0.3, i+0.3], predicted_y[i]-spread, predicted_y[i]+spread, color=color, alpha=0.08)

ax.axvline(x=max(actual_x) if actual_x else 1, color=TEXT, linestyle=":", alpha=0.5, linewidth=1.5)
ax.text(max(actual_x)+0.1 if actual_x else 1.1, 95, "  Prediction -->", color=TEXT, fontsize=10, alpha=0.7)

ax.set_xticks(range(len(exam_order)))
ax.set_xticklabels(exam_order, rotation=20, ha="right", fontsize=10)
ax.set_title("AI Performance Prediction - Exam Trajectory by Student Bucket", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("Average Percentage (%)")
ax.set_ylim(0, 105)
ax.legend(loc="lower left", framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID, fontsize=9, ncol=2)
ax.grid(True, axis="y")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "06_performance_prediction.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 7: Resource Optimization Simulation
# ================================================================
print("7/8  Resource Optimization Simulation ...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Left: Teacher workload distribution
tt_load = timetable.groupby("teacher_id").size().reset_index(name="periods_per_week")
tt_load = tt_load.merge(teachers[["teacher_id","first_name","last_name","designation"]], on="teacher_id")
tt_load["name"] = tt_load["first_name"] + " " + tt_load["last_name"]
tt_load = tt_load.sort_values("periods_per_week", ascending=True).tail(20)

colors_load = [ACCENT2 if p > 35 else ACCENT3 if p > 25 else ACCENT1 for p in tt_load["periods_per_week"]]
ax1.barh(tt_load["name"], tt_load["periods_per_week"], color=colors_load, edgecolor="none")
ax1.axvline(x=30, color=ACCENT3, linestyle="--", linewidth=1.5, alpha=0.8, label="Recommended Max (30)")
ax1.axvline(x=35, color=ACCENT2, linestyle="--", linewidth=1.5, alpha=0.8, label="Overload Threshold (35)")
ax1.set_title("Teacher Workload Analysis\n(Top 20 by Periods/Week)", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Periods per Week")
ax1.legend(framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID, fontsize=9)
ax1.grid(True, axis="x")

# Right: Room occupancy simulation - before vs after optimization
rooms_util = sensors.groupby("room_id")["utilization_pct"].mean().sort_values(ascending=False).head(15)
np.random.seed(77)
optimized = rooms_util.values * np.random.uniform(0.85, 1.15, len(rooms_util))
optimized = np.clip(optimized, 10, 95)
# Redistribute: push low-util rooms up, high-util down
optimized = optimized * 0.7 + 45 * 0.3  # converge toward 45%

x_pos = np.arange(len(rooms_util))
w = 0.35
ax2.bar(x_pos - w/2, rooms_util.values, w, color=ACCENT2, alpha=0.8, label="Current", edgecolor="none")
ax2.bar(x_pos + w/2, optimized, w, color=ACCENT1, alpha=0.8, label="After AI Optimization", edgecolor="none")
ax2.set_xticks(x_pos)
ax2.set_xticklabels(rooms_util.index, rotation=45, ha="right", fontsize=8)
ax2.set_title("Room Utilization: Current vs Optimized", fontsize=13, fontweight="bold", pad=10)
ax2.set_ylabel("Avg Utilization %")
ax2.legend(framealpha=0.8, facecolor=CARD_BG, edgecolor=GRID)
ax2.grid(True, axis="y")

fig.tight_layout()
fig.savefig(os.path.join(OUT, "07_resource_optimization.png"), dpi=180, bbox_inches="tight")
plt.close()

# ================================================================
# GRAPH 8: REAL-TIME ADMIN DASHBOARD (Industry 4.0 Panel)
# ================================================================
print("8/8  Admin Dashboard (Industry 4.0) ...")
fig = plt.figure(figsize=(20, 12))
fig.suptitle("SMART SCHOOL ERP - REAL-TIME ADMIN DASHBOARD", fontsize=20, fontweight="bold", color=ACCENT1, y=0.98)
fig.text(0.5, 0.955, "Industry 4.0 | IoT + AI + Predictive Analytics | Live Monitoring", ha="center", fontsize=11, color="#888", style="italic")

gs = gridspec.GridSpec(3, 4, hspace=0.4, wspace=0.35, top=0.92, bottom=0.06, left=0.06, right=0.96)

# ---- KPI Cards (Row 0) ----
kpis = [
    ("Total Students", f"{len(students[students['is_active']==1]):,}", ACCENT1, "+3.2% vs last year"),
    ("Avg Attendance", f"{attendance['status'].isin(['Present','Late']).mean()*100:.1f}%", ACCENT5, "Above 85% threshold"),
    ("At-Risk Students", f"{len(students[students['performance_bucket']=='at_risk'])}", ACCENT2, "Needs intervention"),
    ("Avg Score", f"{academic['percentage'].mean():.1f}%", ACCENT3, "Across all exams"),
]

for i, (title, value, color, sub) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    # Card background
    rect = FancyBboxPatch((0.02, 0.05), 0.96, 0.9, boxstyle="round,pad=0.05", facecolor=CARD_BG, edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.72, value, ha="center", va="center", fontsize=28, fontweight="bold", color=color)
    ax.text(0.5, 0.42, title, ha="center", va="center", fontsize=12, color=TEXT)
    ax.text(0.5, 0.2, sub, ha="center", va="center", fontsize=9, color="#888")

# ---- Row 1 Left: Attendance by Class (bar) ----
ax_att = fig.add_subplot(gs[1, :2])
class_present = attendance.groupby("class").apply(lambda x: (x["status"].isin(["Present","Late"])).mean() * 100).sort_index()
bars = ax_att.bar(class_present.index, class_present.values,
                  color=[ACCENT1 if v >= 85 else ACCENT3 if v >= 75 else ACCENT2 for v in class_present.values],
                  edgecolor="none", width=0.7)
ax_att.axhline(85, color=ACCENT2, linestyle=":", alpha=0.7)
ax_att.set_title("Attendance Rate by Class", fontsize=12, fontweight="bold")
ax_att.set_xlabel("Class"); ax_att.set_ylabel("Attendance %")
ax_att.set_ylim(70, 100)
ax_att.set_xticks(range(1, 13))
ax_att.grid(True, axis="y")

# ---- Row 1 Right: Performance Distribution (donut) ----
ax_donut = fig.add_subplot(gs[1, 2:])
bucket_counts = students[students["is_active"]==1]["performance_bucket"].value_counts()
bucket_order = ["high","mid","low","at_risk"]
sizes = [bucket_counts.get(b, 0) for b in bucket_order]
colors_donut = [ACCENT1, ACCENT5, ACCENT3, ACCENT2]
wedges, texts, autotexts = ax_donut.pie(sizes, labels=["High","Mid","Low","At-Risk"],
    colors=colors_donut, autopct="%1.1f%%", startangle=90, pctdistance=0.78,
    wedgeprops=dict(width=0.45, edgecolor=BG, linewidth=2))
for t in autotexts: t.set_fontsize(10); t.set_color(TEXT)
for t in texts: t.set_fontsize(10)
ax_donut.set_title("Student Performance Distribution", fontsize=12, fontweight="bold")

# ---- Row 2 Left: IoT - Hourly Occupancy Trend ----
ax_iot = fig.add_subplot(gs[2, :2])
hourly = sensors.groupby("hour")["occupancy_count"].mean()
ax_iot.fill_between(hourly.index, hourly.values, alpha=0.3, color=ACCENT4)
ax_iot.plot(hourly.index, hourly.values, color=ACCENT4, linewidth=2.5, marker="o", markersize=6)
# Add peak annotation
peak_hour = hourly.idxmax()
ax_iot.annotate(f"Peak: {hourly.max():.0f} students\nat {peak_hour}:00",
    xy=(peak_hour, hourly.max()), xytext=(peak_hour+1.5, hourly.max()+3),
    arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=1.5), fontsize=10, color=ACCENT3, fontweight="bold")
ax_iot.set_title("IoT: Avg Classroom Occupancy by Hour", fontsize=12, fontweight="bold")
ax_iot.set_xlabel("Hour of Day"); ax_iot.set_ylabel("Avg Occupancy")
ax_iot.set_xticks(range(7, 16))
ax_iot.set_xticklabels([f"{h}:00" for h in range(7, 16)])
ax_iot.grid(True, axis="y")

# ---- Row 2 Right: Alerts Panel ----
ax_alerts = fig.add_subplot(gs[2, 2:])
ax_alerts.set_xlim(0, 1); ax_alerts.set_ylim(0, 1)
ax_alerts.axis("off")
rect = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.03", facecolor=CARD_BG, edgecolor=ACCENT6, linewidth=2)
ax_alerts.add_patch(rect)
ax_alerts.text(0.5, 0.92, "AUTOMATED ALERTS & RECOMMENDATIONS", ha="center", fontsize=12, fontweight="bold", color=ACCENT6)

alerts = [
    (ACCENT2, "CRITICAL", f"{len(students[students['dropout_risk_score']>0.7])} students with dropout risk > 70%"),
    (ACCENT2, "CRITICAL", f"Class 11-D attendance dropped below 75% this week"),
    (ACCENT3, "WARNING", f"Room-G05 AC running with 0 occupancy (energy waste)"),
    (ACCENT3, "WARNING", f"Teacher TCH0012 exceeds 40 periods/week (burnout risk)"),
    (ACCENT5, "INFO", f"Mid-Term avg score improved by 4.2% vs Unit Test 2"),
    (ACCENT1, "ACTION", f"Schedule parent meeting for 23 at-risk students"),
    (ACCENT1, "ACTION", f"Reassign 3 underutilized classrooms to reduce energy cost"),
]

y_pos = 0.82
for color, level, text in alerts:
    ax_alerts.plot(0.06, y_pos, "s", color=color, markersize=8)
    ax_alerts.text(0.1, y_pos, f"[{level}]", fontsize=9, fontweight="bold", color=color, va="center")
    ax_alerts.text(0.25, y_pos, text, fontsize=9, color=TEXT, va="center")
    y_pos -= 0.11

fig.savefig(os.path.join(OUT, "08_admin_dashboard.png"), dpi=180, bbox_inches="tight")
plt.close()

# ---------- Done ----------
print("\nAll 8 graphs saved to ./graphs/ folder:")
for f in sorted(os.listdir(OUT)):
    size_kb = os.path.getsize(os.path.join(OUT, f)) / 1024
    print(f"   {f:45s}  ({size_kb:.0f} KB)")
