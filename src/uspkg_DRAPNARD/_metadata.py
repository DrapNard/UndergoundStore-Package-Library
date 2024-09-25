import msgpack
import os

METADATA_SIZE_BYTES = 8
AES_BLOCK_SIZE = 16

def _write_uspkg(output_file, encrypted_zip_data, iv, metadata):
    packed_msgpack = msgpack.packb(metadata, use_bin_type=True)
    with open(output_file, 'wb') as f_out:
        f_out.write(encrypted_zip_data)
        f_out.write(iv)
        f_out.write(packed_msgpack)
        f_out.write(len(packed_msgpack).to_bytes(METADATA_SIZE_BYTES, 'big'))

def _read_uspkg_metadata(uspkg_file):
    with open(uspkg_file, 'rb') as f_in:
        f_in.seek(0, os.SEEK_END)
        file_size = f_in.tell()
        f_in.seek(-METADATA_SIZE_BYTES, os.SEEK_END)
        metadata_length = int.from_bytes(f_in.read(METADATA_SIZE_BYTES), 'big')
        encrypted_data_size = file_size - (metadata_length + METADATA_SIZE_BYTES + AES_BLOCK_SIZE)
        f_in.seek(file_size - (metadata_length + METADATA_SIZE_BYTES + AES_BLOCK_SIZE))
        iv = f_in.read(AES_BLOCK_SIZE)
        f_in.seek(file_size - (metadata_length + METADATA_SIZE_BYTES))
        packed_msgpack = f_in.read(metadata_length)
        f_in.seek(0)
        encrypted_zip_data = f_in.read(encrypted_data_size)
        metadata = msgpack.unpackb(packed_msgpack, raw=False)
    return encrypted_zip_data, iv, metadata
