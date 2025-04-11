import json
import vosk
import pyaudio
from difflib import get_close_matches
import os

class VoiceCommandRecognizer:
    def __init__(self, model_path, commands_file):
        """
        Inicjalizacja rozpoznawania mowy.
        :param model_path: Ścieżka do modelu Vosk
        :param commands_file: Ścieżka do pliku JSON z komendami
        """
        self.model = vosk.Model(model_path)
        self.commands = self._load_commands(commands_file)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)  # 16000 Hz - częstotliwość próbkowania
        self.audio_stream = self._setup_audio()

    def _setup_audio(self, format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000, device_index=None):
        """Konfiguracja strumienia audio."""
        p = pyaudio.PyAudio()
        if device_index is None:
            device_index = p.get_default_input_device_info()["index"]
        stream = p.open(
            format=format, channels=channels, rate=rate, input=input, input_device_index=device_index, frames_per_buffer=frames_per_buffer
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
        words = recognized_text.split()
    
        for word in words:
            matches = get_close_matches(word, self.commands.keys(), n=1, cutoff=0.6)
            if matches:
                return self.commands[matches[0]]
        return None

    def _reset_recognizer(self):
        """Resetuje recognizera (czyści bufor dźwięku)."""
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)


    def process_audio(self):
        data = self.audio_stream.read(4000, exception_on_overflow=False)

        if self.recognizer.AcceptWaveform(data):
            partial_result = json.loads(self.recognizer.PartialResult())
            partial_text = partial_result.get("partial", "")
            matched_command = self._match_command(partial_text)
            if matched_command:
                self._reset_recognizer()
                return matched_command

        return None


if __name__ == "__main__":
    commands_file = "commands.json"  # sczytujemy z pliku JSON zawierającego komendy
    model_path = os.path.join("models", "vosk-model-en-us-0.22")
    recognizer = VoiceCommandRecognizer(model_path, commands_file)

    print("Setup recognizera skończony, można mówić")
    while True:
        command = recognizer.process_audio()
        if command:
            print(f"Rozpoznano komendę: {command}")
