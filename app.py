import pandas as pd
import os
import re
import uuid
from openpyxl import load_workbook
from openpyxl.styles import Font
from datetime import datetime
import streamlit as st

# Definisci il percorso assoluto della cartella di upload
UPLOAD_FOLDER = "uploads"

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
        # Assicurati che il file CSV sia nel formato corretto
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

        # Gestione della colonna SKU
        if len(df_data.columns) >= 3:
            df_data['SKU'] = df_data.iloc[:, 1] + '-' + df_data.iloc[:, 2]

        df_data['Value_Next_to_HEADER1'] = values_next_to_header1
        df_data = df_data[['Value_Next_to_HEADER1', 'SKU'] + [col for col in df_data.columns if col not in ['SKU', 'Value_Next_to_HEADER1']]]

        # Genera un nome di file unico per evitare sovrascritture
        unique_filename = f"output_{uuid.uuid4()}.xlsx"
        temp_output_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        headers = ["Rif. Sped.", "SKU", "Collo", "Codice", "Colore", "Size", "UPC", "Made in", "Unità", "Confezione", "customer PO", "Riferimento Spedizione"]
        df_data.columns = headers[:len(df_data.columns)]

        df_data[['Collo', 'UPC']] = df_data[['Collo', 'UPC']].apply(lambda x: '{:.0f}'.format(x) if isinstance(x, (int, float)) else x)

        df_data.to_excel(temp_output_file_path, index=False, float_format="%.0f")

        # Applica lo stile alle celle dell'intestazione
        wb = load_workbook(temp_output_file_path)
        ws = wb.active
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = Font(bold=True)
        wb.save(temp_output_file_path)

        return temp_output_file_path

    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
        return None

def process_file(file_path, expected_fields=9):
    st.write(f"\nInizio elaborazione del file {file_path}...")
    output_file_path = trasponi_valore_accanto_header1(file_path, expected_fields)
    if output_file_path:
        st.success("Elaborazione completata.")
        st.markdown(f"File salvato in: [{output_file_path}]({output_file_path})")
        return output_file_path
    else:
        st.error("Errore nell'elaborazione del file.")
        return None

def index():
    st.title('Caricamento File')
    uploaded_files = st.file_uploader("Carica i file CSV da elaborare", type='csv', accept_multiple_files=True)

    if uploaded_files:
        processed_files_info = []

        for uploaded_file in uploaded_files:
            if uploaded_file:
                file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
                st.write(file_details)
                file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Elabora ogni file
                output_file_path = process_file(file_path)
                if output_file_path:
                    # Qui viene gestito il file processato

                    # Aggiungi il file processato a processed_files_info
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    if "-" in base_name:
                        base_name = base_name.split("-")[1]
                    base_name = base_name[:31]  # Limite del nome del foglio Excel
                    processed_files_info.append((output_file_path, base_name))

                else:
                    st.error(f"Errore nell'elaborazione del file {uploaded_file.name}")

        # Qui combini i file elaborati in un unico file Excel, se necessario
        if processed_files_info:
            combined_path = combine_excel_files(processed_files_info, UPLOAD_FOLDER)
            if combined_path:
                st.success("File combinato salvato correttamente.")
                st.markdown(f"Scarica il file combinato da [qui]({combined_path})")
            else:
                st.error("Errore nella combinazione dei file")
        else:
            st.warning("Nessun file elaborato con successo")

# Avvia l'app Streamlit
if __name__ == "__main__":
    index()

