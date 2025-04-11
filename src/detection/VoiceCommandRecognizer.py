import json
import vosk
import pyaudio
from difflib import get_close_matches
import os


# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
LIGHT_BLUE = "\033[94m"
RESET = "\033[0m"


class VoiceCommandRecognizer:
    def __init__(self, model_path, commands_file):
        self.model = vosk.Model(model_path)
        self.commands = self._load_commands(commands_file)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self._setup_audio()
        self.current_device_index = None

    def _load_commands(self, commands_file):
        with open(commands_file, "r") as file:
            raw_commands = json.load(file)
        return {alt: key for key, alts in raw_commands.items() for alt in alts}

    def _setup_audio(self, device_index=None):
        try:
            if device_index is None:
                device_index = self.pyaudio_instance.get_default_input_device_info()["index"]

            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=4000
            )
            stream.start_stream()
            self.current_device_index = device_index
            info = self.pyaudio_instance.get_device_info_by_index(device_index)
            print(f"{GREEN}Using audio input device (index {device_index}){RESET}")
            return stream
        except Exception as e:
            print(f"{RED}Failed to open audio device {device_index}: {e}{RESET}")
            return None

    def _find_working_audio_device(self):
        count = self.pyaudio_instance.get_device_count()
        for i in range(count):
            info = self.pyaudio_instance.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                stream = self._setup_audio(device_index=i)
                if stream:
                    return stream
        print(f"{RED}No working audio input device found.{RESET}")
        return None

    def _recover_audio(self):
        print(f"{LIGHT_BLUE}Attempting to recover audio stream...{RESET}")

        try:
            if self.audio_stream is not None:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
        except Exception as e:
            print(f"{RED}Error while closing audio stream: {e}{RESET}")

        self.audio_stream = None
        self.audio_stream = self._find_working_audio_device()

        if self.audio_stream:
            print(f"{GREEN}Audio stream successfully restored.{RESET}")
        else:
            print(f"{RED}Failed to restore audio stream.{RESET}")

    def _match_command(self, recognized_text):
        words = recognized_text.split()
        result = None
        for word in words:
            matches = get_close_matches(word, self.commands.keys(), n=1, cutoff=0.6)
            if matches:
                if result is None:
                    result = "2" + self.commands[matches[0]]
                else:
                    result += self.commands[matches[0]]
        return result

    def _reset_recognizer(self):
        self.recognizer.Reset()

    def process_audio(self):
        if not self.audio_stream:
            self._recover_audio()
            if not self.audio_stream:
                return None

        try:
            data = self.audio_stream.read(1000, exception_on_overflow=False)
        except Exception as e:
            print(f"{RED}Audio read error: {e}{RESET}")
            self._recover_audio()
            return None

        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.PartialResult())
            partial_text = result.get("partial", "")
            matched_command = self._match_command(partial_text)
            if matched_command:
                self._reset_recognizer()
                return matched_command

        return None
