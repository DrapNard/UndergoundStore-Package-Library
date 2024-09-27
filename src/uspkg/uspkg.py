import os
import uuid
import io
import zipfile
from ._encryption import _generate_key_from_uid, _encrypt_data, _decrypt_data
from ._file_operations import _zip_folder
from .metadata import write_uspkg, read_uspkg_metadata
from ._utils import _encode_image_to_base64, _verify_file_in_zip, _calculate_sha256

def create_encrypted_uspkg_with_uid(folder_path, output_file, title, description, image_path, _type, main_exe, update_progress_callback=None):
    if len(title) < 1 or len(title) > 100:
        raise ValueError("Title must contain 1-100 characters.")
    
    uid = str(uuid.uuid4())
    key = _generate_key_from_uid(uid)
    
    # Encode image as base64
    image_data = _encode_image_to_base64(image_path)
    
    metadata = {
        "UID": uid,
        "title": title,
        "description": description,
        "image": image_data,
        "type": _type,
        "mainExe": main_exe,
        "zipEncryptedHash": "",
        "zipHash": "",
        "files": {}
    }
    
    zip_file_path, zip_metadata = _zip_folder(folder_path, update_progress_callback)
    metadata["files"] = zip_metadata["files"]
    metadata["zipHash"] = zip_metadata["zipHash"]
    
    with open(zip_file_path, 'rb') as f_zip:
        zip_data = f_zip.read()
    
    encrypted_zip_data, iv = _encrypt_data(key, zip_data)

    metadata['zipEncryptedHash'] = _calculate_sha256(encrypted_zip_data)
    
    write_uspkg(output_file, encrypted_zip_data, iv, metadata)
    os.remove(zip_file_path)

def verify_uspkg_file(uspkg_file, uid=None):
    try:
        encrypted_zip_data, iv, metadata = read_uspkg_metadata(uspkg_file)
        title = metadata.get("title", "")
        if len(title) < 1 or len(title) > 100:
            return False
        
        encrypted_zip_hash = _calculate_sha256(io.BytesIO(encrypted_zip_data).read())
        if encrypted_zip_hash != metadata.get('zipEncryptedHash', ''):
            print("Encrypted ZIP hash does not match.")
            return False

        uid = uid or metadata["UID"]
        key = _generate_key_from_uid(uid)
        zip_data = _decrypt_data(key, iv, encrypted_zip_data)
        
        zip_hash = _calculate_sha256(io.BytesIO(zip_data).read())
        if zip_hash != metadata.get('zipHash', ''):
            print("ZIP hash does not match.")
            return False

        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
            for file_name, stored_hash in metadata["files"].items():
                if file_name not in zip_file.namelist():
                    return False
                if not _verify_file_in_zip(zip_file, file_name, stored_hash):
                    return False
        return True
    except Exception as e:
        print(f"Error during verification: {e}")
        return False

def extract_encrypted_uspkg_with_uid(uspkg_file, output_dir):
    """
    Extract the contents of an encrypted .uspkg file.
    
    Args:
    uspkg_file (str): Path to the .uspkg file to be extracted.
    output_dir (str): Directory where the extracted files will be saved.
    """
    try:
        # Read metadata and encrypted content
        encrypted_zip_data, iv, metadata = read_uspkg_metadata(uspkg_file)
        
        # Generate the key from the UID
        key = _generate_key_from_uid(metadata["UID"])
        
        # Decrypt the ZIP data
        zip_data = _decrypt_data(key, iv, encrypted_zip_data)
        
        # Extract the ZIP file into the output directory
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        print(f"Extraction complete. Files saved to {output_dir}")
    except Exception as e:
        print(f"Error during extraction: {e}")