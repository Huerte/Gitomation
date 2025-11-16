RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
RESET = "\033[0m"


def info(msg): 
    return f"{BLUE}{msg}{RESET}"

def success(msg): 
    return f"{GREEN}{msg}{RESET}"

def warning(msg): 
    return f"{YELLOW}{msg}{RESET}"

def error(msg): 
    return f"{RED}{msg}{RESET}"

def highlight(msg): 
    return f"{CYAN}{msg}{RESET}"
