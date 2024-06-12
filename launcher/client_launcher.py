##
# Programmer   : Regis Rodolfo Schuch
# Date         : 10 June 2024
#              : Applied Computing Research Group, Unijui University, Brazil
#              : regis.schuch@unijui.edu.br
#              :
# Title        : client_launcher.py 
#              :
# Description  : client_launcher.py defines a command line interface for interacting with the server server_launcher.py, 
#              : which runs on a Morello Board using the Flask framework. The client_launcher interface uses the click 
#              : library to create commands to list, upload, delete, compile and run C programmes on the server_launcher. 
#              : It communicates with the server via HTTP requests using the requests library, with the server URL and 
#              : SSL verification settings defined at the start. Each command corresponds to a specific server endpoint 
#              : and handles the respective actions, such as sending file data, manipulating programme IDs and displaying 
#              : results or errors. The run_menu function provides an interactive text-based menu for the user to choose 
#              : these operations from, ensuring that the entries are valid and processing each option as required. SSL 
#              : verification is optional and is set to False for local development, but can be enabled for use with 
#              : valid SSL certificates.
#              :
# Source       : Some inspiration from
#              : https://trstringer.com/easy-and-nice-python-cli/
#              : https://www.youtube.com/watch?v=m1_48lmAX-Y
#              : https://requests.readthedocs.io/en/latest/
#              : https://peps.python.org/pep-0008/
#              :
# Install      :
# dependencies : The client_launcher.py code was executed on the Unix-enabled CheriBSD Operating System, which extends 
#              : FreeBSD
#              : $ sudo pkg64 install python3
#              :
#              : $ sudo pkg64 install py39-pip
#              : 
#              : 
# Compile and  :
# run          : $ python3 client_launcher.py
#              :
#              :
# Directory    :
# structure    : app-transport
#              : ├── client_launcher.py
#              : ├── data_access
#              : │   └── files.db
#              : ├── executables
#              : ├── keys
#              : │   ├── cert.pem
#              : │   ├── prk.pem
#              : │   └── puk.pem
#              : ├── server_launcher.py
#              : └── uploads
#              :
##   

import click
import requests

SERVER_URL = 'https://127.0.0.1:5000' # Server running on Morello Board for local access
VERIFY_SSL = False  # Set to True if using a valid SSL certificate

@click.group()
def cli():
    """CLI for the backend application."""
    pass

@cli.command(name='list-files')
def list_files():
    """List all uploaded files."""
    response = requests.get(f"{SERVER_URL}/files", verify=VERIFY_SSL)
    if response.status_code == 200:
        files = response.json()
        for file in files:
            click.echo(f"{file['id']}: {file['file_name']} - {file['file_path']}")
            if file.get('executable'):
                click.echo(f"    Executable: Available")
    else:
        click.echo(f"Error: {response.json().get('error')}")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def upload(file_path):
    """Upload a file."""
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f"{SERVER_URL}/upload", files=files, verify=VERIFY_SSL)

    if response.status_code == 200:
        click.echo('File successfully uploaded')
    else:
        click.echo(f"Error: {response.json().get('error')}")

@cli.command()
@click.argument('program_id', type=int)
def delete(program_id):
    """Delete a selected program."""
    response = requests.delete(f"{SERVER_URL}/files/{program_id}", verify=VERIFY_SSL)

    if response.status_code == 200:
        click.echo('Selected program deleted successfully')
    else:
        click.echo(f"Error: {response.json().get('error')}")

@cli.command(name='compile')
@click.argument('program_id', type=int)
def compile_program(program_id):
    """Compile and store a selected program."""
    response = requests.post(f"{SERVER_URL}/compile/{program_id}", verify=VERIFY_SSL)

    if response.status_code == 200:
        click.echo('Compilation successful')
        output = response.json().get('output', '')
        error_output = response.json().get('error_output', '')
        if output:
            click.echo(f"Output:\n{output}")
        if error_output:
            click.echo(f"Error Output:\n{error_output}")
    else:
        click.echo(f"Error: {response.json().get('error')}")
        if response.json().get('output'):
            click.echo(f"Output:\n{response.json().get('output')}")

@cli.command()
@click.argument('program_id', type=int)
def execute(program_id):
    """Execute a compiled program."""
    response = requests.post(f"{SERVER_URL}/execute/{program_id}", verify=VERIFY_SSL)

    if response.status_code == 200:
        click.echo('Execution successful')
        output = response.json().get('output', '')
        error_output = response.json().get('error_output', '')
        if output:
            click.echo(f"Output:\n{output}")
        if error_output:
            click.echo(f"Error Output:\n{error_output}")
    else:
        click.echo(f"Error: {response.json().get('error')}")
        if response.json().get('output'):
            click.echo(f"Output:\n{response.json().get('output')}")

def get_valid_input(prompt, validation_func):
    """Get valid input from the user."""
    while True:
        user_input = input(prompt)
        try:
            return validation_func(user_input)
        except ValueError as e:
            click.echo(f"Error: {e}")

def run_menu():
    while True:
        click.echo("\nMenu:")
        click.echo("1. List files")
        click.echo("2. Upload a file")
        click.echo("3. Delete a program")
        click.echo("4. Compile a program")
        click.echo("5. Execute a program")
        click.echo("6. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            list_files(standalone_mode=False)
        elif choice == '2':
            file_path = input("Enter the path of the file to upload: ")
            try:
                upload([file_path], standalone_mode=False)
            except click.BadParameter as e:
                click.echo(f"Error: {e}")
        elif choice == '3':
            program_id = get_valid_input("Enter the ID of the program to delete: ", int)
            delete([str(program_id)], standalone_mode=False)
        elif choice == '4':
            program_id = get_valid_input("Enter the ID of the program to compile: ", int)
            compile_program([str(program_id)], standalone_mode=False)
        elif choice == '5':
            program_id = get_valid_input("Enter the ID of the program to execute: ", int)
            execute([str(program_id)], standalone_mode=False)
        elif choice == '6':
            click.echo("Exiting...")
            break
        else:
            click.echo("Invalid option. Please try again.")

if __name__ == '__main__':
    run_menu()

