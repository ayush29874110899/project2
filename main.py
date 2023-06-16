import requests
import langchain
import openai
import os
import nbformat

import requests


def fetch_user_repositories(user_url):
    # Extracting the username from the user URL
    username = user_url.split("/")[-1]

    # Making a GET request to fetch user repositories
    response = requests.get(f"https://api.github.com/users/{username}/repos")

    if response.status_code == 200:
        repositories = response.json()

        # Extracting file information for each repository
        for repo in repositories:
            repo['files'] = fetch_repository_files(repo['full_name'])

        return repositories
    else:
        raise Exception("Failed to fetch user repositories.")


def fetch_repository_files(repository_name):
    # Making a GET request to fetch files in the repository
    response = requests.get(f"https://api.github.com/repos/{repository_name}/contents")

    if response.status_code == 200:
        files = response.json()
        return files
    else:
        raise Exception("Failed to fetch repository files.")


# Step 2: Preprocessing Code for GPT
def preprocess_code(repository):
    # Implement memory management techniques for large repositories and files
    # Preprocess code in repositories (e.g., splitting large files, handling specific file types)

    # Example: Splitting large files into smaller chunks
    file_size_threshold = 1000000  # Set a threshold for file size (1MB in this example)

    for file in repository['files']:
        if file['size'] > file_size_threshold:
            # Split the file into smaller chunks
            file_chunks = split_file(file['path'])
            # Store the file chunks back into the repository object or process them as needed

    # Example: Handling specific file types (e.g., Jupyter notebooks)
    for file in repository['files']:
        if file['type'] == 'notebook':
            # Preprocess Jupyter notebook file
            preprocess_notebook(file['path'])
            # Update the repository object or perform any necessary processing

    # Perform any other preprocessing steps required for your specific use case


# Helper function to split a file into smaller chunks
def split_file(file_path):
    # Create a directory to store the file chunks
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    output_directory = os.path.join(directory, f"{file_name}_chunks")
    os.makedirs(output_directory, exist_ok=True)

    # Read the file content
    with open(file_path, "r") as file:
        content = file.read()

    # Split the file content into smaller chunks
    chunk_size = 1000  # Set the chunk size as per your requirement
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

    # Save each chunk as a separate file
    for i, chunk in enumerate(chunks):
        chunk_file_path = os.path.join(output_directory, f"{file_name}_chunk{i+1}.txt")
        with open(chunk_file_path, "w") as chunk_file:
            chunk_file.write(chunk)

    # Return the list of chunk file paths
    return [os.path.join(output_directory, f"{file_name}_chunk{i+1}.txt") for i in range(len(chunks))]

# Helper function to preprocess a Jupyter notebook file
def preprocess_notebook(file_path):
    # Load the notebook
    notebook = nbformat.read(file_path, as_version=4)

    # Remove unnecessary metadata from the notebook
    notebook.metadata = {}

    # Iterate over the cells and keep only code cells
    notebook.cells = [cell for cell in notebook.cells if cell.cell_type == "code"]

    # Save the preprocessed notebook
    preprocessed_file_path = file_path.replace(".ipynb", "_preprocessed.ipynb")
    nbformat.write(notebook, preprocessed_file_path, version=4)

    # Return the preprocessed file path
    return preprocessed_file_path

# Step 3: Implementing Prompt Engineering for GPT Evaluation
def generate_prompt(repository):
    # Generate prompts or queries for evaluating technical complexity based on repository code

    # Retrieve the code files from the repository
    code_files = repository['files']

    # Initialize an empty list to store the prompts
    prompts = []

    # Iterate over each code file in the repository
    for file in code_files:
        # Get the file path and content
        file_path = file['path']
        file_content = get_file_content(file_path)

        # Generate a prompt/query specific to the file
        prompt = f"Evaluate the technical complexity of file '{file_path}':\n{file_content}"
        
        # Add the prompt to the list
        prompts.append(prompt)

    # Return the list of prompts
    return prompts


def get_file_content(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    return content

# Step 4: Identifying the Most Complex Repository
def calculate_complexity_score(repository):
    # Retrieve the code files from the repository
    code_files = repository['files']
    
    # Initialize a variable to store the total complexity score
    total_complexity_score = 0
    
    # Iterate over each code file in the repository
    for file in code_files:
        # Get the file path and content
        file_path = file['path']
        file_content = get_file_content(file_path)
        
        # Calculate the complexity score for the file using LangChain or other analysis techniques
        file_complexity_score = langchain.calculate_complexity(file_content)
        
        # Update the total complexity score
        total_complexity_score += file_complexity_score
    
    # Return the total complexity score
    return total_complexity_score

# Step 5: Deploying the Solution and Creating User Interface
def analyze_github_user():
    user_url = input("Enter GitHub user URL: ")
    
    try:
        repositories = fetch_user_repositories(user_url)
        most_complex_repo = None
        max_complexity_score = -float('inf')
        
        for repo in repositories:
            preprocess_code(repo)
            prompt = generate_prompt(repo)
            complexity_score = calculate_complexity_score(repo)
            
            if complexity_score > max_complexity_score:
                max_complexity_score = complexity_score
                most_complex_repo = repo
        
        # Display the most complex repository and GPT analysis
        print("Most Complex Repository:")
        print(f"Name: {most_complex_repo['name']}")
        print(f"Description: {most_complex_repo['description']}")
        print(f"URL: {most_complex_repo['html_url']}")
        print("GPT Analysis:")
        # Generate GPT analysis justifying the selection
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Main program execution
analyze_github_user()
