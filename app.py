import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Funzione per caricare i dati da CSV a Google Sheets
def upload_to_google_sheets(file_path, sheet_name):
    # Leggi il file CSV
    df = pd.read_csv(file_path)

    # Carica le credenziali di accesso all'API di Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = {
        "installed": {
            "client_id": "566018196019-ororo6jebbvpuq73vp4d6b8b8mn0fuqj.apps.googleusercontent.com",
            "project_id": "streamlitdivisioni",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "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",
            "redirect_uris": ["http://localhost"]
        }
    }
    client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds, scope))

    # Apri il foglio di lavoro
    sheet = client.open_by_url(sheet_name).sheet1

    # Pulisci il foglio di lavoro
    sheet.clear()

    # Carica i dati nel foglio di lavoro
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Funzione principale
def main():
    st.title('Caricamento CSV su Google Sheets')

    # Carica il file CSV
    file = st.file_uploader("Carica un file CSV", type=['csv'])

    if file is not None:
        # Mostra i dati del CSV
        df = pd.read_csv(file)
        st.write(df)

        # Carica su Google Sheets
        if st.button('Carica su Google Sheets'):
            upload_to_google_sheets(file, "https://docs.google.com/spreadsheets/d/1xiBRf0dPlnhmpYKJrOAtdSLX5oBKfI0s6pvY3S1MVDw/edit#gid=0")

if __name__ == "__main__":
    main()
