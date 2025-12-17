import streamlit as st
import music21
import tempfile
import os

# Configurazione della pagina
st.set_page_config(page_title="Harmony Checker", page_icon="🎼", layout="wide")

st.title("🎼 Harmony Checker")
st.markdown("Carica il tuo file **MusicXML** (.xml o .mxl). L'app cercherà **Ottave e Quinte Parallele**.")

def check_parallels(score):
    errors = []
    
    # Espandi le ripetizioni
    try:
        score = score.expandRepeats()
    except:
        pass # Se fallisce l'espansione, analizza così com'è
    
    parts = list(score.parts)
    
    if len(parts) < 2:
        return ["⚠️ Il file deve contenere almeno 2 voci distinte per cercare paralleli."]

    # Itera su tutte le coppie di voci
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            part_a = parts[i]
            part_b = parts[j]
            
            # Nomi delle voci
            name_a = part_a.partName or f"Voce {i+1}"
            name_b = part_b.partName or f"Voce {j+1}"
            
            # Estrai le note appiattendo la struttura
            notes_a = part_a.flatten().notesAndRests.stream()
            notes_b = part_b.flatten().notesAndRests.stream()
            
            # Crea liste di (offset, nota) per sincronizzare
            list_a = [(n.offset, n) for n in notes_a if n.isNote]
            list_b = [(n.offset, n) for n in notes_b if n.isNote]
            
            # Trova gli eventi simultanei (note che suonano insieme)
            simultaneous_events = []
            for off_a, note_a in list_a:
                # Cerca una nota nella voce B che inizia allo stesso offset
                match = next((n for off_b, n in list_b if off_b == off_a), None)
                if match:
                    simultaneous_events.append((note_a, match))
            
            # Analisi intervalli consecutivi
            for k in range(len(simultaneous_events) - 1):
                n1_curr, n2_curr = simultaneous_events[k]
                n1_next, n2_next = simultaneous_events[k+1]
                
                # Calcola intervalli
                vl_curr = music21.interval.Interval(n2_curr, n1_curr).simpleName
                vl_next = music21.interval.Interval(n2_next, n1_next).simpleName
                
                # SE entrambi sono P5 (Quinta) o P8 (Ottava)
                if vl_curr in ["P5", "P8"] and vl_next == vl_curr:
                    
                    # Verifica che non siano note ribattute (moto obliquo o nullo)
                    # Errore c'è solo se le note cambiano altezza
                    if n2_curr.pitch != n2_next.pitch and n1_curr.pitch != n1_next.pitch:
                        
                        m_num = n1_curr.measureNumber
                        err = f"🚫 **{vl_curr} Parallela** a Battuta {m_num} | Tra **{name_a}** e **{name_b}**"
                        errors.append(err)

    return errors

# --- INTERFACCIA ---

uploaded_file = st.file_uploader("Trascina qui il file", type=["xml", "mxl", "musicxml"])

if uploaded_file is not None:
    st.info("Analisi in corso... attendere...")
    
    # Salva file temporaneo con l'estensione corretta (IMPORTANTE per .mxl)
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        # Carica e Analizza
        score = music21.converter.parse(tmp_path)
        report = check_parallels(score)
        
        st.divider()
        
        if len(report) == 0:
            st.success("✅ **Nessun errore trovato!** Ottimo lavoro.")
            st.balloons()
        else:
            st.error(f"Trovati {len(report)} errori di moto parallelo:")
            for err in report:
                st.write(err)

    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
    finally:
        # Pulizia file temporaneo
        if os.path.exists(tmp_path):
            os.remove(tmp_path)