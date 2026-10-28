# getTotp
I like to use keyboard shortcuts, so I wrote this script to keep my TOTP (MFA) codes in one place.

The secret key is stored in your operating system's password manager (macOS Keychain, Windows Credential Manager, or the Linux Secret Service such as GNOME Keyring / KWallet). It is never written to a plain file.

## Requirements

- Python 3
- The libraries `pyotp`, `keyring` and `pyperclip`

```
pip3 install --user pyotp keyring pyperclip
```

## Usage

The first time you run it (or with `-n`), the script asks for the TOTP key. This is the secret shown when you set up MFA, often labelled "can't scan the QR code?". Spaces and lowercase letters are fine, and the input is hidden while you type. **Run it once in a terminal** so you can enter the key before binding it to a shortcut.

```
python3 getTotp.py            # Current OTP key: 123456 Time left 17
python3 getTotp.py -o         # 123456
python3 getTotp.py -c         # copy the code to the clipboard (no output)
python3 getTotp.py -c -b      # copy and beep
python3 getTotp.py -l 5       # refresh the display every 5 seconds (Ctrl+C to stop)
python3 getTotp.py -s github  # use a separate key named "github"
python3 getTotp.py -n         # replace the stored key
```

| Option | Description |
|---|---|
| `-o`, `--only_code` | Display only the code |
| `-c`, `--clipboard` | Copy the code to the clipboard |
| `-b`, `--beep` | Beep after copying (with `-c`) |
| `-l N`, `--loop N` | Refresh every N seconds (2 to 30) |
| `-s NAME`, `--service NAME` | Name of the key, one word without accents (default: `default`) |
| `-n`, `--new_code` | Enter a new key |
| `--version` | Show the version |

If fewer than 2 seconds are left on the current code, the script gives you the next one, so it doesn't expire while you paste it.

Use `-s` to keep several accounts, for example `-s work` and `-s github`, each with its own shortcut.

---

## macOS

1. Install the libraries with the **same** Python you will use in your shortcut:
   ```
   /usr/bin/python3 -m pip install --user pyotp keyring pyperclip
   ```
   (If you use Homebrew Python, use `/opt/homebrew/bin/python3` instead, here and in the shortcuts below.)
2. Run it once in Terminal: `/usr/bin/python3 ~/getTotp.py`. Enter the key. macOS may ask whether Python can use your Keychain; choose **Always Allow**.
3. Bind it to a key. Good tools for this include [Raycast](https://www.raycast.com), [Hammerspoon](https://www.hammerspoon.org) and Espanso. I like Raycast and Hammerspoon (fewer options, but good for this).

**Hammerspoon:** add this to `~/.hammerspoon/init.lua` (menu bar icon → Open Config), then Reload Config. It binds Option+1:

```lua
hs.hotkey.bind({"alt"}, "1", function()
  hs.alert.closeAll()
  hs.alert.show("OTP copied to clipboard!")
  ok, result = hs.applescript('do shell script "/usr/bin/python3 ~/getTotp.py -c"')
  ok, result = hs.applescript('do shell script "/usr/bin/python3 ~/getTotp.py"')
  hs.alert.show(result, hs.styledtext, hs.screen.mainScreen(), 10)
end)
```

**Raycast:** create a Script Command (Raycast Settings → Extensions → Script Commands → Create Script Command) such as `copy-totp.sh`:

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Copy TOTP
# @raycast.mode silent
/usr/bin/python3 ~/getTotp.py -c && echo "TOTP copied"
```

Then give it a hotkey in Raycast's settings.

To delete a stored key: open **Keychain Access** and search for `gettotp`.

---

## Windows 11

1. Install Python from [python.org](https://www.python.org/downloads/windows/) and keep **"py launcher"** checked. Then, in a terminal (Windows Terminal / PowerShell):
   ```
   py -m pip install --user pyotp keyring pyperclip
   ```
2. Copy `getTotp.py` to your user folder, for example `C:\Users\<you>\getTotp.py`, and run it once to enter the key:
   ```
   py "%USERPROFILE%\getTotp.py"
   ```
   In PowerShell, use `py "$env:USERPROFILE\getTotp.py"`. The key is saved in **Credential Manager → Windows Credentials**.
3. Create a keyboard shortcut:
   - Right-click the Desktop → **New → Shortcut**.
   - For the location, enter (`pyw` runs without opening a console window):
     ```
     C:\Windows\pyw.exe "%USERPROFILE%\getTotp.py" -c
     ```
     If `C:\Windows\pyw.exe` doesn't exist (for example with the Microsoft Store Python), use the full path to `pythonw.exe`, which you can find with `where pythonw`.
   - Name it, for example "Copy TOTP", and click Finish.
   - Right-click the shortcut → **Properties** → click in **Shortcut key** and press a combination, for example `Ctrl+Alt+1`, then click OK.

   Windows only honours the shortcut key if the shortcut is on the Desktop or in the Start menu. To keep your Desktop clean, move it to `%APPDATA%\Microsoft\Windows\Start Menu\Programs`.

   Press the keys, then paste with Ctrl+V. For more control, such as a pop-up showing the code, [AutoHotkey](https://www.autohotkey.com) v2 also works:
   ```
   ^!1::Run 'pyw "' EnvGet("USERPROFILE") '\getTotp.py" -c'
   ```

To delete a stored key: open **Credential Manager → Windows Credentials** and remove the `gettotp_code_...` entry.

---

## Linux

1. Install the libraries and a clipboard tool:
   ```
   pip3 install --user pyotp keyring pyperclip
   # X11
   sudo apt install xclip        # or xsel
   # Wayland
   sudo apt install wl-clipboard
   ```
   (Use `dnf`, `pacman`, etc. on other distributions.) If pyperclip fails, the script tries `xclip`, `xsel` and then `wl-copy`.
2. `keyring` needs a Secret Service, which is GNOME Keyring or KWallet on most desktops. Run `python3 ~/getTotp.py` once in a terminal to enter the key. On a headless or minimal system with no keyring service, the script reports "I did not find a keyring manager".
3. Create a keyboard shortcut:
   - **GNOME:** Settings → Keyboard → View and Customize Shortcuts → Custom Shortcuts → **+**. For the command, use `python3 /home/<you>/getTotp.py -c`, then set a shortcut such as Super+1.
   - **KDE Plasma:** System Settings → Shortcuts → Add New → Command or Script, with the same command.
   - Other window managers (i3, sway, etc.) work too, for example:
     `bindsym $mod+1 exec python3 ~/getTotp.py -c`

   To get a desktop notification with the code:
   ```
   sh -c 'python3 ~/getTotp.py -c && notify-send "TOTP" "$(python3 ~/getTotp.py -o)"'
   ```

To delete a stored key: open **Passwords and Keys** (Seahorse) or KWalletManager and search for `gettotp`.
