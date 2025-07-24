import re
from datetime import datetime
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section
from langgraph.graph.state import CompiledStateGraph

from src.configuration.kpis import SalesReportRequest
from src.configuration.settings import (
    DOCUMENTATION_DIR,
    STORAGE_DIR,
    TEMP_DIR,
)


def get_request_temp_dir(request: SalesReportRequest) -> Path:
    """
    Get the temporary directory for a specific sales report request.
    """
    path = TEMP_DIR / f"{request.task_id}"
    path.mkdir(parents=True, exist_ok=True)

    return path


def get_all_temp_files(request: SalesReportRequest) -> list[Path]:
    """Get all files in the temporary directory."""
    temp_dir = get_request_temp_dir(request)
    return list(temp_dir.glob("*"))


def get_full_path_to_temp_file(file_name: str, request: SalesReportRequest) -> Path:
    """Get the full path to a temporary file."""
    temp_dir = get_request_temp_dir(request)
    return temp_dir / file_name


def get_sales_history_location(request: SalesReportRequest) -> Path:
    """Helper function to get the input location for sales history data."""
    temp_dir = get_request_temp_dir(request)
    grouping_value = request.grouping_value.replace(" ", "_").lower()
    return temp_dir / f"{grouping_value}_sales_history.csv"


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


def convert_markdown_to_pdf(markdown_path: Path, root_dir: Path) -> Path:
    """
    Convert the given markdown content to a PDF file.
    If the file is in TEMP_DIR, convert absolute paths to relative paths.
    """
    if not markdown_path.exists() or not markdown_path.is_file():
        raise FileNotFoundError(f"The file {markdown_path} does not exist.")

    markdown_content = None
    with open(markdown_path, "r") as file:
        markdown_content = file.read()

    # Set the styling for the PDF
    css = (
        "body {font-family: 'Helvetica', 'Arial', sans-serif;}"
        "h1, h2, h3 {color: #0A2347;}"
        "p, li {line-height: 1.5;}"
    )

    # By default, no table of content is generated in the PDF.
    pdf = MarkdownPdf(toc_level=0)
    pdf_path = markdown_path.with_suffix(".pdf")
    pdf.add_section(
        Section(text=markdown_content, toc=False, root=str(root_dir)), user_css=css
    )
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


def store_graph_as_png(graph: CompiledStateGraph, file_name: str) -> Path:
    """
    Store the graph as a PNG file.
    """
    file_path = DOCUMENTATION_DIR / f"{file_name}.png"
    graph.get_graph().draw_mermaid_png(output_file_path=file_path)

    return file_path
