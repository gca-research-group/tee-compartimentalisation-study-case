import click
import requests
import subprocess
import os

SERVER_URL = 'https://127.0.0.1:5000'  # Server running on Morello Board for local access
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

        executable_path = response.json().get('executable_path')
        if executable_path:
            click.echo("Running in the current terminal:")
            # Run directly in the current terminal with proper interactivity
            subprocess.run([executable_path])
        else:
            click.echo("Executable path not provided.")
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
        click.echo("\n|Menu:                  |")
        click.echo("-------------------------")
        click.echo("| 1. List files         |")
        click.echo("| 2. Upload a file      |")
        click.echo("| 3. Delete a program   |")
        click.echo("| 4. Compile a program  |")
        click.echo("| 5. Execute a program  |")
        click.echo("| 6. Exit               |")
        click.echo("-------------------------")
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
