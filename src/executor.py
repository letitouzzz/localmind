"""Extraction et validation des commandes [EXEC]"""

import re
import shlex

KNOWN_BINARIES = {
    "curl", "wget", "xdg-open", "nmap", "shodan", "python3", "python",
    "ls", "cat", "echo", "git", "docker", "systemctl", "ping",
    "traceroute", "dig", "nslookup", "ssh", "scp", "maltego",
    "spiderfoot", "sf.py", "firefox", "code", "gedit", "nano", "vim",
}


def extract_exec_commands(text: str) -> list:
    return re.findall(r"\[EXEC\](.*?)\[/EXEC\]", text, re.DOTALL)


def is_plausible_command(cmd: str) -> bool:
    cmd = cmd.strip()
    if not cmd:
        return False
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return False
    if not tokens:
        return False

    first = tokens[0].lower()
    if first.startswith(("./", "/", "~")):
        return True
    if first.split("/")[-1] in KNOWN_BINARIES:
        return True

    french_stopwords = {"de", "du", "la", "le", "un", "une", "site", "web", "sur", "pour"}
    if any(t.lower() in french_stopwords for t in tokens):
        return False
    return False
