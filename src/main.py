import subprocess
from utils.colors import *
from sys import exit
import os
import requests
from yaspin import yaspin
from yaspin.spinners import Spinners
from time import sleep
import re
import subprocess


current_path = os.getcwd()


def is_valid_git_url(url):
    # Matches HTTPS or SSH GitHub URLs
    https_pattern = r'^https://[\w\-]+(\.[\w\-]+)+/[\w\-]+/[\w\-]+\.git$'
    ssh_pattern   = r'^git@[\w\-]+:[\w\-]+/[\w\-]+\.git$'
    return re.match(https_pattern, url) or re.match(ssh_pattern, url)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_choices(msg=""):
    print(f"""===============================
     Commit Automation Tool
===============================
{msg}
[1] Initialize Repository
[2] Choose Branch
[3] Set Commit Loops
[4] Check Settings
[5] Run Automation
[6] About
[7] Exit
===============================""")


def get_main_branch():
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'origin/HEAD'],
            capture_output=True,
            text=True
        )
        main_branch = result.stdout.strip().split('/')[-1]
        return main_branch
    except Exception:
        return None
    
def get_remote():
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True
        )
        remotes = result.stdout.strip().splitlines()

        if not remotes:
            return None 
        
        for line in remotes:
            if line.startswith("origin"):
                parts = line.split()
                if len(parts) >= 2:
                    url = parts[1]
                    return url

        return None
    except Exception:
        return None

def get_current_branch():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()
        return branch if branch else None
    except Exception:
        return None
    
def initialize_repo():
    clear_screen()
    print("==== Initialize Repository ====\n")
    
    os.chdir(current_path)
    print(f"Working in folder: {current_path}\n")
    
    # Check if already a git repo
    if not os.path.exists(os.path.join(current_path, ".git")):
        init = input("No git repo detected. Initialize? (y/n): ").lower()
        if init == "y":
            subprocess.run(["git", "init"])
            print(success("Repository initialized."))
        else:
            print(warning("Initialization cancelled."))
            return None
    
    while True:
        remote = input("Enter remote URL (required): ").strip()
        
        if not remote:
            print(warning("Remote URL is required. Please enter a valid URL."))
            continue
        
        if not is_valid_git_url(remote):
            print(warning("Invalid Git URL. Must be HTTPS or SSH GitHub URL ending with .git"))
            continue
        
        subprocess.run(["git", "remote", "add", "origin", remote])
        print(f"Remote '{info(remote)}' added.")
        break
    
    first_commit = input("Create initial commit now? (y/n): ").lower()
    if first_commit == "y":
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Initial commit"])
        print(success("\nInitial commit done."))

    input("\n\nPress Enter to return to menu...")
    return remote


def get_branches():
    branches = []

    result = subprocess.run(
        ['git', 'branch', '-r'],
        capture_output=True,
        text=True
    )
    raw = result.stdout

    lines = raw.splitlines()

    for line in lines:
        line = line.strip()

        # Skip symbolic HEAD reference
        if "->" in line:
            continue

        # Remove 'origin/' prefix
        if line.startswith("origin/"):
            line = line[len("origin/"):]
        
        if line:
            branches.append(line)
            
    return branches

def select_branch():
    selected_branch = None
    branches = get_branches()
    msg = ""
    while True:
        clear_screen()
        print("==== Existing Branches ====")
        print(warning(msg))
        for i in range(len(branches)):
            print(f"[{i+1}] {branches[i]}")
        print('=======================')
        user_input = input(">> ").strip()

        if user_input == "":
            msg = "Empty input is invalid"
            continue
        elif user_input not in map(str, range(1, len(branches)+1)):
            msg = "Invalid user choice"
            continue
        else:
            msg = ""

        if user_input == 'q':
            return
        
        selected_branch = branches[int(user_input) - 1]

        subprocess.run(['git', 'checkout', f'{selected_branch}'])
        subprocess.run(['git', 'pull', 'origin', f'{get_main_branch()}'])
        break

    input("\n\nPress Enter to return to menu...")
    return selected_branch

def create_branch(branch_name=None):
    new_branch = "" if not branch_name else branch_name
    branches = get_branches()
    msg = ""

    while new_branch == "":
        clear_screen()
        print("Enter new branch name")
        print("=======================")
        print(warning(msg))
        new_branch = input(">> ").strip()

        if new_branch == "":
            msg = "Empty input is invalid"
            continue
        elif new_branch in branches:
            msg = f"Branch --{new_branch.title()}-- already exist"
            new_branch = ""
            continue
        else:
            msg = ""

        if new_branch == 'q':
            return 

        break

    subprocess.run(['git', 'checkout', '-b', f'{new_branch}'])
    subprocess.run(['git', 'push', '-u', 'origin', f'{new_branch}'])
    
    if not branch_name:
        input("\n\nPress Enter to return to menu...")
        
    return new_branch


def auto_create_branch():
    auto_branch_name = f"feature/gitomation-{int(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip(), 16)}"
    return create_branch(auto_branch_name)


def set_branch():
    msg = ""
    selected_branch = None
    while True:
        clear_screen()
        print("==== Set Branch ====")
        print(msg)
        print("""[1] Select existing branch
[2] Create new branch
[3] Auto-generate branch
[4] Back to Main Menu
===========================""")
        user_input = input(">> ").strip()

        # Verify user input
        if user_input == "":
            msg = warning("Empty input is invalid")
            continue
        elif user_input not in ['1', '2', '3', '4']:
            msg = warning("Invalid user choice")
            continue
        else:
            msg = "" if "Selected Branch: " not in msg else msg
            
        if user_input == "1":
            selected_branch = select_branch()
            msg = f"Selected Branch: {success(selected_branch)}"
        elif user_input == "2":
            selected_branch = create_branch()
            msg = f"Selected Branch: {success(selected_branch)}"
        elif user_input == "3":
            selected_branch = auto_create_branch()
            msg = f"Selected Branch: {success(selected_branch)}"
            break
        else:
            break

    input("\n\nPress Enter to return to menu...")
    return selected_branch


def set_commit_loops():
    msg = ""
    loop_number = 3 # Default loop
    while True:
        clear_screen()
        print("==== Set Commit Loops ====")
        print(msg)

        try:
            print("How many loops?")
            loop_number = int(input(">> "))

            if loop_number <= 0:
                msg = warning("Loop number must be greater than 0")
            else:
                msg = ""
                break

        except ValueError:
            msg = warning("Invalid input for number of loops")
        except KeyboardInterrupt:
            break
    
    input("\n\nPress Enter to return to menu...")
    return loop_number


def display_about(loop_number):
    clear_screen()
    print(f"""
{success('                  ==============================')}
                            {success('GITOMATION')}
{success('                  ==============================')}

{info('Description:')}
    This tool automatically creates, pushes, and merges multiple commits
    to make your repository look very active. It is designed for repositories 
    you own.

{success(f"Hint:")}
    Each commit loop creates 2 commits on GitHub. For {loop_number} loops, expect {loop_number*2} commits.

{warning('WARNING:')}
    - This will clutter your commit history.
    - Only use on repositories you control.
    - Make sure the repository is initialized before running automation.
    - First commit must exist or be created during initialization.

    Use this tool responsibly. All commits and merges are automated
    based on your chosen branch and loop settings.

{info('Repository:')} {'https://github.com/Huerte/Gitomation'}
""")
    input("Press Enter to return to menu...")


def display_settings(selected_branch, commit_loops, remote):
    clear_screen()
    print("==== Current Settings ====")
    print(f"""
Repository Path : {warning(current_path)}
Selected Branch : {success(selected_branch)}
Commit Loops    : {error(commit_loops)}
Remote          : {info(remote)}""")
    print("\n===========================")
    input("\nPress Enter to return...")


def generate_content(limit=1, max_length=100):

    try:
        data = requests.get(f"https://api.realinspire.live/v1/quotes/random?limit={limit}&maxLength={max_length}").json()
        content = data[0]['content']
        author = data[0]['author']
        slug = data[0]['authorSlug']

        with open("Inspirational_Quote.md", "a", encoding="utf-8") as file:
            file.write(f'### "{content}" - {author}\n')
        
        return slug
            
    except requests.exceptions.Timeout:
        print("Request timed out")

    except requests.exceptions.ConnectionError:
        print("Network problem (server down?)")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Something went wrong: {e}")


def commit_changes(msg="commit"):
    try:
        subprocess.run(['git', 'add', '.'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        status = subprocess.run(['git', 'diff', '--cached', '--quiet'])
        if status.returncode != 0:
            subprocess.run(['git', 'commit', '-m', msg], check=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def change_branch(branch_name):
    try:
        subprocess.run(['git', 'checkout', branch_name], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def push_changes(selected_branch, remote, msg="commit", merge_to_main=False):
    try:
        subprocess.run(['git', 'push', '-u', 'origin', selected_branch], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if merge_to_main:
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'origin/HEAD'],
                    capture_output=True, text=True, check=True
                )
                main_branch = result.stdout.strip().split('/')[-1]
            except subprocess.CalledProcessError:
                main_branch = 'main'

            subprocess.run(['git', 'checkout', main_branch], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'pull', 'origin', main_branch], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'merge', selected_branch], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'push', 'origin', main_branch], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def run_automation(selected_branch, commit_loops, remote):
    auto_delete_branch = False
    if not remote or remote.strip() == '':
        print("Remote not set. Cannot run automation.")
        return
    
    if not selected_branch or selected_branch.strip() == '' or selected_branch == get_main_branch():
        selected_branch = auto_create_branch()
    
    clear_screen()
    print("==== Running Automation ====")

    proceed = input(warning(f"\nYou are about to push {commit_loops} commits to '{selected_branch}' "
                f"and merge into the default branch. Proceed? (y/n): ")).strip().lower()
    if proceed != 'y':
        print("Operation cancelled by user.")
        return

    branch_condition = input(highlight("\nDo you want to delete the branch after merging? (y/n): ")).strip().lower()

    if branch_condition == 'y':
        auto_delete_branch = True
    
    change_branch(selected_branch)

    clear_screen()

    for i in range(1, commit_loops + 1):
        quote_msg = generate_content()  # returns quote slug
        commit_msg = f"add: inspirational quote @{i} - {quote_msg}" if quote_msg else f"{i}: Commit"

        with yaspin(Spinners.line, text=f"Processing commit {i}/{commit_loops}") as spinner:
            try:
                commit_changes(msg=commit_msg)
                spinner.ok("✔")
            except Exception:
                spinner.fail("✖")
                return

    with yaspin(Spinners.line, text="Merging feature branch into main") as spinner:
        try:
            push_changes(selected_branch=selected_branch, remote=remote, msg="Merge to main", merge_to_main=True)
            spinner.ok("✔")
        except Exception:
            spinner.fail("✖")
            return
    
    if auto_delete_branch:
        with yaspin(Spinners.line, text="Deleting feature branch") as spinner:
            try:
                subprocess.run(['git', 'branch', '-D', selected_branch], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['git', 'push', 'origin', '--delete', selected_branch], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spinner.ok("✔")
            except subprocess.CalledProcessError as e:
                spinner.fail("✖")
                print(f"Git command failed: {e}")
            except Exception as e:
                spinner.fail("✖")
                print(f"Unexpected error: {e}")

    clear_screen()

    input(success("Automation successfully operated. Press Enter to return to menu..."))

    
if __name__ == "__main__":
    
    exit_program = False
    msg = ""
    selected_branch = get_current_branch()
    remote = get_remote()
    loop_number = 3 #Default Loop Value

    while not exit_program:
        clear_screen()
        try:
            display_choices(msg)
            user_input = input(">> ").strip()

            # User validation section
            if user_input == "":
                msg = warning("Empty input is invalid!")
                continue
            elif user_input not in ['1', '2', '3', '4', '5', '6', '7']:
                msg = warning("Invalid choice! Please select a valid option.")
                continue
            else:
                msg = ""

            if user_input == '1':
                remote = initialize_repo()

            elif user_input == '2':
                selected_branch = set_branch()

            elif user_input == '3':
                loop_number = set_commit_loops()

            elif user_input == '4':
                display_settings(selected_branch, loop_number, remote)

            elif user_input == '5':
                run_automation(selected_branch, loop_number, remote)

            elif user_input == '6':
                display_about(loop_number)

            elif user_input == '7':
                exit_program = True


        except KeyboardInterrupt:
            exit_program = True
            print(warning("\nProgram exited by user"))
    
    exit(0)
