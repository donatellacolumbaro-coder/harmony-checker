import time
import os

class Partitura:
    def __init__(self, titolo="Nuova Partitura", compositore="Sconosciuto", bpm=120):
        self.titolo = titolo
        self.compositore = compositore
        self.bpm = bpm
        self.strumenti = []

    def aggiungi_strumento(self, nome, chiave):
        """Crea un nuovo rigo nella partitura."""
        self.strumenti.append({"nome": nome, "chiave": chiave, "note": []})

    def carica_da_testo(self, nome_strumento, testo_note):
        """
        Carica le note da una stringa. 
        Formato: Nota:Durata, Nota:Durata (es. Do4:1, Re4:1)
        """
        for s in self.strumenti:
            if s["nome"] == nome_strumento:
                parti = testo_note.replace(" ", "").split(",")
                for p in parti:
                    if ":" in p:
                        n, d = p.split(":")
                        s["note"].append((n, float(d)))
                print(f"✅ Note caricate in: {nome_strumento}")
                return
        print(f"❌ Strumento {nome_strumento} non trovato.")

    def play(self):
        """Il tasto PLAY: riproduce la musica nel terminale."""
        print(f"\n▶️  ESECUZIONE: {self.titolo} ({self.compositore})")
        print(f"⏱️  Tempo: {self.bpm} BPM")
        print("-" * 30)

        secondi_per_quarto = 60 / self.bpm

        if not self.strumenti or not self.strumenti[0]["note"]:
            print("🔇 Nulla da suonare. Carica delle note!")
            return

        # Suoniamo il primo strumento caricato
        strumento = self.strumenti[0]
        for nota, durata in strumento["note"]:
            # Visualizzazione grafica
            barra = "█" * int(durata * 4)
            print(f"   ♪ {nota:<5} {barra}")
            
            # Aspetta il tempo reale della nota
            time.sleep(durata * secondi_per_quarto)

        print("-" * 30)
        print("⏹️  Fine.\n")

# --- AVVIO DELL'APP ---
if __name__ == "__main__":
    # 1. Inizializziamo l'app
    app = Partitura("Il mio brano", "Studente", bpm=120)
    app.aggiungi_strumento("Piano", "Sol")

    # 2. Carichiamo la musica (puoi cambiare questa stringa con quello che vuoi)
    musica = "Do4:1, Mi4:1, Sol4:1, Do5:2, Sol4:1, Mi4:1, Do4:2"
    app.carica_da_testo("Piano", musica)

    # 3. Premiamo Play
    app.play()