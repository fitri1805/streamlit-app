import streamlit as st
import pandas as pd
import numpy as np
import os
import mysql.connector
import time 
from datetime import datetime, date
from Login import apply_sidebar_theme

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123",       
        database="gamifiedqc"
    )

# Function to check if submission is allowed based on current date
#COMMENTED OUT FOR A WHILE 
#def is_submission_allowed():
#    today = date.today()
#    return 1 <= today.day <= 14

# Function to count submissions for the current month
def count_current_month_submissions(lab):
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT COUNT(*) FROM submissions 
        WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s
    """
    cursor.execute(query, (lab, current_month, current_year))
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return count

# Function to check if all required parameters are submitted
def check_required_parameters(lab):
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    conn = get_connection()
    query = """
        SELECT Parameter, Level FROM submissions 
        WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s
    """
    submitted_df = pd.read_sql(query, conn, params=[lab, current_month, current_year])
    conn.close()
    
    # Define all required parameters
    all_parameters = sorted([
        "Albumin", "ALT", "AST", "Bilirubin (Total)", "Cholesterol",
        "Creatinine", "Direct Bilirubin", "GGT", "Glucose", "HDL Cholesterol",
        "LDL Cholesterol", "Potassium", "Protein (Total)", "Sodium",
        "Triglycerides", "Urea", "Uric Acid"
    ])
    
    # Check if all parameters have both levels submitted
    missing_params = []
    for param in all_parameters:
        param_data = submitted_df[submitted_df['Parameter'] == param]
        if len(param_data) == 0:
            missing_params.append(f"{param} (both levels)")
        elif 'L1' not in param_data['Level'].values:
            missing_params.append(f"{param} (L1)")
        elif 'L2' not in param_data['Level'].values:
            missing_params.append(f"{param} (L2)")
    
    return missing_params

# Function to get all submissions for a lab (for filter)
def get_all_submissions(lab):
    conn = get_connection()
    query = """
        SELECT * FROM submissions 
        WHERE Lab = %s
        ORDER BY created_at DESC
    """
    all_df = pd.read_sql(query, conn, params=[lab])
    conn.close()
    return all_df

# Function to get submissions for CSV export
def get_submissions_for_csv(lab, month=None, year=None):
    conn = get_connection()
    
    if month and year:
        query = """
            SELECT * FROM submissions 
            WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s
            ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn, params=[lab, month, year])
    else:
        query = """
            SELECT * FROM submissions 
            WHERE Lab = %s
            ORDER BY created_at DESC
        """
        df = pd.read_sql(query, conn, params=[lab])
    
    conn.close()
    return df

DATA_DIR = "data"

def run():
    apply_sidebar_theme()
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stDataFrame {
            font-size: 12px;
        }
        .stButton > button {
            width: 100%;
            margin: 5px 0;
        }
        .stSelectbox, .stTextInput {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📋 LLKK Direct Data Entry")

    if "logged_in_lab" not in st.session_state:
        st.warning("Please log in from the sidebar to access data entry.")
        st.stop()

    lab = st.session_state["logged_in_lab"]
    
    # Check if submission is allowed based on date (COMMENT OUT FOR A WHILE)
    #if not is_submission_allowed():
    #    st.error("🚫 Data submission is only allowed from the 1st to the 14th of each month.")
    #    st.info("The battle begins on the 15th. Please come back next month for data submission.")
    #    st.stop()

    # Show submission status in a cleaner way
    submission_count = count_current_month_submissions(lab)
    missing_params = check_required_parameters(lab)
    
    # Create a status indicator with expandable details
    status_col1, status_col2 = st.columns([1, 3])
    with status_col1:
        if submission_count == 34 and not missing_params:
            st.success(f"✅ Ready for battle! ({submission_count}/34)")
        else:
            st.warning(f"⚠️ Incomplete ({submission_count}/34)")
    
    with status_col2:
        #today = date.today()
        #days_left = 14 - today.day
        #st.info(f"📅 Submission window: 1st-14th ({days_left} days left)")
        st.info("submission is open anytime for now")
    
    # Expandable section for missing parameters
    if missing_params:
        with st.expander("Show missing parameters", expanded=False):
            st.warning("⚠️ Missing submissions for:")
            for param in missing_params:
                st.write(f"- {param}")

    # Get all submissions for this lab (for filter)
    all_submissions_df = get_all_submissions(lab)
    
    # Add filter options for viewing data
    st.subheader("📂 Previously Submitted Data")
    
    # Create filter options
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        view_option = st.radio("Filter by:", 
                              ["Current month", "All time", "Specific month"])
    
    # Filter data based on selection
    if view_option == "Current month":
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        conn = get_connection()
        query = """
            SELECT * FROM submissions 
            WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s
            ORDER BY created_at DESC
        """
        view_df = pd.read_sql(query, conn, params=[lab, current_month, current_year])
        conn.close()
        
    elif view_option == "All time":
        view_df = all_submissions_df
        
    else:  # Specific month
        if not all_submissions_df.empty:
            all_submissions_df['created_at'] = pd.to_datetime(all_submissions_df['created_at'])
            available_months = sorted(all_submissions_df['created_at'].dt.strftime('%Y-%m').unique(), reverse=True)
            
            selected_month = st.selectbox("Select month:", available_months)
            year, month = selected_month.split('-')
            
            conn = get_connection()
            query = """
                SELECT * FROM submissions 
                WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s
                ORDER BY created_at DESC
            """
            view_df = pd.read_sql(query, conn, params=[lab, month, year])
            conn.close()
        else:
            view_df = pd.DataFrame()

    # Initialize edit mode if not set
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    # Create columns to position the buttons at top right of table
    col1, col2, col3 = st.columns([6, 1, 1])  

    #with col1:
        #st.markdown(f"**Displaying: {view_option}**")

    with col2:
        if st.button("✏️ Edit", key="edit_records_button", use_container_width=True):  
            st.session_state.edit_mode = True
            st.session_state.edit_lab = lab
            st.rerun()

    with col3:
        if st.button("🗑️ Delete", key="delete_records_button", use_container_width=True):  
            st.session_state.delete_mode = True
            st.session_state.delete_lab = lab
            st.rerun()

    st.dataframe(view_df)

    # Add delete mode interface (similar to edit mode but simpler)
    if st.session_state.get("delete_mode", False):
        # Add a button to exit delete mode
        if st.button("← Back to Data Entry"):
            st.session_state.delete_mode = False
            st.rerun()
        
        # Fetch all parameters and levels for this lab in current month
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        conn = get_connection()
        query = """
            SELECT DISTINCT Parameter, Level FROM submissions 
            WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s 
            ORDER BY Parameter, Level
        """
        params_df = pd.read_sql(query, conn, params=[lab, current_month, current_year])
        conn.close()
        
        if params_df.empty:
            st.error("No records found for deletion.")
        else:
            # Select parameter to delete
            parameters = sorted(params_df['Parameter'].unique())
            selected_param = st.selectbox("Select Parameter", parameters, key="delete_param")
            
            # Select level based on chosen parameter
            available_levels = params_df[params_df['Parameter'] == selected_param]['Level'].unique()
            selected_level = st.selectbox("Select Level", available_levels, key="delete_level")
            
            # Show confirmation
            st.warning(f" ⚠️ You are about to delete ALL records for: {selected_param} - {selected_level} This action cannot be undone!")
            
            # Get count of records that will be deleted
            conn = get_connection()
            query = """
                SELECT COUNT(*) as count FROM submissions 
                WHERE Lab = %s AND Parameter = %s AND Level = %s 
                AND MONTH(created_at) = %s AND YEAR(created_at) = %s
            """
            count_df = pd.read_sql(query, conn, params=[lab, selected_param, selected_level, current_month, current_year])
            record_count = count_df.iloc[0]['count']
            conn.close()
            
            st.write(f"Number of records that will be deleted: **{record_count}**")
            
            # Confirmation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", type="primary",  use_container_width=True):
                    # Delete records from database
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        DELETE FROM submissions 
                        WHERE Lab = %s AND Parameter = %s AND Level = %s 
                        AND MONTH(created_at) = %s AND YEAR(created_at) = %s
                        """,
                        (lab, selected_param, selected_level, current_month, current_year)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success(f"✅ Deleted {record_count} records for {selected_param} - {selected_level}")
                    
                    countdown_placeholder = st.empty()
                    for i in range(5, 0, -1):
                        countdown_placeholder.info(f"Returning to data entry in {i} seconds...")
                        time.sleep(1)
                    
                    # Clear delete mode and refresh
                    st.session_state.delete_mode = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel Delete", use_container_width=True):
                    st.session_state.delete_mode = False
                    st.rerun()

    # If edit mode is activated, show the edit interface
    if st.session_state.get("edit_mode", False):
        # Fetch all parameters and levels for this lab in current month
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        conn = get_connection()
        query = """
            SELECT DISTINCT Parameter, Level FROM submissions 
            WHERE Lab = %s AND MONTH(created_at) = %s AND YEAR(created_at) = %s 
            ORDER BY Parameter, Level
        """
        params_df = pd.read_sql(query, conn, params=[lab, current_month, current_year])
        conn.close()
        
        if params_df.empty:
            st.error("No records found for editing.")
        else:
            # Step 1: Select parameter
            parameters = sorted(params_df['Parameter'].unique())
            selected_param = st.selectbox("Select Parameter", parameters, key="edit_param")
            
            # Step 2: Select level based on chosen parameter
            available_levels = params_df[params_df['Parameter'] == selected_param]['Level'].unique()
            selected_level = st.selectbox("Select Level", available_levels, key="edit_level")
            
            # Step 3: Fetch all records for this parameter and level in current month
            conn = get_connection()
            query = """
                SELECT * FROM submissions 
                WHERE Lab = %s AND Parameter = %s AND Level = %s 
                AND MONTH(created_at) = %s AND YEAR(created_at) = %s
            """
            records_df = pd.read_sql(query, conn, params=[lab, selected_param, selected_level, current_month, current_year])
            conn.close()
            
            if records_df.empty:
                st.error("No records found for the selected parameter and level.")
            else:
                # Display the records and allow editing
                st.subheader(f"Editing {selected_param} - {selected_level}")
                
                # Create a form for editing
                with st.form("edit_form"):
                    updated_data = []
                    
                    # Get all available parameters and levels for the dropdowns
                    all_parameters = sorted([
                    "Albumin", "ALT", "AST", "Bilirubin (Total)", "Cholesterol",
                    "Creatinine", "Direct Bilirubin", "GGT", "Glucose", "HDL Cholesterol",
                    "LDL Cholesterol", "Potassium", "Protein (Total)", "Sodium",
                    "Triglycerides", "Urea", "Uric Acid"
                    ])
                    all_levels = ["L1", "L2"]
                
                    for idx, record in records_df.iterrows():
                        st.markdown(f"**Record {idx+1}**")

                         # Allow editing Parameter
                        new_param = st.selectbox(
                            "Parameter", 
                            all_parameters,
                            index=all_parameters.index(record['Parameter']),
                            key=f"param_{record['id']}"
                        )
                    
                        # Allow editing Level
                        new_level = st.selectbox(
                            "Level", 
                            all_levels,
                            index=all_levels.index(record['Level']),
                            key=f"level_{record['id']}"
                        )
                        
                        # Get month value
                        month = st.selectbox(
                            "Month", 
                            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                            index=["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(record['Month']),
                            key=f"month_{record['id']}"
                        )
                        
                        cv = st.number_input(
                            "CV(%)", 
                            min_value=0.0, 
                            max_value=100.0, 
                            value=float(record['CV(%)']),
                            key=f"cv_{record['id']}"
                        )
                        
                        n_qc = st.number_input(
                            "n(QC)", 
                            min_value=0, 
                            max_value=100, 
                            value=int(record['n(QC)']),
                            key=f"nqc_{record['id']}"
                        )
                        
                        wd = st.number_input(
                            "Working_Days", 
                            min_value=1, 
                            max_value=31, 
                            value=int(record['Working_Days']),
                            key=f"wd_{record['id']}"
                        )
                        
                        ratio = round(n_qc / wd, 2) if n_qc > 0 and wd > 0 else 0.0
                        st.number_input("Ratio", value=ratio, disabled=True, key=f"ratio_{record['id']}")
                        
                        updated_data.append({
                            "id": record['id'],
                            "parameter": new_param,
                            "level": new_level,
                            "month": month,
                            "cv": cv,
                            "n_qc": n_qc,
                            "wd": wd,
                            "ratio": ratio
                        })
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("Update Records")
                    with col2:
                        cancel_edit = st.form_submit_button("Cancel Edit")
                    
                    if update_submitted:
                        # Update records in database
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        for data in updated_data:
                            cursor.execute("""
                                UPDATE submissions 
                                SET Parameter = %s, Level = %s, Month = %s, 
                                    `CV(%)` = %s, `n(QC)` = %s, 
                                    `Working_Days` = %s, Ratio = %s
                                WHERE id = %s
                            """, (
                                data['parameter'], data['level'], data['month'], 
                                data['cv'], data['n_qc'], data['wd'], data['ratio'], 
                                data['id']
                            ))

                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        st.success("✅ Records updated successfully!")
                        # Clear edit mode
                        st.session_state.edit_mode = False
                        
                        # Add a countdown timer before refreshing
                        countdown_placeholder = st.empty()
                        for i in range(5, 0, -1):
                            countdown_placeholder.info(f"Returning to data entry in {i} seconds...")
                            time.sleep(1)
                        
                        st.rerun()
                    
                    if cancel_edit:
                        # Clear edit mode
                        st.session_state.edit_mode = False
                        st.rerun()

    # Only show data input section if not in edit mode
    if not st.session_state.edit_mode:
        
        # Data input section
        parameters = sorted([
            "Albumin", "ALT", "AST", "Bilirubin (Total)", "Cholesterol",
            "Creatinine", "Direct Bilirubin", "GGT", "Glucose", "HDL Cholesterol",
            "LDL Cholesterol", "Potassium", "Protein (Total)", "Sodium",
            "Triglycerides", "Urea", "Uric Acid"
        ])
        levels = ["L1", "L2"]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        num_rows = st.number_input("🔢 How many entries to input?", min_value=1, max_value=50, value=5, step=1)

        st.subheader(f"📝 Enter Data for: :green[{lab}]")

        input_data = []
        for i in range(num_rows):
            cols = st.columns(7)
            parameter = cols[0].selectbox("Parameter", parameters, key=f"param_{i}")
            level = cols[1].selectbox("Level", levels, key=f"level_{i}")
            month = cols[2].selectbox("Month", months, key=f"month_{i}")
            cv = cols[3].number_input("CV(%)", min_value=0.0, max_value=100.0, key=f"cv_{i}")
            n_qc = cols[4].number_input("n(QC)", min_value=0, max_value=100, key=f"n_{i}")
            wd = cols[5].number_input("Working_Days", min_value=1, max_value=31, key=f"wd_{i}")
            ratio = round(n_qc / wd, 2) if n_qc > 0 and wd > 0 else 0.0
            cols[6].number_input("Ratio", value=ratio, disabled=True, key=f"ratio_{i}")

            input_data.append({
                "Lab": lab,
                "Parameter": parameter,
                "Level": level,
                "Month": month,
                "CV(%)": cv,
                "n(QC)": n_qc,
                "Working_Days": wd,
                "Ratio": ratio
            })

        df = pd.DataFrame(input_data)
        df = df[(df["CV(%)"] > 0) & (df["n(QC)"] > 0) & (df["Working_Days"] > 0)]

        st.subheader("📊 Preview of Valid Entries")
        st.dataframe(df)
        
        # Download button for submitted data
        if not view_df.empty:
            csv_data = view_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Submitted Data",
                data=csv_data,
                file_name=f"{lab}_llkk_data_entry.csv",
                mime="text/csv",
                key="download_submitted_data"
            )
        else:
            st.info("No submitted data available to download")

        # Combined button to save data and submit to battle
        if st.button("💾 Submit to battle"):
            if not df.empty:
                errors = []
                grouped = df.groupby("Parameter")["Level"].apply(list).to_dict()

                # Validation: Each parameter must have L2 in its entries
                for param, levels in grouped.items():
                    if "L2" not in levels:
                        errors.append(param)

                if errors:
                    st.error(f"⚠️ For these parameters you must include Level 2: {', '.join(errors)}")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    saved_rows = 0

                    for _, row in df.iterrows():
                        # Insert only valid entries
                        cursor.execute("""
                            INSERT INTO submissions 
                            (Lab, Parameter, Level, Month, `CV(%)`, `n(QC)`, `Working_Days`, Ratio)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row["Lab"], row["Parameter"], row["Level"], row["Month"],
                            row["CV(%)"], row["n(QC)"], row["Working_Days"], row["Ratio"]
                        ))
                        saved_rows += 1

                    conn.commit()
                    cursor.close()
                    conn.close()

                    if saved_rows > 0:
                        st.success(f"✅ Data saved and submitted into battlefield successfully for {lab}!")
                        
                        # Update submission count
                        submission_count = count_current_month_submissions(lab)
                        
                        # Check if all required parameters are submitted
                        missing_params = check_required_parameters(lab)
                        if missing_params:
                            st.warning("⚠️ Still missing submissions for:")
                            for param in missing_params:
                                st.write(f"- {param}")
                        else:
                            st.success("✅ All required test submitted! You're ready for battle!")

                        if "llkk_data" not in st.session_state:
                            st.session_state["llkk_data"] = df
                        else:
                            st.session_state["llkk_data"] = pd.concat(
                                [st.session_state["llkk_data"], df], ignore_index=True
                            )
                            
                        # Refresh the page to show updated data
                        st.rerun()
            else:
                st.warning("⚠️ Please complete all fields before submitting.")

if __name__ == "__main__":
    run()