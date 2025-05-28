import os.path
import csv
import json
import hashlib
import mimetypes

class File:
    """
    This class represents a file on the file system.
    """
    def __init__(self, *path):
        """
        Initializes the File object with the specified path.

        Args:
            Path (str): The path to the file.
        """
        self.Path = "" if path[0] == None else os.path.join(*path)
        self.Content = None
        if self.Exists():
            self.Content = open(self.Path, 'r', encoding='utf-8')

    def __enter__(self):
        """
        Enter method for context management support.
        """
        if not self.Content:
            self.Open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit method for context management support.
        Ensures that the file is properly closed.
        """
        if self.Content:
            self.Content.close()

    def Open(self):
        """
        Opens the file in read-only mode and stores the entire content in self.Content.

        Returns:
            bool: True if the file was read successfully, False otherwise.
        """
        if self.Exists():
            try:
                self.Content = open(self.Path, 'r', encoding='utf-8')
            except (FileNotFoundError, UnicodeDecodeError) as e:
                print(f"Error reading file content: {e}")
        else:
            self.Content = None
            print(f"File not found: {self.Path}")
        return self

    def Close(self):
        """
        Closes the file if it is open.
        """
        if self.Content:
            self.Content.close()
            self.Content = None

    def Exists(self):
        """
        Checks if the file exists at the specified path.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.exists(self.Path)

    def GetBasename(self):
        """
        Returns the filename without the directory path.

        Returns:
            str: The filename.
        """
        return os.path.basename(self.Path)

    def GetDirname(self):
        """
        Returns the directory path of the file.

        Returns:
            str: The directory path.
        """
        return os.path.dirname(self.Path)

    def GetAbsolutePath(self):
        """
        Returns the absolute path of the file.

        Returns:
            str: The absolute path.
        """
        return os.path.abspath(self.Path)

    def GetFileSize(self):
        """
        Returns the size of the file in bytes.

        Returns:
            int: The size of the file in bytes, or None if the file does not exist.
        """
        if self.Exists():
            return os.path.getsize(self.Path)
        return None

    def GetMimeType(self):
        """
        Returns the MIME type of the file based on its extension.

        Returns:
            str: The MIME type of the file, or None if it cannot be determined.
        """
        mime_type, _ = mimetypes.guess_type(self.Path)
        return mime_type
    
    def Create(self):
        """
        Creates the file and its directory structure if they don't exist.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Create directories if they don't exist (avoid race conditions)
        os.makedirs(self.GetDirname(), exist_ok=True)

        # Create the empty file
        try:
            with open(self.Path, 'x', encoding='utf-8') as f:
                pass  # Empty file creation
        except FileExistsError:
            pass  # File already exists, ignore

        return self  # Return self to allow chaining
    
    def Delete(self):
        """
        Deletes the file from the file system.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        if self.Exists():
            self.Content.close()
            try:
                os.remove(self.Path)
                return self
            except FileNotFoundError:
                print(f"File not found: {self.Path}")
            except PermissionError:
                print(f"Permission error deleting file: {self.Path}")
        return self
    
    def Recreate(self):
        """
        Deletes the file if it exists and then creates a new empty file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        if self.Exists():
            self.Delete()

        # Create the empty file
        self.Create()
        self.Open()
        return self  # Return self to allow chaining
    
    def Read(self):
        """
        Reads the entire content of the file line by line and returns a list of strings.

        Returns:
            list[str]: A list of lines from the file, or None if there's an error.
        """
        return self.Content.read() if self.Content else None

    def ReadLines(self):
        """
        Reads the entire content of the file line by line and returns a list of strings.

        Returns:
            list[str]: A list of lines from the file, or None if there's an error.
        """
        return self.Content.readlines() if self.Content else None
    
    def Append(self, *content):
        """
        Appends a line of text to the end of the file with a newline character.

        Args:
            content (str): The line of text to write.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Open the file in append mode with UTF-8 encoding
        with open(self.Path, 'a', encoding='utf-8') as f:
            for line in content:
                f.write(line + "\n")  # Add newline character

        return self  # Return self to allow chaining

    def Overwrite(self, *content):
        """
        Overwrites the entire content of the file with the provided content.

        Args:
            content (str): The content to write to the file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Open the file in write mode with UTF-8 encoding
        with open(self.Path, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line + "\n")

        return self  # Return self to allow chaining

    def ReadAsJson(self):
        """
        Reads the contents of the file as JSON and returns the parsed data.

        Returns:
            object: The parsed JSON data, or None if there's an error.
        """
        try:
            return json.load(self.Content)
        except (json.JSONDecodeError) as e:
            return None
    
    def WriteAsJson(self, content):
        """
        Saves the provided content as JSON to the file.

        Args:
            content (object): The content to serialize and write as JSON.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        # Ensure content is JSON serializable
        if not isinstance(content, (dict, list, str, int, float, bool, type(None))):
            raise TypeError("Content must be JSON serializable")

        # Open the file in write mode with UTF-8 encoding
        with open(self.Path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)  # Improved formatting

        return self  # Return self to allow chaining
    
    def ReadAsCsv(self):
        """
        Reads the contents of the file as CSV and returns a list of rows.

        Returns:
            list[list[str]]: A list of rows from the CSV file, or None if there's an error.
        """
        try:
            with open(self.Path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                return [row for row in reader]
        except (FileNotFoundError, csv.Error) as e:
            print(f"Error reading file as CSV: {e}")
            return None

    def WriteAsCsv(self, rows):
        """
        Saves the provided rows as CSV to the file.

        Args:
            rows (list[list[str]]): A list of rows to write to the CSV file.

        Returns:
            File: The File object itself, allowing for chaining.
        """
        if not all(isinstance(row, list) for row in rows):
            raise TypeError("Content must be a list of lists (rows) to write as CSV")

        try:
            with open(self.Path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        except (FileNotFoundError, csv.Error) as e:
            print(f"Error writing file as CSV: {e}")

        return self  # Return self to allow chaining
    
    def IsEmpty(self):
        """
        Checks if the file is empty (has zero size).

        Returns:
            bool: True if the file is empty, False otherwise.
        """
        if self.Exists():
            return os.path.getsize(self.Path) == 0  # Check file size
        else:
            return True  # Consider a non-existent file as empty
    
    def Hash(self, algorithm = 'sha256'):
        """
        Calculates the hash of the file content using the specified algorithm.

        Args:
            algorithm (str, optional): The hashing algorithm to use. Defaults to 'sha256'.

        Returns:
            str: The hash value of the file content in hexadecimal format, or None if there's an error.
        """
        if not self.Exists():
            print(f"File not found: {self.Path}")
            return None

        try:
            # Open the file in binary read mode
            with open(self.Path, 'rb') as f:
                # Create the hash object
                hasher = hashlib.new(algorithm)
                # Read the file content in chunks and update the hash
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
                # Return the hash digest in hexadecimal format
                return hasher.hexdigest()
        except FileNotFoundError:
            print(f"File not found: {self.Path}")
            return None

    def Backup(self):
        """
        Creates a backup of the file with a timestamp appended to the filename.

        Returns:
            str: The path to the backup file.
        """
        import time
        backup_path = f"{self.Path}.{time.strftime('%Y%m%d%H%M%S')}.bak"
        try:
            with open(self.Path, 'r', encoding='utf-8') as original:
                with open(backup_path, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())
        except FileNotFoundError:
            print(f"File not found for backup: {self.Path}")
            return None

        return backup_path
