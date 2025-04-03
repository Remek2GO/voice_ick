import json
import vosk
import pyaudio
from difflib import get_close_matches


class VoiceCommandRecognizer:
    def __init__(self, model_path, commands_file):
        """
        Inicjalizacja rozpoznawania mowy.
        :param model_path: Ścieżka do modelu Vosk
        :param commands_file: Ścieżka do pliku JSON z komendami
        """
        self.model = vosk.Model(model_path)
        self.commands = self._load_commands(commands_file)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000) #16000-częstotliwosc probkowania
        self.audio_stream = self._setup_audio()

    def _setup_audio(self, format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000
):
        """Konfiguracja strumienia audio."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=format, channels=channels, rate=rate, input=input, frames_per_buffer=frames_per_buffer
        )
        stream.start_stream()
        return stream

    def _load_commands(self, commands_file):
        """Ładuje komendy i ich alternatywy z pliku JSON."""
        with open(commands_file, "r") as file:
            raw_commands = json.load(file)

        commands_map = {}
        for key, alternatives in raw_commands.items():
            for alt in alternatives:
                commands_map[alt] = key  # Mapujemy każde alternatywne słowo do głównej komendy

        return commands_map

    def _match_command(self, recognized_text):
        """
        Dopasowuje rozpoznany tekst do najbliższej komendy lub jej alternatywy.
        """
        matches = get_close_matches(recognized_text, self.commands.keys(), n=1, cutoff=0.7)
        return self.commands[matches[0]] if matches else None

    def process_audio(self):
        """
        Przetwarza dźwięk i zwraca wykrytą komendę, lub None-brak dopasowania
        """
        data = self.audio_stream.read(4000, exception_on_overflow=False)
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            recognized_text = result.get("text", "")
            matched_command = self._match_command(recognized_text)
            if matched_command:
                return matched_command
        return None

if __name__ == "__main__":
    commands_file = "commands.json"  # sczytujemyz plikujson zawierającego komendy
    recognizer = VoiceCommandRecognizer("models/vosk-model-en-us-0.22", commands_file)

    # print("Setup recognizera skończony, można mówić")
    # while True:
    #     command = recognizer.process_audio()
    #     if command:
    #         print(f"Rozpoznano komendę: {command}")