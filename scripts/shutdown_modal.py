"""Stop this meeting app only. Does not delete research assets or private volumes."""
import subprocess
import sys
if __name__=='__main__':
    raise SystemExit(subprocess.run([sys.executable,'-m','modal','app','stop','insurance-slm-meeting-demo'],check=False).returncode)
