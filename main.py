import streamlit as st
import logging

from src.styling import render_header
from src.charts import display_results 

def main():

    logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Set page config
    st.set_page_config(
        page_icon="🍐",
        layout="centered"
    )

    render_header()
    display_results()

if __name__ == "__main__":
    main()