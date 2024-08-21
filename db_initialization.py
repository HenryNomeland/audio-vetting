import sqlite3
import os
import pandas as pd

def cycle_folders(data_directory):
    folderpaths = []
    for path, _, _ in os.walk(data_directory):
        pathlist = path.split(os.sep)
        if len(pathlist) > 2:
            if pathlist[-3] == os.path.basename(data_directory):
                folderpaths.append(path)
    return(folderpaths)

# Initializing the database with 3 tables of things that we need to keep track of
def init_db(data_folder = "Data", overwrite_db = False):
    conn = sqlite3.connect("prp.db")
    cursor = conn.cursor()
    drop_table = ""

    # Creating the Files table which includes every file, their assignments, and their status
    tablename = "Files"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(f"""
                   CREATE TABLE IF NOT EXISTS {tablename} (
                   FileID INTEGER PRIMARY KEY,
                   StudentID INT,
                   FolderName VARCHAR(50),
                   FileName VARCHAR(50) NOT NULL,
                   FilePath VARCHAR(260) NOT NULL,
                   FileType VARCHAR(10) NOT NULL,
                   FileStatus VARCHAR(20) DEFAULT "Incomplete" NOT NULL,
                   FOREIGN KEY (StudentID) REFERENCES Students (StudentID)
                   FOREIGN KEY (FolderName) REFERENCES Folders (FolderName)
                   )
                   """)
    
    # Creating the Student table which includes every student that is assigned to files
    tablename = "Students"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(f"""
                   CREATE TABLE IF NOT EXISTS {tablename} (
                   StudentID INTEGER PRIMARY KEY,
                   StudentName VARCHAR(50),
                   StudentType VARCHAR(50)
                   )
                   """)
    
    # Creating the Folders table which includes every folder representing a child in the dataset
    tablename = "Folders"
    if overwrite_db:
        cursor.execute(f"DROP TABLE IF EXISTS {tablename}")
    cursor.execute(f"""
                   CREATE TABLE IF NOT EXISTS {tablename} (
                   FolderName VARCHAR(50) PRIMARY KEY,
                   TotalFiles INT NOT NULL,
                   FolderPath VARCHAR(260)
                   )
                   """)
    
    for folderpath in cycle_folders(data_folder):
        foldername = os.path.basename(folderpath)
        totalfiles = 0
        for path, _, files in os.walk(folderpath):
            totalfiles += len(files)
            for filename in files:
                filepath = os.path.join(path, filename)
                # If the file isn't in the database this inserts the folder into the database
                cursor.execute(f"""
                    SELECT exists(SELECT 1 FROM Files WHERE FileName = '{filename}') AS row_exists;
                    """
                )
                if cursor.fetchall()[0][0] == 0:
                    cursor.execute(f"""
                    INSERT INTO Files (FolderName, FileName, FilePath, FileType) VALUES ('{foldername}', '{filename}', '{filepath}', '{os.path.basename(filepath).split(" ")[0]}')
                    """
                    )
        # If the folder isn't in the database this inserts the folder into the database
        cursor.execute(f"""
            SELECT exists(SELECT 1 FROM Folders WHERE FolderName = '{foldername}') AS row_exists;
            """
        )
        if cursor.fetchall()[0][0] == 0:
            cursor.execute(f"""
            INSERT INTO Folders (TotalFiles, FolderName, FolderPath) VALUES ('{totalfiles}', '{foldername}', '{folderpath}')
            """
            )

    conn.commit()
    cursor.close()
    if conn:
        conn.close()

if __name__ == "__main__":
    init_db('Data', True)

