import pandas as pd
from datetime import datetime
import streamlit as st

def export_to_excel(df):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"fee_report_{now}.xlsx"
    df.to_excel(filename, index=False)

    with open(filename, "rb") as f:
        st.download_button(label="Download Excel",
                           data=f,
                           file_name=filename,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
