import re
from datetime import datetime
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

from src.configuration.settings import STORAGE_DIR, TEMP_DIR


def store_response_with_timestamp(
    response: str, file_name: str, temp: bool = True
) -> Path:
    """
    Store the agent's response in a file.
    """
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    if temp:
        file_path = TEMP_DIR / f"{timestamp} - {file_name}.md"
    else:
        file_path = STORAGE_DIR / f"{timestamp} - {file_name}.md"

    with open(file_path, "a") as file:
        file.write(response)

    return file_path


def convert_markdown_to_pdf(markdown_path: Path) -> Path:
    """
    Convert the given markdown content to a PDF file.
    If the file is in TEMP_DIR, convert absolute paths to relative paths.
    """
    if not markdown_path.exists() or not markdown_path.is_file():
        raise FileNotFoundError(f"The file {markdown_path} does not exist.")

    markdown_content = None
    with open(markdown_path, "r") as file:
        markdown_content = file.read()

    # By default, no table of content is generated in the PDF.
    pdf = MarkdownPdf(toc_level=0)
    pdf_path = markdown_path.with_suffix(".pdf")
    pdf.add_section(Section(text=markdown_content, toc=False, root=str(TEMP_DIR)))
    pdf.save(pdf_path)

    return pdf_path


def move_file_to_storage(file_path: Path) -> Path:
    """
    Move a file to the storage directory.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    storage_path = STORAGE_DIR / file_path.name
    file_path.rename(storage_path)

    return storage_path


def clean_temp_folder() -> None:
    """
    Clean the temporary folder by removing all files in TEMP_DIR.
    """
    if not TEMP_DIR.exists() or not TEMP_DIR.is_dir():
        return

    for item in TEMP_DIR.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            # Optionally, remove directories as well
            item.rmdir()  # This will only work if the directory is empty


def get_all_files_mentioned_in_response(response: str) -> list[str]:
    """
    Extract all file names mentioned in the response string.

    Args:
        response (str): The response string containing file names.

    Returns:
        list[str]: A list of file names extracted from the response.
    """
    # Use regex to find .png or .csv files mentioned in the response
    file_pattern = r"\b[\w\-_]+\.(?:png|csv)\b"
    found_files: list[str] = re.findall(file_pattern, response)
    return found_files
