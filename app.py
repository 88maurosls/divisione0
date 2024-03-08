import streamlit as st
import pandas as pd
import gspread
import re
import os
import tempfile
from google.oauth2 import service_account

# Funzione per correggere le righe del file CSV se contengono più campi del previsto
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

# Funzione per trasporre un valore specifico accanto a HEADER1 in tutte le righe
def transpose_value_next_to_header1(file_path, expected_fields):
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
            elif not header_pattern.match(fields[0]):
                data_rows.append(fields)
                values_next_to_header1.append(value_next_to_header1)

        # Aggiunta del valore accanto a HEADER1 come nuova colonna
        df_data = pd.DataFrame(data_rows)
        df_data.insert(0, 'Value_Next_to_HEADER1', values_next_to_header1)

        temp_output_file_path = os.path.join(tempfile.gettempdir(), f"processed_{os.path.basename(file_path)}")
        df_data.to_csv(temp_output_file_path, index=False)
        return temp_output_file_path

    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
        return None

# Funzione per caricare i dati da un file CSV a Google Sheets
def upload_to_google_sheets(df, sheet_name):
    try:
        creds_info = {
            "type": st.secrets["service_account"]["type"],
            "project_id": st.secrets["service_account"]["project_id"],
            "private_key_id": st.secrets["service_account"]["private_key_id"],
            "private_key": st.secrets["service_account"]["private_key"],
            "client_email": st.secrets["service_account"]["client_email"],
            "client_id": st.secrets.get("client_id"),  # Solo se necessario
            "auth_uri": st.secrets.get("auth_uri"),    # Solo se necessario
            "token_uri": st.secrets.get("token_uri"),  # Solo se necessario
            "auth_provider_x509_cert_url": st.secrets.get("auth_provider_x509_cert_url"),  # Solo se necessario
            "client_x509_cert_url": st.secrets.get("client_x509_cert_url")  # Solo se necessario
        }
        creds = service_account.Credentials.from_service_account_info(creds_info)

        # Autorizza l'accesso a Google Sheets
        gc = gspread.authorize(creds)

        # Apertura del foglio di lavoro Google Sheets
        sheet = gc.open(sheet_name).sheet1
        sheet.clear()

        # Trasforma il DataFrame in una lista di liste per l'aggiornamento di Google Sheets
        values = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update(values)
        st.success('File caricato con successo su Google Sheets!')
    except Exception as e:
        st.error(f"Errore durante il caricamento su Google Sheets: {e}")

# Funzione principale di Streamlit per l'interfaccia utente
def main():
    st.title('Caricamento CSV su Google Sheets')

    # Caricamento del file CSV
    file = st.file_uploader("Carica un file CSV", type=['csv'])

    if file is not None:
        file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())
        
        # Processa il file CSV
        processed_file_path = transpose_value_next_to_header1(file_path, 9)

        if processed_file_path:
            try:
                df = pd.read_csv(processed_file_path)
                st.dataframe(df)

                # Quando premuto, carica i dati su Google Sheets
                if st.button('Carica su Google Sheets'):
                    sheet_name = st.text_input('Inserisci il nome del foglio di lavoro di Google Sheets', 'Sheet1')
                    upload_to_google_sheets(df, sheet_name)
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")

if __name__ == "__main__":
    main()
