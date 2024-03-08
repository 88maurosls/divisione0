import streamlit as st
import pandas as pd
import gspread
import os
import re
import uuid
from google.oauth2.service_account import Credentials
import tempfile

# Funzioni di elaborazione del CSV dallo script Flask
def correct_csv(file_path, expected_fields):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    corrected_lines = []
    for line in lines:
        fields = line.strip().split(',')
        if len(fields) > expected_fields:
            corrected_fields = fields[:expected_fields]
        else:
            corrected_fields = fields
        corrected_lines.append(','.join(corrected_fields) + '\n')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(corrected_lines)

def trasponi_valore_accanto_header1(file_path, expected_fields):
    try:
        correct_csv(file_path, expected_fields)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # [Il resto della funzione trasponi_valore_accanto_header1 va qui]
        # ...

        return temp_output_file_path

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return None

# Funzione per caricare i dati da CSV a Google Sheets (da adattare)
def upload_to_google_sheets(file_path, sheet_name):
    # [Codice per caricare il CSV modificato su Google Sheets]
    # ...

# Funzione principale Streamlit
def main():
    st.title('Caricamento CSV su Google Sheets')

    # Carica il file CSV
    file = st.file_uploader("Carica un file CSV", type=['csv'])

    if file is not None:
        # Crea un percorso temporaneo per salvare il file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(file.getvalue())
            file_path = tmp_file.name

        # Elabora il file CSV
        processed_file_path = trasponi_valore_accanto_header1(file_path, 9)

        if processed_file_path:
            try:
                df = pd.read_csv(processed_file_path)
                st.write(df)
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")
                return

            # Carica su Google Sheets
            if st.button('Carica su Google Sheets'):
                upload_to_google_sheets(processed_file_path, "https://docs.google.com/spreadsheets/d/1xiBRf0dPlnhmpYKJrOAtdSLX5oBKfI0s6pvY3S1MVDw/edit#gid=0")

if __name__ == "__main__":
    main()
