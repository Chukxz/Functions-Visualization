
import sys
import tkinter as tk

def get_usable_screen_size():
  root = tk.Tk()

  # Get full screen size
  full_width = root.winfo_screenwidth()
  full_height = root.winfo_screenheight()

  # Get usable screen size (excluding taskbar/dock)
  usable_width = root.winfo_vrootwidth()
  usable_height = root.winfo_vrootheight()

  root.destroy()

  # Windows-specific fix using Win32 API
  if sys.platform == "win32":
    try:
      import ctypes.wintypes

      # Get work area excluding taskbar
      rect = ctypes.wintypes.RECT()
      ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)

      usable_width = rect.right - rect.left
      usable_height = rect.bottom - rect.top

    except ImportError:
      pass # Win32 modules not available, fallback to Tkinter values

  # macOS-specific fix using AppKit
  elif sys.platform == "darwin":
    try:
      from AppKit import NSScreen
      screen = NSScreen.mainScreen()
      frame = screen.visibleframe()

      usable_width = int(frame.size.width)
      usable_height = int(frame.size.height)

    except ImportError:
      pass # AppKit not available, fallback to Tkinter values
  
  # Linux fixs
  elif sys.platform.startswith("linux"):
    import subprocess
    session_type = os.getenv("XDG_SESSION_TYPE")

    if session_type == "x11":        
      # Use xrandr for x11
      try:
        output = subprocess.check_output("xrandr --query | grep '*' | awk '{print $1}'", shell=True)
        usable_width, usable_height = map(int, output.decode().split("x"))
        
      except Exception:
        pass # xrandr not available, fallback to TKinter values
    
    elif session_type == "wayland":
      # Try GTK for GNOME/KDE
      try:
        import gi
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk

        screen = Gdk.Screen.get_default()
        usable_width = screen.get_width()
        usable_height = screen.get_height()

      except Exception:
        pass # move on to wlr-randr

      # Try wlr-randr for wlroots-based compositors
      try:
        output = subprocess.check_output("wlr-randr", shell=True).decode()
        for line in output.split("\n"):
          if "*" in line:
            resolution = line.split()[0]
            usable_width, usable_height = map(int, resolution.split("x"))
      
      except Exception:
        pass # fallback to Tkinter values

  
  return full_width, full_height, usable_width, usable_height

if __name__ == "__main__":
  print(get_usable_screen_size())
