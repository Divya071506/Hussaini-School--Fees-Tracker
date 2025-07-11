import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="Student Fee Tracker", layout="centered")

# Database setup
conn = sqlite3.connect("students.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_number TEXT PRIMARY KEY,
        name TEXT,
        class TEXT,
        type TEXT,
        fee_amount REAL,
        status TEXT,
        contact TEXT,
        added_on TEXT,
        last_updated TEXT
    )
''')
conn.commit()

# Title and Tabs
st.markdown("<h3 style='text-align:center;'>📘 Student Fee Tracker</h3>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["➕ Add Student", "📊 Fee Status"])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("Add New Student")
    with st.form("student_form"):
        col1, col2 = st.columns(2)
        with col1:
            roll = st.text_input("Roll Number")
            name = st.text_input("Student Name")
            fee_amount = st.number_input("Fee Amount", min_value=0.0)
        with col2:
            class_name = st.selectbox("Class", [f"Class {i} - {s}" for i in range(1, 11) for s in ["A", "B", "C"]])
            student_type = st.selectbox("Type", ["New", "Old"])
            status = st.selectbox("Fee Status", ["Paid", "Unpaid"])
        contact = st.text_input("Contact Number")
        submitted = st.form_submit_button("Add Student")

        if submitted:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            try:
                c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                    roll, name, class_name, student_type, fee_amount, status, contact, now, now
                ))
                conn.commit()
                st.success("✅ Student added successfully!")
            except sqlite3.IntegrityError:
                st.error("⚠️ Roll number already exists!")

# ---------- TAB 2 ----------
with tab2:
    st.subheader("🔍 Search Students")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_class = st.selectbox("Select Class", ["-- Select --"] + [f"Class {i} - {s}" for i in range(1, 11) for s in ["A", "B", "C"]])
    with col2:
        student_name = st.text_input("Student Name")
    with col3:
        status_filter = st.selectbox("Status", ["All", "Paid", "Unpaid"])

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if selected_class != "-- Select --":
        query += " AND class = ?"
        params.append(selected_class)
    if student_name.strip() != "":
        query += " AND name LIKE ?"
        params.append(f"%{student_name}%")
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if selected_class != "-- Select --" or student_name.strip() != "" or status_filter != "All":
        c.execute(query, params)
        results = c.fetchall()

        if results:
            df = pd.DataFrame(results, columns=[
                "Roll No", "Name", "Class", "Type", "Fee Amount", "Status", "Contact", "Added On", "Last Updated"
            ])

            # Download as Excel (browser)
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Excel", data=csv_data, file_name="fee_status.csv", mime="text/csv")

            st.markdown("---")
            st.subheader("📋 Fee Details")

            for i, row in df.iterrows():
                with st.expander(f"{row['Name']} ({row['Roll No']}) – {row['Class']}"):
                    st.write(f"**Type:** {row['Type']}")
                    st.write(f"**Contact:** {row['Contact']}")
                    st.write(f"**Added On:** {row['Added On']}")
                    st.write(f"**Last Updated:** {row['Last Updated']}")

                    with st.form(f"edit_form_{row['Roll No']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_amount = st.number_input("Fee Amount", value=float(row["Fee Amount"]), key=f"amt_{row['Roll No']}")
                        with col2:
                            new_status = st.selectbox("Status", ["Paid", "Unpaid"], index=0 if row["Status"] == "Paid" else 1, key=f"status_{row['Roll No']}")
                        if st.form_submit_button("💾 Save Changes"):
                            updated_on = datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("UPDATE students SET fee_amount = ?, status = ?, last_updated = ? WHERE roll_number = ?",
                                      (new_amount, new_status, updated_on, row["Roll No"]))
                            conn.commit()
                            st.success("✅ Updated!")
                            st.rerun()
        else:
            st.info("🙁 No matching students found.")
    else:
        st.warning("🔎 Please apply at least one filter to view results.")
