import pandas as pd
import re
import uuid
from openpyxl import load_workbook
from openpyxl.styles import Font
from datetime import datetime
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def gsheet_api_check():
    creds = None
    if st.session_state.get('token_json'):
        creds = Credentials.from_authorized_user_info(st.session_state.token_json, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        st.session_state['token_json'] = creds.to_json()
    return creds

def upload_to_gsheet(df_data, spreadsheet_id, range_name):
    creds = gsheet_api_check()
    service = build('sheets', 'v4', credentials=creds)

    # Converti il DataFrame in una lista di liste escludendo l'intestazione
    values = df_data.values.tolist()

    # Chiamata all'API per aggiungere i nuovi dati al foglio di calcolo usando il metodo append
    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=body).execute()
    st.write(f"{result.get('updates', {}).get('updatedCells')} celle aggiornate.")

def correct_csv(file_data, expected_fields):
    lines = file_data.decode('utf-8').splitlines()

    corrected_lines = []
    for line in lines:
        fields = line.strip().split(',')
        if len(fields) > expected_fields:
            corrected_fields = fields[:expected_fields]
        else:
            corrected_fields = fields
        corrected_lines.append(','.join(corrected_fields) + '\n')

    return ''.join(corrected_lines)

def trasponi_valore_accanto_header1(file_data, expected_fields):
    try:
        # Assicurati che il file CSV sia nel formato corretto
        corrected_data = correct_csv(file_data, expected_fields)

        lines = corrected_data.splitlines()

        values_next_to_header1 = []
        data_rows = []
        header_pattern = re.compile(r'^HEADER\d+')
        value_next_to_header1 = ""

        for line in lines:
            fields = line.strip().split(',')
            if fields[0] == "HEADER1":
                value_next_to_header1 = fields[1] if len(fields) > 1 else ""
            if not header_pattern.match(fields[0]):
                data_rows.append(fields)
                values_next_to_header1.append(value_next_to_header1)

        df_data = pd.DataFrame(data_rows)

        # Gestione della colonna SKU
        if len(df_data.columns) >= 3:
            df_data['SKU'] = df_data.iloc[:, 1] + '-' + df_data.iloc[:, 2]

        df_data['Value_Next_to_HEADER1'] = values_next_to_header1
        df_data = df_data[['Value_Next_to_HEADER1', 'SKU'] + [col for col in df_data.columns if col not in ['SKU', 'Value_Next_to_HEADER1']]]

        # Genera un DataFrame con l'intestazione corretta
        headers = ["Rif. Sped.", "SKU", "Collo", "Codice", "Colore", "Size", "UPC", "Made in", "Unità", "Confezione", "customer PO", "Riferimento Spedizione"]
        df_data.columns = headers[:len(df_data.columns)]

        return df_data

    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
        return None

def process_file(uploaded_file, expected_fields=9):
    try:
        # Elabora il file
        df = trasponi_valore_accanto_header1(uploaded_file.getvalue(), expected_fields)
        return df
    except Exception as e:
        st.error(f"Errore nell'elaborazione del file: {e}")
        return None

st.title('Caricamento File')
uploaded_file = st.file_uploader("Carica un file CSV", type="csv")
if uploaded_file is not None:
    df = process_file(uploaded_file)
    if df is not None:
        st.success("Elaborazione completata.")
        st.write(df)

        # Caricamento su Google Sheets
        if st.button("Carica su Google Sheets"):
            spreadsheet_id = 'YOUR_SPREADSHEET_ID'
            range_name = 'Sheet1!A1'  # Sostituire con il proprio intervallo
            upload_to_gsheet(df, spreadsheet_id, range_name)
