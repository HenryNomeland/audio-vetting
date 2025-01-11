import sqlite3
import os
import pandas as pd
from db_updates import *
import sys


# Initializing the database with 3 tables of things that we need to keep track of
def init_db(data_folder="Data", overwrite_db=False):
    conn, cursor = make_conn()
    base_dir = get_directorypath("X:\\CHILD TD RSCH\\PRP")
    data_folder = os.path.join(base_dir, data_folder)

    # Creating the Files table which includes every file, their assignments, and their status
    tablename = "Files"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(
        f"""
         CREATE TABLE IF NOT EXISTS {tablename} (
         FileID INTEGER PRIMARY KEY,
         WorkerID INTEGER,
         FolderID INTEGER,
         FileName VARCHAR(50) NOT NULL,
         FilePath VARCHAR(260) NOT NULL,
         FileType VARCHAR(10) NOT NULL,
         FileStatus VARCHAR(20) DEFAULT "Incomplete" NOT NULL,
         Comments VARCHAR(100),
         FOREIGN KEY (WorkerID) REFERENCES Workers (WorkerID) ON DELETE SET NULL,
         FOREIGN KEY (FolderID) REFERENCES Folders (FolderID) ON DELETE CASCADE
         )
         """
    )

    # Creating the Worker table which includes every worker that is assigned to files
    tablename = "Workers"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(
        f"""
         CREATE TABLE IF NOT EXISTS {tablename} (
         WorkerID INTEGER PRIMARY KEY,
         WorkerName VARCHAR(50) UNIQUE,
         WorkerType VARCHAR(50)
         )
         """
    )

    # Creating the Folders table which includes every folder representing a child in the dataset
    tablename = "Folders"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(
        f"""
         CREATE TABLE IF NOT EXISTS {tablename} (
         FolderID INTEGER PRIMARY KEY,
         FolderName VARCHAR(50),
         TotalFiles INT NOT NULL,
         FolderPath VARCHAR(260),
         FolderGroup VARCHAR(10)
         )
         """
    )

    for folderpath in cycle_folders(data_folder):
        foldername = folderpath.split(os.sep)
        foldername = foldername[-2] + f"-v{foldername[-1][-2:]}"
        totalfiles = 0
        for path, _, files in os.walk(folderpath):
            totalfiles += len(files)
        # If the folder isn't in the database this inserts the folder into the database
        cursor.execute(
            """
            SELECT exists(SELECT 1 FROM Folders WHERE FolderName = ?) AS row_exists;
            """,
            (foldername,),
        )
        if cursor.fetchone()[0] == 0:
            start = foldername[:2]
            if start.isnumeric():
                foldergroup = f"TD-{start}yo"
            else:
                foldergroup = f"CP-{start[0]}"
            cursor.execute(
                """
                INSERT INTO Folders (TotalFiles, FolderName, FolderPath, FolderGroup) VALUES (?, ?, ?, ?)
                """,
                (totalfiles, foldername, folderpath, foldergroup),
            )
        for path, _, files in os.walk(folderpath):
            for filename in files:
                filepath = os.path.join(path, filename)
                # If the file isn't in the database this inserts the file into the database
                if filepath[-3:].lower() == "wav":
                    cursor.execute(
                        """
                        SELECT FolderID FROM Folders WHERE FolderName = ?
                        """,
                        (foldername,),
                    )
                    folderID = cursor.fetchone()[0]
                    filetype = filepath.split(os.sep)[-2].split(" ")[0]
                    cursor.execute(
                        """
                        SELECT exists(SELECT 1 FROM Files WHERE FileName = ? AND FileType = ? AND FolderID = ?) AS row_exists
                        """,
                        (filename, filetype, folderID),
                    )
                    if cursor.fetchone()[0] == 0:
                        print("New file being added to the database: ", filename)
                        cursor.execute(
                            """
                            INSERT INTO Files (FolderID, FileName, FilePath, FileType) VALUES (?, ?, ?, ?)
                            """,
                            (folderID, filename, filepath, filetype),
                        )
                    # Uncomment to deal with that one weird disaster situation:
                    # else:
                    #     cursor.execute(
                    #         """
                    #         SELECT exists(SELECT 1 FROM Files WHERE FilePath != ? AND FileName = ? AND FileType = ? AND FolderID = ?) AS row_exists
                    #         """,
                    #         (filepath, filename, filetype, folderID),
                    #     )
                    #     if cursor.fetchone()[0] == 1:
                    #         cursor.execute(
                    #             """
                    #             SELECT FilePath FROM Files WHERE FilePath != ? AND FileName = ? AND FileType = ? AND FolderID = ?
                    #             """,
                    #             (filepath, filename, filetype, folderID),
                    #         )
                    #         print("Deleting the following: ", cursor.fetchone()[0])
                    #         cursor.execute(
                    #             """
                    #             DELETE FROM Files WHERE FilePath != ? AND FileName = ? AND FileType = ? AND FolderID = ?
                    #             """,
                    #             (filepath, filename, filetype, folderID),
                    #         )
    commit_conn(conn, cursor)


if __name__ == "__main__":
    init_db("Data", False)
