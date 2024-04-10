import typing


FILE_TYPES = {
    'folder': {
        'extension': '',
    },
    'dashboard': {
        'extension': '.dbd',
    },
    'worksheet': {
        'extension': '.ws',
        # 'max_size': 500,
        # 'operation': ...
        # More properties to be added for generalization.
    }
    # Add more file types as needed.
}

class File:
    # Create a File object that contains id, name, filetype, folder (optional).
    def __init__(self, fileId: int, fileName: str, fileType: str, folderId=None):
        self.id = fileId
        self.name = fileName
        self.type = fileType
        self.folder_id = folderId  # Keep track of the folder
        self.extension = self.get_extension(fileType)  # File extension

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.type

    def get_id(self) -> int:
        return self.id

    def get_extension(self, fileType: str) -> str:
        return FILE_TYPES.get(fileType, {}).get('extension', '')

    def get_full_path(self, fileSystem) -> str:
        path = [self.name]
        # This will be used to traverse up the folder hierarchy.
        curr_folderId = self.folder_id
        # Loop up of the hierarchy.
        while curr_folderId is not None:
            curr_folder = fileSystem.files[curr_folderId]
            # Insert the folder at beginning of the list.
            path.insert(0, curr_folder.name)
            # Update, and move up.
            curr_folderId = curr_folder.folder_id
        return "/" + "/".join(path)

    def get_relative_path(self, file_system, start_folder_id) -> str:
        if start_folder_id not in file_system.files or file_system.files[start_folder_id].type != 'folder':
            print(f"Invalid start folder ID: {start_folder_id}")
            return ""

        path = [self.name]
        curr_folder_id = self.folder_id

        while curr_folder_id is not None and curr_folder_id != start_folder_id:
            curr_folder = file_system.files[curr_folder_id]
            path.insert(0, curr_folder.name)
            curr_folder_id = curr_folder.folder_id

        if curr_folder_id is None:
            print(f"File {self.name} is not within folder {file_system.files[start_folder_id].name}")
            return ""
        path.insert(0, file_system.files[start_folder_id].name)


        return '/'.join(path)

class FileSystem:

    def __init__(self):
        # Initializing root folder.
        self.files = {0: File(0, "MyDocuments", "folder", None)}
        # Keep track of total count of different types of the file.
        self.file_counts = {"dashboard": 0, "worksheet": 0}
        # Tt should increment by 1 everytime a new file is added, results in unique ID
        self.next_id = 1

    def get_total_dashboards(self) -> int:
        return self.file_counts.get("dashboard", 0)

    def get_total_worksheets(self) -> int:
        return self.file_counts.get("worksheet", 0)

    def add_new_file(self, fileName: str, fileType: str, folderId: int) -> None:
        # Check if the fileType is valid.
        if not self.valid_fileType(fileType):
            return
        # Check if folder_id is valid.
        if not self.valid_folder(folderId):
            return
        # Create new File object, assigning the properties.
        new_file = File(self.next_id, fileName, fileType, folderId)
        # Update the count for the according type.
        if fileType in self.file_counts:
            self.file_counts[fileType] += 1

        self.next_id += 1
        folder_name = self.files[folderId].get_name()
        # Add the new_file to the file system.
        self.files[new_file.id] = new_file
        #print(f"ID[{new_file.id}] Successfully Added: ~/{folder_name}/{new_file.get_name()}{new_file.extension} ")
        #print(f"ID[{new_file.id}] Successfully Added: " + new_file.get_full_path(self))
        print(f"ID[{new_file.id}] Successfully Added: " + new_file.get_relative_path(self, self.files[folderId].id))

    def get_file_id(self, fileName: str, folderId: int) -> int:
        for file in self.files.values():
            # 1) Check if name & folder matches. 2) Check folder ID is valid.
            if file.name == fileName and file.folder_id == folderId and self.valid_folder(folderId):
                return file.id
            if fileName == "MyDocuments" and folderId == None:
                return 0  # Root
        print(fileName + "not found. Return 0 Instead.")
        return 0  # Return root Instead

    def move_file(self, fileId: int, newFolderId: int) -> None:
        # 1) Check if the newFolderId is valid.
        if not self.valid_folder(newFolderId):
            return
        # 2) Check if the fileId is valid.
        if fileId not in self.files:
            print("Invalid file ID.")
            return

        curr_file = self.files[fileId].get_name()
        new_folder = self.files[newFolderId].get_name()

        self.files[fileId].folder_id = newFolderId  # Moving...
        print(f"Moving Completed: ~/{new_folder}/{curr_file}")
        return

    def get_files(self, folderId: int) -> typing.List[str]:
        if not self.valid_folder(folderId):
            return []
        # Return all the names of all files in that folder.
        file_list = [file.get_name() for file in self.files.values() if file.folder_id == folderId]

        # I use this to emphasize this is an empty folder, it not necessary.
        if len(file_list) == 0:
            file_list = ["[EMPTY FOLDER]"]
        return file_list

    def print_files(self, folder_id=0, level=0) -> None:
        indent = "    "  # 4 spaces
        prefix = "|-- "  # Prefix for each file/folder
        # Print the root folder
        if level == 0:
            root_folder = self.files[folder_id]
            print(f"[{root_folder.id}] {root_folder.name} ({root_folder.type})")

        # Current folder in the level
        files_list = [file for file in self.files.values() if file.folder_id == folder_id]

        # Sort the files by id
        files_list.sort(key=lambda file: file.id)
        # Print each file in the folder

        for file in files_list:
            print(indent * level + prefix + f"[{file.id}] {file.name}{file.extension}")
            # Recursive call --> moving to the next level
            if file.type == 'folder':
                self.print_files(file.id, level + 1)

    def delete_file(self, fileId: int) -> None:
        if fileId not in self.files:
            print(f"File id {fileId} does not exits.")
            return

        file_to_delete = self.files[fileId]
        deleteType = file_to_delete.type

        if deleteType == 'folder':
            delete_list = [file.id for file in self.files.values() if file.folder_id == fileId]
            for id in delete_list:
                self.delete_file(id)

        del self.files[fileId]
        print(f"File id {fileId} has been successfully deleted!")
        if deleteType in self.file_counts:
            self.file_counts[deleteType] -= 1

        # Update the file count

    #  ------Other Helper Functions-----

    # Check if 1) folderId exists. 2) folderId is a "folder" type.
    def valid_folder(self, folderId: int) -> bool:
        if folderId is None:  # allow None for root folder
            return True

        if folderId not in self.files:
            print(f"Folder ID: {folderId} does not exist.")
            return False

        if self.files[folderId].type != "folder":
            print(f"Folder ID: {folderId} is not a folder type.")
            return False
        # ... Add more conditions in the future to check if it's valid
        return True

    # Check if fileType is valid
    def valid_fileType(self, fileType: str) -> bool:
        if fileType not in FILE_TYPES:
            print("Invalid file type.")
            return False
        return True


# /////////////////////////////////////////////////////////
# // YOU DO NOT NEED TO MAKE CHANGES BELOW UNLESS NECESSARY
# /////////////////////////////////////////////////////////

# PLEASE ENSURE run_example() RUNS BEFORE SUBMITTING.
def run_example():
    fs = FileSystem()

    rootId = fs.get_file_id("MyDocuments", None)
    fs.add_new_file("draft", "folder", rootId)
    fs.add_new_file("complete", "folder", rootId)
    draftId = fs.get_file_id("draft", rootId)
    completeId = fs.get_file_id("complete", rootId)
    fs.add_new_file("foo", "worksheet", draftId)
    fs.add_new_file("bar", "dashboard", completeId)
    fooId = fs.get_file_id("foo", draftId)
    fs.move_file(fooId, completeId)

    print(", ".join(fs.get_files(rootId)))
    print(", ".join(fs.get_files(draftId)))
    print(", ".join(fs.get_files(completeId)))

    fs.add_new_file("project", "folder", draftId)
    projectId = fs.get_file_id("project", draftId)
    for filename in ["page1", "page2", "page3"]:
        fs.add_new_file(filename, "worksheet", projectId)
    fs.add_new_file("cover", "dashboard", projectId)
    fs.move_file(projectId, completeId)
    projectId = fs.get_file_id("project", completeId)
    coverId = fs.get_file_id("cover", projectId)
    fs.move_file(coverId, rootId)

    print(", ".join(fs.get_files(rootId)))
    print(", ".join(fs.get_files(draftId)))
    print(", ".join(fs.get_files(completeId)))
    print(", ".join(fs.get_files(projectId)))

    print(fs.get_total_dashboards())
    print(fs.get_total_worksheets())
    fs.print_files()

    fs.delete_file(projectId)
    fs.print_files()
    print()


def ask_for_int(question: str) -> int:
    val = input(question)
    try:
        return int(val)
    except:
        print('Please enter a valid integer value\n')
        return ask_for_int(question)


def ask_question():
    fs = FileSystem()
    running = True
    while (running):
        command = ask_for_int(
            "\nEnter an integer to indicate a command: \n[1] get_total_dashboards\n[2] get_total_worksheets\n[3] add_new_file\n[4] get_file_id\n[5] move_file\n[6] get_files \n[7] print_files\n[8] exit\n")
        if command == 1:
            totalDashboards = fs.get_total_dashboards()
            print("There are {0} dashboards in the file system.".format(totalDashboards));
        elif command == 2:
            totalWorksheets = fs.get_total_worksheets()
            print("There are {0} worksheets in the file system.".format(totalWorksheets));
        elif command == 3:
            fileName = input("Enter a new file name: ")
            fileType = input("Enter a file type (worksheet, dashboard, or folder): ")
            folderId = ask_for_int("Enter a folder id where you'd like to put this file: ")
            fs.add_new_file(fileName, fileType, folderId);
            print("{0} has been added to folder {1}".format(fileName, folderId))
        elif command == 4:
            fileName = input("Enter the file name: ")
            folderId = ask_for_int("Enter the folder id: ")
            fileId = fs.get_file_id(fileName, folderId)
            print("{0} is file {1}".format(fileName, fileId));
        elif command == 5:
            fileId = ask_for_int("Enter a file id:")
            newFileId = ask_for_int("Enter the folder id where you'd like to move this file: ")
            fs.move_file(fileId, newFileId);
            print("Successfully moved file {0} to folder {1}".format(fileId, newFileId))
        elif command == 6:
            folderId = ask_for_int("Enter a folderId:")
            fileNames = fs.get_files(folderId)
            if (len(fileNames) == 0):
                print("There are no files in folder {0}".format(folderId))
            else:
                print("The following files are in folder {0}: ".format(folderId))
                for fileName in fileNames:
                    print("\t{0}".format(fileName))
        elif command == 7:
            fs.print_files()
        elif command == 8:
            print("Exiting program.")
            running = False
        else:
            print("Invalid command: {0}. Please try again.\n".format(command))


def main():
    print('run_example output:')
    run_example()
    print('ask_question output:')
    ask_question()

main()
