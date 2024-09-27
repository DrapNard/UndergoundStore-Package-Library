import argparse
import base64
from PIL import Image
import uspkg
import shutil
import io
from colorama import init, Fore
from term_image.image import AutoImage

# Initialize colorama for cross-platform support
init(autoreset=True)

def display_image_in_terminal(image_data, left_column_width):
    """Display the image in the terminal using term_image."""
    try:
        # Use term_image to display the image in the terminal
        img = AutoImage(image_data)
        wid, hgt = image_data.size
        img.set_size(height=int(hgt/30), width=int(wid/20))  # Fixed size for the image
        
        print(img)
    except Exception as e:
        print(Fore.RED + f"Failed to display image: {e}")


def create_uspkg(folder, output_file, title, description, image_file):
    """Create a .uspkg package."""
    def update_progress(percent):
        print(Fore.CYAN + f"Progress: {percent:.2f}%")

    try:
        uspkg.create_encrypted_uspkg_with_uid(
            folder, output_file, title, description, image_file,
            update_progress_callback=update_progress
        )
        print(Fore.GREEN + f"USPkg file created: {output_file}")
    except ValueError as e:
        print(Fore.RED + f"Failed to create package: {e}")
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {e}")


def extract_uspkg(uspkg_file, output_dir):
    """Extract a .uspkg package."""
    try:
        uspkg.extract_encrypted_uspkg_with_uid(uspkg_file, output_dir)
        print(Fore.GREEN + f"Files extracted to: {output_dir}")
    except Exception as e:
        print(Fore.RED + f"Failed to extract package: {e}")

def preview_uspkg(uspkg_file):
    """Preview and verify a .uspkg package."""
    try:
        # Verify the package
        is_valid = uspkg.verify_uspkg_file(uspkg_file)
        if is_valid:
            print(Fore.GREEN + "Verification Status: Package is valid")
        else:
            print(Fore.RED + "Verification Status: Package is invalid")
            return

        # Read metadata
        _, _, metadata = uspkg.read_uspkg_metadata(uspkg_file)

        # Prepare metadata information
        title = f"Package Title: {metadata.get('title', 'N/A')}"
        description = f"Package Description: {metadata.get('description', 'N/A')}"

        # Get terminal width to adjust the layout
        terminal_width = shutil.get_terminal_size().columns
        left_column_width = terminal_width // 2  # Divide terminal into two equal parts

        # Print package info on the left
        print(f"{Fore.CYAN}{title.ljust(left_column_width)}", end="\n")
        print(f"{Fore.CYAN}{description.ljust(left_column_width)}", end='\n')

        # Display image on the right, aligned with the above text
        if metadata.get("image"):
            image_data = base64.b64decode(metadata["image"])
            image = Image.open(io.BytesIO(image_data))
            # Display the image using term_image
            display_image_in_terminal(image, left_column_width)
        else:
            print(Fore.YELLOW + "No image available")

    except Exception as e:
        print(Fore.RED + f"Failed to preview package: {e}")

def main():
    parser = argparse.ArgumentParser(description="USPkg Tool CLI for creating, extracting, and previewing .uspkg files.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new .uspkg package")
    create_parser.add_argument("folder", help="Path to the folder to package")
    create_parser.add_argument("output", help="Output path for the .uspkg file")
    create_parser.add_argument("title", help="Title of the package")
    create_parser.add_argument("description", help="Description of the package")
    create_parser.add_argument("image", help="Path to the image file (png, jpg)")
    create_parser.set_defaults(func=lambda args: create_uspkg(args.folder, args.output, args.title, args.description, args.image))

    # Extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract a .uspkg package")
    extract_parser.add_argument("uspkg_file", help="Path to the .uspkg file")
    extract_parser.add_argument("output_dir", help="Directory where the package will be extracted")
    extract_parser.set_defaults(func=lambda args: extract_uspkg(args.uspkg_file, args.output_dir))

    # Preview subcommand
    preview_parser = subparsers.add_parser("preview", help="Preview and verify a .uspkg package")
    preview_parser.add_argument("uspkg_file", help="Path to the .uspkg file")
    preview_parser.set_defaults(func=lambda args: preview_uspkg(args.uspkg_file))

    # Parse arguments
    args = parser.parse_args()

    # Call the appropriate function based on the command
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
