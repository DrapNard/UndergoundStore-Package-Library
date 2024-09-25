import hashlib
import base64

HASH_BLOCK_SIZE = 4096

def _calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(HASH_BLOCK_SIZE), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def _verify_file_in_zip(zip_file, file_name, expected_hash):
    with zip_file.open(file_name) as file:
        sha256_hash = hashlib.sha256()
        for byte_block in iter(lambda: file.read(HASH_BLOCK_SIZE), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == expected_hash

def _encode_image_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
