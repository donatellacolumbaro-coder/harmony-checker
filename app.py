import streamlit as st
import time
import os

# Importiamo music21 per la gestione dei file musicali
try:
    import music21
except ImportError:
    st.error("Libreria music21 mancante. Assicurati che sia nel file requirements.txt")

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Harmony XML Player", page_icon="🎼")

class Partitura:
    def __init__(self, bpm=120):
        self.titolo = "Nessun brano caricato"
        self.bpm = bpm
        self.strumenti = {}

    def carica_da_xml(self, file_caricato):
        """Legge il file XML e prepara le note per la riproduzione."""
        try:
            # Salvataggio temporaneo per permettere a music21 di leggere il file
            with open("temp.xml", "wb") as f:
                f.write(file_caricato.getbuffer())
            
            # Conversione del file in un oggetto musicale
            score = music21.converter.parse("temp.xml")
            
            # Recupero titolo dai metadati
            if score.metadata and score.metadata.title:
                self.titolo = score.metadata.title
            else:
                self.titolo = file_caricato.name
            
            # Estrazione note per ogni strumento
            for part in score.parts:
                nome = part.partName if part.partName else "Strumento"
                self.strumenti[nome] = []
                for nota in part.recurse().notes:
                    if nota.isNote:
                        self.strumenti[nome].append((nota.nameWithOctave, nota.duration.quarterLength))
                    elif nota.isChord:
                        # Se è un accordo, prendiamo la nota più alta
                        self.strumenti[nome].append((nota.sortTuple()[0].nameWithOctave, nota.duration.quarterLength))
            return True
        except Exception as e:
            st.error(f"Errore tecnico durante la lettura del file: {e}")
            return False

# --- INTERFACCIA GRAFICA STREAMLIT ---
st.title("🎼 Harmony: Lettore MusicXML")
st.write("Trascina il tuo file XML qui sotto per visualizzare e riprodurre la partitura.")

# Sidebar per le impostazioni di velocità
bpm = st.sidebar.slider("Regola Velocità (BPM)", 60, 200, 120)
app = Partitura(bpm=bpm)

# Componente per il caricamento del file (Unico metodo di input)
file_xml = st.file_uploader("Scegli un file .xml o .musicxml", type=["xml", "musicxml"])

if file_xml is not None:
    # Se il file è caricato, lo processiamo
    if app.carica_da_xml(file_xml):
        st.success(f"✅ Brano caricato: **{app.titolo}**")
        
        # Mostra quante note sono state trovate
        nome_traccia = list(app.strumenti.keys())[0]
        st.info(f"Strumento rilevato: {nome_traccia} ({len(app.strumenti[nome_traccia])} note)")

        # TASTO PLAY
        if st.button("▶️ AVVIA RIPRODUZIONE"):
            placeholder_nota = st.empty()
            progresso = st.progress(0)
            
            note = app.strumenti[nome_traccia]
            secondi_per_quarto = 60 / bpm
            
            # Ciclo di riproduzione visiva
            for i, (nota, durata) in enumerate(note):
                # Aggiornamento UI
                placeholder_nota.markdown(f"### 🎵 Nota attuale: **{nota}**")
                progresso.progress((i + 1) / len(note))
                
                # Attesa basata sulla durata della nota e BPM
                time.sleep(durata * secondi_per_quarto)
            
            st.balloons()
            st.success("Riproduzione terminata!")
else:
    st.info("In attesa di un file XML per iniziare...")

# Pulizia file temporaneo alla fine
if os.path.exists("temp.xml"):
    os.remove("temp.xml")