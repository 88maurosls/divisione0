import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Funzione per caricare i dati da CSV a Google Sheets
def upload_to_google_sheets(file_path, sheet_name):
    # Leggi il file CSV
    df = pd.read_csv(file_path)

    # Carica le credenziali di accesso all'API di Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('path/to/your/credentials.json', scopes=scope)
    client = gspread.authorize(creds)

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
        try:
            df = pd.read_csv(file, delimiter=',')
            st.write(df)
        except Exception as e:
            st.error(f"Errore durante la lettura del file CSV: {e}")
            return

        # Carica su Google Sheets
        if st.button('Carica su Google Sheets'):
            upload_to_google_sheets(file, "https://docs.google.com/spreadsheets/d/1xiBRf0dPlnhmpYKJrOAtdSLX5oBKfI0s6pvY3S1MVDw/edit#gid=0")

if __name__ == "__main__":
    main()
