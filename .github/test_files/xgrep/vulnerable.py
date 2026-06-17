"""Sample file with deliberate security issues to exercise the xgrep action."""

import os
import subprocess


def run_command(user_input):
    # Command injection: untrusted input passed to a shell.
    os.system("echo " + user_input)
    subprocess.call("ping " + user_input, shell=True)


def connect():
    # Hardcoded credentials / secret.
    aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
    aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    return aws_access_key_id, aws_secret_access_key
