from pycaw.pycaw import AudioUtilities
import time

def list_audio_sessions():
    # Get all audio sessions
    sessions = AudioUtilities.GetAllSessions()
    app_names = set()  # To store unique application names

    print("Applications with active audio sessions:")
    print("-" * 30)
    
    for session in sessions:
        process = session.Process
        if process:
            # Get process name
            process_name = process.name()
            app_names.add(process_name)

    for name in app_names:
        print(f"Application: {name}")

if __name__ == "__main__":
    list_audio_sessions()