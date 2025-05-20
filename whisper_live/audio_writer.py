import queue
import threading

import numpy as np


class AudioWriter:
    def __init__(self):
        self.audio_queues = {}
        self.writers = {}
        self.running = True
        self.thread = threading.Thread(target=self._write_loop, daemon=True)
        self.thread.start()

    def add_client(self, client_uid: str, original_rate: int):

        self.audio_queues[client_uid] = {
            'original': queue.Queue(),
            'resampled': queue.Queue()
        }

        import wave
        original_filename = f"saved_audio/{client_uid}_original.wav"
        resampled_filename = f"saved_audio/{client_uid}_resampled.wav"

        original_wf = wave.open(original_filename, 'wb')
        original_wf.setnchannels(1)  # Mono
        original_wf.setsampwidth(2)  # 2 bytes for int16
        original_wf.setframerate(original_rate)


        resampled_wf = wave.open(resampled_filename, 'wb')
        resampled_wf.setnchannels(1)  # Mono
        resampled_wf.setsampwidth(2)  # 2 bytes for int16
        resampled_wf.setframerate(16000)  # Always 16kHz for resampled

        self.writers[client_uid] = {
            'original': original_wf,
            'resampled': resampled_wf
        }

    def remove_client(self, client_uid: str):
        if client_uid in self.audio_queues:
            # Signal stop for both queues
            self.audio_queues[client_uid]['original'].put(None)
            self.audio_queues[client_uid]['resampled'].put(None)

            # Wait for queues to be empty
            self.audio_queues[client_uid]['original'].join()
            self.audio_queues[client_uid]['resampled'].join()

            # Close both files
            self.writers[client_uid]['original'].close()
            self.writers[client_uid]['resampled'].close()

            # Clean up
            del self.audio_queues[client_uid]
            del self.writers[client_uid]

    def write_audio(self, client_uid: str, audio_data: np.ndarray):
        """Write original audio data"""
        if client_uid in self.audio_queues:
            self.audio_queues[client_uid]['original'].put(audio_data)

    def write_resampled(self, client_uid: str, audio_data: np.ndarray):
        """Write resampled audio data"""
        if client_uid in self.audio_queues:
            self.audio_queues[client_uid]['resampled'].put(audio_data)

    def _write_loop(self):
        while self.running:
            for client_uid in list(self.audio_queues.keys()):
                try:
                    # Process original audio
                    try:
                        original_audio = self.audio_queues[client_uid]['original'].get_nowait()
                        if original_audio is None:  # Signal to stop
                            self.audio_queues[client_uid]['original'].task_done()
                            continue

                        # Convert float32 to int16 for saving
                        audio_int16 = (original_audio * 32768.0).astype(np.int16)
                        self.writers[client_uid]['original'].writeframes(audio_int16.tobytes())
                        self.audio_queues[client_uid]['original'].task_done()
                    except queue.Empty:
                        pass

                    # Process resampled audio
                    try:
                        resampled_audio = self.audio_queues[client_uid]['resampled'].get_nowait()
                        if resampled_audio is None:  # Signal to stop
                            self.audio_queues[client_uid]['resampled'].task_done()
                            continue

                        # Convert float32 to int16 for saving
                        audio_int16 = (resampled_audio * 32768.0).astype(np.int16)
                        self.writers[client_uid]['resampled'].writeframes(audio_int16.tobytes())
                        self.audio_queues[client_uid]['resampled'].task_done()
                    except queue.Empty:
                        pass

                except Exception as e:
                    #logging.error(f"Error writing audio for client {client_uid}: {e}",exc_info=True)
                    try:
                        self.audio_queues[client_uid]['original'].task_done()
                    except:
                        pass
                    try:
                        self.audio_queues[client_uid]['resampled'].task_done()
                    except:
                        pass

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
