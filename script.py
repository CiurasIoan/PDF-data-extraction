import pdfplumber
import re
import pandas as pd
import glob
import os

# folderul pdf
folder_path = " "
pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

date_extrase = []

for pdf_path in pdf_files:
    print("Procesez:", pdf_path)  # ca să vezi progresul

    # extrage greutate si inaltime
    g_val = t_val = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_all = ""
            if len(pdf.pages) > 0:
                text_all += pdf.pages[0].extract_text() or ""

            if len(pdf.pages) > 1:
                text_all += pdf.pages[1].extract_text() or ""

            # caută în tot textul
            match_context = re.search(r"Starea la internare", text_all)
            if match_context:
                # ia doar textul după acel punct
                text_after = text_all[match_context.end():]

                # caută G și T în acest text
                data1 = re.search(r"G\D+(\d+)", text_after)
                data2 = re.search(r"T\D+(\d+)", text_after)

                g_val = data1.group(1) if data1 else None
                t_val = data2.group(1) if data2 else None
    except Exception as e:
        print("Eroare la citirea G/T în", pdf_path, e)

    # extrage nume, sex, varsta
    nume = sex = varsta = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()

            if tables:
                primul_tabel = tables[0]
                if len(primul_tabel) > 1:
                    linia2 = primul_tabel[1]
                    if len(linia2) >= 6:
                        nume = linia2[0]
                        sex = linia2[4]
                        varsta = linia2[5]
    except Exception as e:
        print("Eroare la citirea tabelului în", pdf_path, e)

    # adauga datele
    date_extrase.append([nume, sex, varsta, g_val, t_val])

# export to excel
df = pd.DataFrame(date_extrase, columns=["Nume si Prenume", "Sex", "Varsta", "Greutate", "Inaltime"])
df.to_excel("calea spre excel", index=False)

print("✅ Procesare completă! Am extras", len(df), "fișiere.")
