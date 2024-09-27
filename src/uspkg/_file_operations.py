import os
import zipfile
import io
from ._utils import _calculate_sha256

def _zip_folder(folder_path, update_progress_callback=None):
    metadata = {"files": {}, "zipHash": ""}
    zip_file_path = 'temp_folder.zip'

    # Calculate total number of files
    total_files = sum([len(files) for _, _, files in os.walk(folder_path)])
    
    file_count = 0
    with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)
                metadata["files"][arcname] = _calculate_sha256(file_path)
                
                file_count += 1
                progress_percent = (file_count / total_files) * 100
                if update_progress_callback:
                    update_progress_callback(progress_percent)
                
    metadata["zipHash"] = _calculate_sha256(zip_file_path)
    return zip_file_path, metadata

def _extract_zip(zip_data, output_dir):
    with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
        zip_ref.extractall(output_dir)
