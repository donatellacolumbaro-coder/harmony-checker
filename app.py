import time

class Partitura:
    """
    Questa classe rappresenta una Partitura (Score) generica.
    Può essere usata per corali, sinfonie, sonate o brani pop.
    """
    def __init__(self, titolo, compositore, tempo_bpm=120):
        self.titolo = titolo
        self.compositore = compositore
        self.tempo_bpm = tempo_bpm  # Battiti Per Minuto (velocità)
        self.strumenti = []  # Lista che conterrà i righi della partitura

    def aggiungi_strumento(self, nome_strumento, chiave):
        """
        Aggiunge un rigo strumentale vuoto alla partitura.
        Es: nome="Violino", chiave="Sol"
        """
        nuovo_strumento = {
            "nome": nome_strumento,
            "chiave": chiave,
            "note": [] # Lista delle note per questo strumento
        }
        self.strumenti.append(nuovo_strumento)
        print(f"➕ Strumento aggiunto: {nome_strumento} (Chiave di {chiave})")

    def aggiungi_nota(self, nome_strumento, nota, durata_quarti):
        """
        Aggiunge una nota a uno specifico strumento.
        durata_quarti: 1 = semiminima (un quarto), 2 = minima (due quarti), etc.
        """
        strumento_trovato = False
        for strumento in self.strumenti:
            if strumento["nome"] == nome_strumento:
                strumento["note"].append((nota, durata_quarti))
                strumento_trovato = True
                break
        
        if not strumento_trovato:
            print(f"⚠️ Errore: Lo strumento '{nome_strumento}' non esiste nella partitura.")

    def play(self):
        """
        IL TASTO PLAY.
        Simula la riproduzione della partitura calcolando i tempi reali in base ai BPM.
        """
        print(f"\n{'='*40}")
        print(f"▶️  PLAY: {self.titolo} - {self.compositore}")
        print(f"    Tempo: {self.tempo_bpm} BPM")
        print(f"{'='*40}")
        
        # Calcolo quanto dura un "quarto" in secondi reali
        secondi_per_quarto = 60 / self.tempo_bpm

        if not self.strumenti:
            print("🔇 La partitura è vuota!")
            return

        # SIMULAZIONE PLAYBACK
        # Per semplicità in console, riproduciamo la linea del primo strumento inserito
        strumento_lead = self.strumenti[0]
        print(f"🔊 Ascolto traccia: {strumento_lead['nome']}...\n")

        for i, (nota, durata) in enumerate(strumento_lead["note"], 1):
            durata_reale = durata * secondi_per_quarto
            
            # Visualizzazione "Player"
            barra_avanzamento = "▓" * int(durata * 4) # Grafica semplice per la durata
            print(f"[{i}] 🎵 {nota:<4} (Durata: {durata}q) {barra_avanzamento}")
            
            # Il programma attende qui, simulando il suono
            time.sleep(durata_reale)

        print("\n⏹️  STOP - Fine esecuzione.")
        print(f"{'='*40}\n")

# --- ZONA DI TEST (ESEMPIO D'USO) ---

if __name__ == "__main__":
    # 1. Creazione della Partitura (Generica, non più solo Corale)
    # Impostiamo un tempo veloce (140 BPM)
    mia_partitura = Partitura("Inno alla Gioia (Demo)", "L. van Beethoven", tempo_bpm=140)

    # 2. Aggiunta degli strumenti (Righi)
    mia_partitura.aggiungi_strumento("Flauto", "Sol")
    mia_partitura.aggiungi_strumento("Violoncello", "Fa")

    # 3. Scrittura delle note (Melodia: Mi - Mi - Fa - Sol - Sol - Fa - Mi - Re)
    # Formato: (Nome Nota, Durata in quarti)
    note_beethoven = [
        ("Mi", 1), ("Mi", 1), ("Fa", 1), ("Sol", 1),
        ("Sol", 1), ("Fa", 1), ("Mi", 1), ("Re", 1),
        ("Do", 1), ("Do", 1), ("Re", 1), ("Mi", 1),
        ("Mi", 1.5), ("Re", 0.5), ("Re", 2) # Finale della frase
    ]

    # Inseriamo le note nel Flauto
    for n, d in note_beethoven:
        mia_partitura.aggiungi_nota("Flauto", n, d)

    # 4. Premiamo Play
    mia_partitura.play()