Set WshShell = CreateObject("WScript.Shell")

' Start Ollama silently in the background (no window)
WshShell.Run "ollama run llama3.2:3b", 0, False

' Wait 8 seconds for model to load
WScript.Sleep 8000

' Launch the assistant GUI
WshShell.Run "python C:\Users\Bizec\Desktop\School_General\Ollama-Projects\stacey_assistant.py", 0, False
