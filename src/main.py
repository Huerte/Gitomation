import subprocess
from utils.colors import *
from sys import exit
import os
import requests
from yaspin import yaspin
from yaspin.spinners import Spinners
import re


current_path = os.getcwd()


def print_separator(char="=", length=60):
    
    print(info(char * length))


def print_section_header(title):
    
    print()
    print_separator()
    print(f"  {highlight(title)}")
    print_separator()
    print()


def print_status(message, status_type="info"):
    
    color_func = {"info": info, "success": success, "warning": warning, "error": error}.get(status_type, info)
    print(f"  {color_func(message)}")


def print_menu_item(number, description):
    
    print(f"  {highlight(f'[{number}]')} {description}")


def is_valid_git_url(url):

    https_pattern = r'^https://[\w\-]+(\.[\w\-]+)+/[\w\-]+/[\w\-]+\.git$'
    ssh_pattern   = r'^git@[\w\-]+:[\w\-]+/[\w\-]+\.git$'
    return re.match(https_pattern, url) or re.match(ssh_pattern, url)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_choices(msg=""):
    
    print_section_header("Gitomation - Commit Automation Tool")
    
    if msg:
        print(f"  {msg}")
        print()
    
    print_menu_item("1", "Initialize Repository")
    print_menu_item("2", "Choose Branch")
    print_menu_item("3", "Set Commit Loops")
    print_menu_item("4", "Check Settings")
    print_menu_item("5", "Run Automation")
    print_menu_item("6", "About")
    print_menu_item("7", "Exit")
    
    print()
    print_separator()
    print()


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
    print_section_header("Initialize Repository")
    
    os.chdir(current_path)
    print_status(f"Working directory: {info(current_path)}", "info")
    print()
    

    if not os.path.exists(os.path.join(current_path, ".git")):
        print_status("No Git repository detected in current directory.", "warning")
        print()
        init = input(f"  {highlight('Initialize new repository?')} (y/n): ").lower().strip()
        if init == "y":
            with yaspin(Spinners.dots, text="Initializing repository") as spinner:
                try:
                    subprocess.run(["git", "init"], check=True, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spinner.ok("[OK]")
                    print_status("Repository initialized successfully.", "success")
                except subprocess.CalledProcessError:
                    spinner.fail("[FAILED]")
                    print_status("Failed to initialize repository.", "error")
                    input("\n  Press Enter to return to menu...")
                    return None
        else:
            print_status("Initialization cancelled.", "warning")
            input("\n  Press Enter to return to menu...")
            return None
        print()
    

    existing_remote = get_remote()
    if existing_remote:
        print_status(f"Remote already configured: {info(existing_remote)}", "info")
        update = input(f"  {highlight('Update remote?')} (y/n): ").lower().strip()
        if update == "y":
            subprocess.run(["git", "remote", "remove", "origin"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            input("\n  Press Enter to return to menu...")
            return existing_remote
        print()
    
    while True:
        print_status("Enter remote repository URL (HTTPS or SSH format)", "info")
        print_status("Example: https://github.com/user/repo.git or git@github.com:user/repo.git", "info")
        print()
        remote = input(f"  {highlight('Remote URL:')} ").strip()
        
        if not remote:
            print_status("Remote URL is required. Please enter a valid URL.", "warning")
            print()
            continue
        
        if not is_valid_git_url(remote):
            print_status("Invalid Git URL format. Must be HTTPS or SSH GitHub URL ending with .git", "error")
            print()
            continue
        
        with yaspin(Spinners.dots, text="Adding remote") as spinner:
            try:
                subprocess.run(["git", "remote", "add", "origin", remote], check=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spinner.ok("[OK]")
                print_status(f"Remote '{info(remote)}' added successfully.", "success")
                break
            except subprocess.CalledProcessError:
                spinner.fail("[FAILED]")
                print_status("Failed to add remote. It may already exist.", "error")
                print()
    
    print()
    first_commit = input(f"  {highlight('Create initial commit now?')} (y/n): ").lower().strip()
    if first_commit == "y":
        with yaspin(Spinners.dots, text="Creating initial commit") as spinner:
            try:
                subprocess.run(["git", "add", "."], check=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["git", "commit", "-m", "Initial commit"], check=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spinner.ok("[OK]")
                print_status("Initial commit created successfully.", "success")
            except subprocess.CalledProcessError:
                spinner.fail("[FAILED]")
                print_status("Failed to create initial commit.", "error")

    print()
    input(f"  {highlight('Press Enter to return to menu...')}")
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


        if "->" in line:
            continue


        if line.startswith("origin/"):
            line = line[len("origin/"):]
        
        if line:
            branches.append(line)
            
    return branches

def select_branch():
    
    selected_branch = None
    branches = get_branches()
    msg = ""
    
    if not branches:
        clear_screen()
        print_section_header("Select Branch")
        print_status("No remote branches found.", "warning")
        print_status("Please create a branch first or ensure remote is configured.", "info")
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
        return None
    
    while True:
        clear_screen()
        print_section_header("Select Existing Branch")
        
        if msg:
            print(f"  {msg}")
            print()
        
        print_status("Available branches:", "info")
        print()
        for i in range(len(branches)):
            current_marker = " (current)" if branches[i] == get_current_branch() else ""
            print(f"  {highlight(f'[{i+1}]')} {info(branches[i])}{current_marker}")
        
        print()
        print_separator()
        print()
        user_input = input(f"  {highlight('Select branch number')} (or 'q' to cancel): ").strip()

        if user_input == "":
            msg = warning("Empty input is invalid. Please select a branch number.")
            continue
        elif user_input.lower() == 'q':
            return None
        elif user_input not in map(str, range(1, len(branches)+1)):
            msg = warning("Invalid selection. Please choose a number from the list.")
            continue
        else:
            msg = ""
        
        selected_branch = branches[int(user_input) - 1]
        
        print()
        print_status(f"Switching to branch: {info(selected_branch)}", "info")
        
        with yaspin(Spinners.dots, text="Checking out branch") as spinner:
            try:
                subprocess.run(['git', 'checkout', selected_branch], check=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spinner.ok("[OK]")
            except subprocess.CalledProcessError:
                spinner.fail("[FAILED]")
                print_status("Failed to checkout branch.", "error")
                print()
                input(f"  {highlight('Press Enter to continue...')}")
                continue
        
        main_branch = get_main_branch()
        if main_branch:
            with yaspin(Spinners.dots, text=f"Pulling latest changes from {main_branch}") as spinner:
                try:
                    subprocess.run(['git', 'pull', 'origin', main_branch], check=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spinner.ok("[OK]")
                    print_status(f"Branch updated with latest changes from {info(main_branch)}.", "success")
                except subprocess.CalledProcessError:
                    spinner.fail("[FAILED]")
                    print_status("Failed to pull changes. Continuing anyway.", "warning")
        
        print_status(f"Successfully switched to branch: {success(selected_branch)}", "success")
        break

    print()
    input(f"  {highlight('Press Enter to return to menu...')}")
    return selected_branch

def create_branch(branch_name=None):
    
    new_branch = "" if not branch_name else branch_name
    branches = get_branches()
    msg = ""

    while new_branch == "":
        clear_screen()
        print_section_header("Create New Branch")
        
        if msg:
            print(f"  {msg}")
            print()
        
        print_status("Enter a name for the new branch.", "info")
        print_status("Branch names should be lowercase, use hyphens for spaces.", "info")
        print()
        new_branch = input(f"  {highlight('Branch name:')} ").strip()

        if new_branch == "":
            msg = warning("Branch name cannot be empty. Please enter a valid name.")
            continue
        elif new_branch.lower() == 'q':
            return None
        elif new_branch in branches:
            msg = warning(f"Branch '{info(new_branch)}' already exists. Please choose a different name.")
            new_branch = ""
            continue
        else:
            msg = ""

        break

    print()
    print_status(f"Creating branch: {info(new_branch)}", "info")
    
    with yaspin(Spinners.dots, text="Creating and checking out branch") as spinner:
        try:
            subprocess.run(['git', 'checkout', '-b', new_branch], check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spinner.ok("[OK]")
        except subprocess.CalledProcessError:
            spinner.fail("[FAILED]")
            print_status("Failed to create branch locally.", "error")
            if not branch_name:
                print()
                input(f"  {highlight('Press Enter to return to menu...')}")
            return None
    
    with yaspin(Spinners.dots, text="Pushing branch to remote") as spinner:
        try:
            subprocess.run(['git', 'push', '-u', 'origin', new_branch], check=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            spinner.ok("[OK]")
            print_status(f"Branch '{success(new_branch)}' created and pushed successfully.", "success")
        except subprocess.CalledProcessError:
            spinner.fail("[FAILED]")
            print_status("Branch created locally but failed to push to remote.", "warning")
            print_status("You may need to configure remote or check your connection.", "info")
    
    if not branch_name:
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
        
    return new_branch


def auto_create_branch():
    auto_branch_name = f"feature/gitomation-{int(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip(), 16)}"
    return create_branch(auto_branch_name)


def set_branch():
    
    msg = ""
    selected_branch = None
    while True:
        clear_screen()
        print_section_header("Branch Management")
        
        if msg:
            print(f"  {msg}")
            print()
        
        current_branch = get_current_branch()
        if current_branch:
            print_status(f"Current branch: {info(current_branch)}", "info")
            print()
        
        print_menu_item("1", "Select existing branch")
        print_menu_item("2", "Create new branch")
        print_menu_item("3", "Auto-generate branch")
        print_menu_item("4", "Back to Main Menu")
        
        print()
        print_separator()
        print()
        user_input = input(f"  {highlight('Select option:')} ").strip()


        if user_input == "":
            msg = warning("Empty input is invalid. Please select an option.")
            continue
        elif user_input not in ['1', '2', '3', '4']:
            msg = warning("Invalid choice. Please select 1, 2, 3, or 4.")
            continue
        else:
            msg = ""
            
        if user_input == "1":
            selected_branch = select_branch()
            if selected_branch:
                msg = f"Selected Branch: {success(selected_branch)}"
        elif user_input == "2":
            selected_branch = create_branch()
            if selected_branch:
                msg = f"Selected Branch: {success(selected_branch)}"
        elif user_input == "3":
            selected_branch = auto_create_branch()
            if selected_branch:
                msg = f"Selected Branch: {success(selected_branch)}"
                break
        else:
            break

    if selected_branch:
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
    return selected_branch


def set_commit_loops():
    
    msg = ""
    loop_number = 3 
    while True:
        clear_screen()
        print_section_header("Set Commit Loops")
        
        if msg:
            print(f"  {msg}")
            print()
        
        print_status("Each loop will create 1 commits on GitHub.", "info")
        print_status("Enter the number of commit loops to execute.", "info")
        print()
        
        try:
            user_input = input(f"  {highlight('Number of loops')} (default: 3): ").strip()
            
            if user_input == "":
                loop_number = 3
                print_status(f"Using default value: {info('3')}", "info")
                break
            
            loop_number = int(user_input)

            if loop_number <= 0:
                msg = warning("Loop number must be greater than 0. Please enter a positive number.")
            elif loop_number > 100:
                confirm = input(f"  {warning('Warning:')} You selected {loop_number} loops ({loop_number*2} commits). Continue? (y/n): ").lower().strip()
                if confirm == 'y':
                    msg = ""
                    break
                else:
                    msg = ""
                    continue
            else:
                msg = ""
                break

        except ValueError:
            msg = warning("Invalid input. Please enter a valid number.")
        except KeyboardInterrupt:
            break
    
    print()
    print_status(f"Commit loops set to: {success(loop_number)} ({loop_number} total commits)", "success")
    print()
    input(f"  {highlight('Press Enter to return to menu...')}")
    return loop_number


def display_about(loop_number):
    
    clear_screen()
    print()
    print_separator("=", 60)
    print(f"  {highlight('GITOMATION')}")
    print(f"  {info('Commit Automation Tool')}")
    print_separator("=", 60)
    print()
    
    print_section_header("Description")
    print_status("This tool automatically creates, pushes, and merges multiple commits", "info")
    print_status("to make your repository look very active.", "info")
    print_status("It is designed for repositories you own.", "info")
    print()
    
    print_section_header("How It Works")
    print_status(f"Each commit loop creates 1 commits on GitHub.", "info")
    print()
    
    print_section_header("Important Warnings")
    print_status("This will clutter your commit history.", "warning")
    print_status("Only use on repositories you control.", "warning")
    print_status("Make sure the repository is initialized before running automation.", "warning")
    print_status("First commit must exist or be created during initialization.", "warning")
    print()
    print_status("Use this tool responsibly. All commits and merges are automated", "info")
    print_status("based on your chosen branch and loop settings.", "info")
    print()
    
    print_section_header("Repository")
    print_status("https://github.com/Huerte/Gitomation", "info")
    print()
    
    input(f"  {highlight('Press Enter to return to menu...')}")


def display_settings(selected_branch, commit_loops, remote):
    
    clear_screen()
    print_section_header("Current Settings")
    
    print_status("Repository Configuration", "info")
    print()
    

    path_status = "configured" if os.path.exists(os.path.join(current_path, ".git")) else "not initialized"
    path_color = "success" if path_status == "configured" else "warning"
    print(f"  {highlight('Repository Path:')} {current_path}")
    print(f"    Status: ", end="")
    print_status(path_status, path_color)
    print()
    

    if selected_branch:
        current = get_current_branch()
        branch_display = f"{success(selected_branch)}"
        if current == selected_branch:
            branch_display += f" {info('(current)')}"
        print(f"  {highlight('Selected Branch:')} {branch_display}")
    else:
        print(f"  {highlight('Selected Branch:')} {warning('Not set')}")
    print()
    

    print(f"  {highlight('Commit Loops:')} {info(commit_loops)} ({commit_loops * 2} total commits)")
    print()
    

    if remote:
        print(f"  {highlight('Remote URL:')} {info(remote)}")
    else:
        print(f"  {highlight('Remote URL:')} {warning('Not configured')}")
    print()
    
    print_separator()
    print()
    input(f"  {highlight('Press Enter to return to menu...')}")


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
        print_status("Request timed out. Using fallback content.", "warning")
        return None

    except requests.exceptions.ConnectionError:
        print_status("Network connection problem. Using fallback content.", "warning")
        return None

    except requests.exceptions.HTTPError as e:
        print_status(f"HTTP error occurred: {e}. Using fallback content.", "warning")
        return None

    except requests.exceptions.RequestException as e:
        print_status(f"Request failed: {e}. Using fallback content.", "warning")
        return None


def commit_changes(msg="commit"):
    
    try:
        subprocess.run(['git', 'add', '.'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        status = subprocess.run(['git', 'diff', '--cached', '--quiet'])
        if status.returncode != 0:
            subprocess.run(['git', 'commit', '-m', msg], check=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        return False
    except subprocess.CalledProcessError as e:
        print_status(f"Git command failed: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False


def change_branch(branch_name):
    
    try:
        subprocess.run(['git', 'checkout', branch_name], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to checkout branch: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False


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
            return True

        return True

    except subprocess.CalledProcessError as e:
        print_status(f"Git command failed: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        return False


def run_automation(selected_branch, commit_loops, remote):
    
    auto_delete_branch = False
    

    if not remote or remote.strip() == '':
        clear_screen()
        print_section_header("Automation Error")
        print_status("Remote repository not configured.", "error")
        print_status("Please initialize the repository first (Option 1).", "info")
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
        return
    

    if not selected_branch or selected_branch.strip() == '' or selected_branch == get_main_branch():
        print()
        print_status("No valid branch selected. Auto-generating branch...", "info")
        selected_branch = auto_create_branch()
        if not selected_branch:
            print_status("Failed to create branch. Automation cancelled.", "error")
            print()
            input(f"  {highlight('Press Enter to return to menu...')}")
            return
    

    clear_screen()
    print_section_header("Automation Confirmation")
    
    main_branch = get_main_branch() or "main"
    total_commits = commit_loops
    
    print_status("Automation Summary", "info")
    print()
    print(f"  {highlight('Target Branch:')} {info(selected_branch)}")
    print(f"  {highlight('Commit Loops:')} {info(commit_loops)}")
    print(f"  {highlight('Total Commits:')} {info(total_commits)}")
    print(f"  {highlight('Merge Target:')} {info(main_branch)}")
    print()
    print_separator()
    print()
    print_status(f"You are about to create {info(total_commits)} commits and merge into {info(main_branch)}.", "warning")
    print()
    
    proceed = input(f"  {highlight('Proceed with automation?')} (y/n): ").strip().lower()
    if proceed != 'y':
        print()
        print_status("Automation cancelled by user.", "info")
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
        return

    print()
    branch_condition = input(f"  {highlight('Delete branch after merging?')} (y/n): ").strip().lower()
    if branch_condition == 'y':
        auto_delete_branch = True
        print_status("Branch will be deleted after successful merge.", "info")
    

    print()
    print_separator("-", 60)
    print()
    print_status(f"Switching to branch: {info(selected_branch)}", "info")
    
    if not change_branch(selected_branch):
        print_status("Failed to switch branch. Automation cancelled.", "error")
        print()
        input(f"  {highlight('Press Enter to return to menu...')}")
        return
    
    print_status("Branch switched successfully.", "success")
    print()
    

    print_separator("=", 60)
    print()
    print_section_header("Running Automation")
    print()

    clear_screen()
    
    successful_commits = 0
    failed_commits = 0
    
    for i in range(1, commit_loops + 1):
        quote_msg = generate_content()
        commit_msg = f"add: inspirational quote @{i} - {quote_msg}" if quote_msg else f"commit: automation loop {i}"
        
        with yaspin(Spinners.dots, text=f"Processing commit {i}/{commit_loops}") as spinner:
            if commit_changes(msg=commit_msg):
                spinner.ok("[OK]")
                successful_commits += 1
            else:
                spinner.fail("[FAILED]")
                failed_commits += 1
    

    print()
    with yaspin(Spinners.dots, text=f"Pushing {successful_commits} commits to {selected_branch}") as spinner:
        if push_changes(selected_branch=selected_branch, remote=remote, msg="Push commits", merge_to_main=False):
            spinner.ok("[OK]")
        else:
            spinner.fail("[FAILED]")
            print_status("Failed to push commits. Automation stopped.", "error")
            print()
            input(f"  {highlight('Press Enter to return to menu...')}")
            return
    
    with yaspin(Spinners.dots, text=f"Merging {selected_branch} into {main_branch}") as spinner:
        if push_changes(selected_branch=selected_branch, remote=remote, msg="Merge to main", merge_to_main=True):
            spinner.ok("[OK]")
        else:
            spinner.fail("[FAILED]")
            print_status("Failed to merge branch. Automation stopped.", "error")
            print()
            input(f"  {highlight('Press Enter to return to menu...')}")
            return
    

    if auto_delete_branch:
        with yaspin(Spinners.dots, text=f"Deleting branch {selected_branch}") as spinner:
            try:
                subprocess.run(['git', 'branch', '-D', selected_branch], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['git', 'push', 'origin', '--delete', selected_branch], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                spinner.ok("[OK]")
            except subprocess.CalledProcessError as e:
                spinner.fail("[FAILED]")
                print_status(f"Failed to delete branch: {e}", "warning")
            except Exception as e:
                spinner.fail("[FAILED]")
                print_status(f"Unexpected error: {e}", "error")
    

    clear_screen()
    print()
    print_separator("=", 60)
    print()
    print_section_header("Automation Complete")
    print()
    
    print_status("Summary", "info")
    print()
    print(f"  {highlight('Successful Commits:')} {success(successful_commits)}")
    if failed_commits > 0:
        print(f"  {highlight('Failed Commits:')} {error(failed_commits)}")
    print(f"  {highlight('Branch Merged:')} {success('Yes')}")
    if auto_delete_branch:
        print(f"  {highlight('Branch Deleted:')} {success('Yes')}")
    print()
    print_separator("=", 60)
    print()
    
    input(f"  {highlight('Press Enter to return to menu...')}")

    
if __name__ == "__main__":
    
    exit_program = False
    msg = ""
    selected_branch = get_current_branch()
    remote = get_remote()
    loop_number = 3

    while not exit_program:
        clear_screen()
        try:
            display_choices(msg)
            user_input = input(f"  {highlight('Select option:')} ").strip()


            if user_input == "":
                msg = warning("Empty input is invalid. Please select an option.")
                continue
            elif user_input not in ['1', '2', '3', '4', '5', '6', '7']:
                msg = warning("Invalid choice. Please select a number from 1 to 7.")
                continue
            else:
                msg = ""

            if user_input == '1':
                remote = initialize_repo()

                selected_branch = get_current_branch()

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
                clear_screen()
                print()
                print_separator()
                print_status("Thank you for using Gitomation!", "info")
                print_separator()
                print()
                exit_program = True

        except KeyboardInterrupt:
            exit_program = True
            clear_screen()
            print()
            print_separator()
            print_status("Program interrupted by user.", "warning")
            print_separator()
            print()
        except Exception as e:
            clear_screen()
            print()
            print_section_header("Unexpected Error")
            print_status(f"An unexpected error occurred: {e}", "error")
            print_status("Please report this issue if it persists.", "info")
            print()
            input(f"  {highlight('Press Enter to continue...')}")
            msg = ""
    
    exit(0)
