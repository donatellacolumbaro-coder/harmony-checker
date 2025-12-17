import streamlit as st
import time
import os

# Proviamo a importare music21 per i file XML
try:
    import music21
except ImportError:
    st.error("Libreria music21 mancante. Aggiungila al file requirements.txt")

# Configurazione della pagina
st.set_page_config(page_title="Harmony XML Player", page_icon="🎼")

class Partitura:
    def __init__(self, titolo="Nuova Partitura", bpm=120):
        self.titolo = titolo
        self.bpm = bpm
        self.strumenti = {}

    def carica_da_testo(self, nome_strumento, testo_note):
        self.strumenti[nome_strumento] = []
        parti = testo_note.replace(" ", "").split(",")
        for p in parti:
            if ":" in p:
                n, d = p.split(":")
                self.strumenti[nome_strumento].append((n, float(d)))
        return True

    def carica_da_xml(self, file_caricato):
        try:
            # Salviamo temporaneamente il file per farlo leggere a music21
            with open("temp.xml", "wb") as f:
                f.write(file_caricato.getbuffer())
            
            score = music21.converter.parse("temp.xml")
            self.titolo = score.metadata.title if score.metadata.title else "Brano XML"
            
            for part in score.parts:
                nome = part.partName if part.partName else "Strumento"
                self.strumenti[nome] = []
                for nota in part.recurse().notes:
                    if nota.isNote:
                        self.strumenti[nome].append((nota.nameWithOctave, nota.duration.quarterLength))
            return True
        except Exception as e:
            st.error(f"Errore nella lettura dell'XML: {e}")
            return False

# --- INTERFACCIA STREAMLIT ---
st.title("🎼 Harmony XML & Text Player")
st.write("Carica un file MusicXML o inserisci le note manualmente.")

# Sidebar per le impostazioni
bpm = st.sidebar.slider("Velocità (BPM)", 60, 200, 120)
app = Partitura(bpm=bpm)

# Scelta della modalità di inserimento
modalita = st.radio("Scegli come inserire la musica:", ("Inserimento Manuale", "Carica file XML"))

musica_pronta = False

if modalita == "Inserimento Manuale":
    musica_input = st.text_area("Note (Nota:Durata)", "Do4:1, Mi4:1, Sol4:1, Do5:2")
    if st.button("Carica Note"):
        musica_pronta = app.carica_da_testo("Piano", musica_input)