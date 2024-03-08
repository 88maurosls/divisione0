import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import re
import os
import tempfile

# Definisci il percorso della cartella di upload temporanea
UPLOAD_FOLDER = tempfile.gettempdir()
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Credenziali del tuo account di servizio
CREDENTIALS = {
    "type": "service_account",
    "project_id": "streamlitdivisioni",
    "private_key_id": "a82c6b4d8ffc775bf25e826bd328f318e67ab155",
    "private_key": "-----BEGIN PRIVATE KEY-----\n[PRIVATE_KEY]\n-----END PRIVATE KEY-----\n",
    "client_email": "divisione@streamlitdivisioni.iam.gserviceaccount.com",
    "client_id": "116678136247034327255",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/divisione%40streamlitdivisioni.iam.gserviceaccount.com"
}

# Creazione delle credenziali
creds = service_account.Credentials.from_service_account_info(CREDENTIALS, scopes=SCOPES)

# Funzioni di elaborazione del CSV
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
        df_data['Value_Next_to_HEADER1'] = values_next_to_header1

        temp_output_file_path = os.path.join(UPLOAD_FOLDER, f"processed_{os.path.basename(file_path)}")
        df_data.to_csv(temp_output_file_path, index=False)
        return temp_output_file_path

    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
        return None

# Funzione per caricare i dati da CSV a Google Sheets
def upload_to_google_sheets(file_path, sheet_name):
    try:
        df = pd.read_csv(file_path)

        # Autorizzazione con credenziali
        client = gspread.authorize(creds)

        sheet = client.open_by_url(sheet_name).sheet1
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("File caricato con successo su Google Sheets!")
    except Exception as e:
        st.error(f"Errore durante il caricamento su Google Sheets: {e}")

# Funzione principale Streamlit
def main():
    st.title('Caricamento CSV su Google Sheets')

    # Carica il file CSV
    file = st.file_uploader("Carica un file CSV", type=['csv'])

    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(file.getvalue())
            file_path = tmp_file.name

        processed_file_path = trasponi_valore_accanto_header1(file_path, 9)

        if processed_file_path:
            try:
                df = pd.read_csv(processed_file_path)
                st.write(df)
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")
                return

            if st.button('Carica su Google Sheets'):
                upload_to_google_sheets(processed_file_path, "https://docs.google.com/spreadsheets/d/1xiBRf0dPlnhmpYKJrOAtdSLX5oBKfI0s6pvY3S1MVDw/edit#gid=0")

if __name__ == "__main__":
    main()
