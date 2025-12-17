import streamlit as st
import music21
import tempfile
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Harmony Checker Pro", page_icon="🎼", layout="wide")

st.title("🎼 Harmony Checker Pro")
st.markdown("""
Questo strumento analizza la tua **partitura** (MusicXML) cercando i seguenti errori accademici:
* ❌ **Quinte e Ottave Parallele**
* ❌ **Sensibile non risolta** (sale alla Tonica)
* ❌ **Errori Melodici** (Salti di 2a eccedente, 7a, o > ottava)
* ❌ **Spaziatura eccessiva** (tra le voci superiori)
* ❌ **Incrocio delle parti**
""")

# --- FUNZIONI DI ANALISI ---

def get_simultaneous_notes(part_a, part_b):
    """Sincronizza due parti e trova le note che suonano insieme."""
    notes_a = part_a.flatten().notesAndRests.stream()
    notes_b = part_b.flatten().notesAndRests.stream()
    
    list_a = [(n.offset, n) for n in notes_a if n.isNote]
    list_b = [(n.offset, n) for n in notes_b if n.isNote]
    
    simultaneous = []
    for off_a, note_a in list_a:
        match = next((n for off_b, n in list_b if off_b == off_a), None)
        if match:
            simultaneous.append((note_a, match))
    return simultaneous

def check_parallels(parts):
    errors = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            part_a = parts[i]
            part_b = parts[j]
            name_a = part_a.partName or f"Voce {i+1}"
            name_b = part_b.partName or f"Voce {j+1}"
            
            pairs = get_simultaneous_notes(part_a, part_b)
            
            for k in range(len(pairs) - 1):
                n1_cur, n2_cur = pairs[k]
                n1_nxt, n2_nxt = pairs[k+1]
                
                try:
                    vl_cur = music21.interval.Interval(n2_cur, n1_cur).simpleName
                    vl_nxt = music21.interval.Interval(n2_nxt, n1_nxt).simpleName
                    
                    if vl_cur in ["P5", "P8"] and vl_nxt == vl_cur:
                        if n2_cur.pitch != n2_nxt.pitch and n1_cur.pitch != n1_nxt.pitch:
                            m_num = n1_cur.measureNumber
                            errors.append(f"🔴 **{vl_cur} Parallela** a Battuta {m_num} | Tra {name_a} e {name_b}")
                except:
                    continue
    return errors

def check_melodic_errors(parts):
    errors = []
    for part in parts:
        name = part.partName or "Voce"
        notes = list(part.flatten().notes.stream())
        
        for k in range(len(notes) - 1):
            n1 = notes[k]
            n2 = notes[k+1]
            
            try:
                melodic_int = music21.interval.Interval(n1, n2)
                semitones = abs(melodic_int.semitones)
                
                if melodic_int.simpleName == "A2":
                    errors.append(f"⚠️ **Intervallo Vietato (2a Aumentata)** a Battuta {n1.measureNumber} | {name}: {n1.name} -> {n2.name}")
                
                if semitones > 12:
                     errors.append(f"⚠️ **Salto eccessivo (> 8va)** a Battuta {n1.measureNumber} | {name}")
                elif melodic_int.simpleName in ["M7", "m7"]:
                     errors.append(f"⚠️ **Salto difficile (7a)** a Battuta {n1.measureNumber} | {name}")
                     
            except:
                continue
    return errors

def check_leading_tone_resolution(score, parts):
    errors = []
    try:
        key = score.analyze('key')
        leading_tone = key.getLeadingTone()
        tonic = key.tonic
        
        if not leading_tone or not tonic:
            return []

        for part in parts:
            name = part.partName or "Voce"
            notes = list(part.flatten().notes.stream())
            
            for k in range(len(notes) - 1):
                n1 = notes[k]
                n2 = notes[k+1]
                
                if n1.pitch.name == leading_tone.name:
                    if n2.pitch.name != tonic.name:
                        errors.append(f"🟠 **Sensibile non risolta** a Battuta {n1.measureNumber} | {name}: Il {n1.name} dovrebbe andare a {tonic.name}, invece va a {n2.name}")
    except:
        pass 
    return errors

def check_spacing_and_crossing(parts):
    errors = []
    if len(parts) < 2:
        return []

    for i in range(len(parts) - 1):
        upper_part = parts[i]
        lower_part = parts[i+1]
        
        pairs = get_simultaneous_notes(upper_part, lower_part)
        
        for n_up, n_low in pairs:
            if n_low.pitch > n_up.pitch:
                errors.append(f"❌ **Incrocio delle parti** a Battuta {n_up.measureNumber}: {upper_part.partName} scende sotto {lower_part.partName}")
            
            if i < 2: 
                interval = music21.interval.Interval(n_low, n_up)
                if interval.semitones > 12:
                    errors.append(f"📏 **Spaziatura eccessiva** a Battuta {n_up.measureNumber}: Tra {upper_part.partName} e {lower_part.partName} (> 1 ottava)")
                    
    return errors

# --- INTERFACCIA PRINCIPALE ---

uploaded_file = st.file_uploader("Trascina qui il file della tua partitura (.xml, .mxl)", type=["xml", "mxl", "musicxml"])

if uploaded_file is not None:
    st.info("Analisi della partitura in corso... 🧠")
    
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        score = music21.converter.parse(tmp_path)
        try:
            score = score.expandRepeats()
        except:
            pass
            
        parts = list(score.parts)
        
        if len(parts) < 2:
            st.warning("⚠️ La partitura ha meno di 2 voci. Impossibile controllare l'armonia.")
        else:
            errors_parallels = check_parallels(parts)
            errors_melody = check_melodic_errors(parts)
            errors_leading = check_leading_tone_resolution(score, parts)
            errors