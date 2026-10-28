#!/usr/bin/env python3

"""
MFA TOTP code generation

Code tested with python3
python3 ./getTotp.py --help

The first time you roll this code it will ask you to enter the OTP key

You need to have the following libraries installed pyotp, keyring and pyperclip

    pip3 install --user pyotp keyring pyperclip


@Author: Mike Naso
@Date: Oct 28, 2026
@version: 0.6.0

"""
__author__="Mike Naso"
__license__="GPL"
__version__="0.6.0"
__maintainer__="Mike Naso"
__date__="2026-10-28"


import argparse
import binascii
import getpass
import shutil
import subprocess
import sys
import time

import keyring
import keyring.errors
import pyotp
import pyperclip

KEYRING_SERVICE = "system"
# Below this many seconds left, give the next code so it doesn't expire while being pasted
MIN_SECONDS_LEFT = 2


def keyring_user( service ):
    return "gettotp_code_%s" % service

def normalize_key( key ):
    # Keys are often shown as "abcd efgh ..." , base32 wants uppercase without spaces
    return "".join(key.split()).upper()

def is_valid_key( key ):
    try:
        pyotp.TOTP( key ).now()
        return True
    except (binascii.Error, ValueError, TypeError):
        return False

def enter_key( service ):
    while True:
        try:
            _key=normalize_key( getpass.getpass('Enter the TOTP KEY =>') )
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)
        if _key and is_valid_key( _key ):
            break
        print("Sorry the key is not a valid base32 TOTP secret, try again")
    keyring.set_password(KEYRING_SERVICE, keyring_user( service ), _key)
    return _key

def get_key( service, new_code ):
    # Reading code from the system password manager, this will not work if no keyring backend is available
    try:
        _key=None if new_code else keyring.get_password(KEYRING_SERVICE, keyring_user( service ))
    except keyring.errors.NoKeyringError:
        print("I did not find a keyring manager", file=sys.stderr)
        sys.exit(1)
    except keyring.errors.KeyringError as e:
        print("Unable to read the keyring: %s" % e, file=sys.stderr)
        sys.exit(1)

    if _key and not is_valid_key( _key ):
        print("Sorry the stored key is not valid, please enter it again", file=sys.stderr)
        _key=None
    if not _key:
        _key=enter_key( service )
    return _key

def current_code( totp ):
    _now = time.time()
    _time_remaining = totp.interval - _now % totp.interval
    if _time_remaining < MIN_SECONDS_LEFT:
        return totp.at( _now + totp.interval ), _time_remaining + totp.interval
    return totp.at( _now ), _time_remaining

def copy_to_clipboard( code ):
    try:
        pyperclip.copy( code )
        return True
    except pyperclip.PyperclipException:
        pass
    # Fallback, I saw some problem with pyperclip on some linux distribution
    for _cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["wl-copy"]):
        if shutil.which(_cmd[0]):
            try:
                subprocess.run(_cmd, input=code, text=True, check=True)
                return True
            except (OSError, subprocess.CalledProcessError):
                continue
    print("Unable to copy to the clipboard, install xclip, xsel or wl-copy", file=sys.stderr)
    return False

def range_limit_loop(arg):
    try:
        _value=int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Value must be an integer")
    if _value < 2 or _value > 30:
        raise argparse.ArgumentTypeError("Value must be between 2 and 30")
    return _value

def parse_args():
    parser = argparse.ArgumentParser(add_help=False, description="Generate TOTP (MFA) codes from a key saved in the system keyring")
    for grp in parser._action_groups:
        if grp.title in ('optional arguments', 'options'):
            grp.title = 'arguments'

    parser.add_argument("-h", "--help", action="help", default=argparse.SUPPRESS, help="This help")
    parser.add_argument('-n', '--new_code', action="store_true", help="Asked to enter a new code" )
    parser.add_argument('-l', '--loop', default=None, help="Refresh every N seconds, value between 2 and 30", type=range_limit_loop )
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('-o', '--only_code', action="store_true", help="Display only the code" )
    parser.add_argument('-c', '--clipboard', action="store_true", help="Copy to clipboard" )
    parser.add_argument('-s', '--service', help="Choose the service description in one word no accent, can remain empty", type=str, default='default')
    parser.add_argument('-b', '--beep', action="store_true", help="Beep only if -c option is used" )
    return parser.parse_args()

def main():
    args = parse_args()
    totp = pyotp.TOTP( get_key( args.service, args.new_code ) )
    # In loop mode the line is rewritten in place, otherwise print a normal line
    _end = '\r' if args.loop else '\n'

    while True:
        _code, _time_remaining = current_code( totp )

        if args.only_code:
            print(_code, end=_end, flush=True)
        elif args.clipboard:
            if copy_to_clipboard( _code ) and args.beep:
                print('\a', end='', flush=True)
        else:
            print("Current OTP key: %s Time left %2d " % (_code, _time_remaining), end=_end, flush=True)

        if not args.loop:
            break
        time.sleep(args.loop)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
