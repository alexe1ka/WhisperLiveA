from whisper_live.client import TranscriptionClient

host = 'localhost'
host = '0.0.0.0'
port = 9090

client = TranscriptionClient(
    host,
    port,
    lang="kk",
    translate=False,
    model="",
    use_vad=False,
    save_output_recording=True,
    output_recording_filename="./output_recording.wav",
    max_clients=4,
    max_connection_time=600,
    mute_audio_playback=False,
    rate=8000
)
client()
