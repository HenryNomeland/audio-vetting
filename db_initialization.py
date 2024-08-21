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

    if overwrite_db:
        table_create = "CREATE TABLE IF NOT EXISTS"
    else:
        table_create = "CREATE TABLE"

    # Creating the Files table which includes every file, their assignments, and their status
    cursor.execute(f"""
                   {table_create} Files (
                   FileID INTEGER PRIMARY KEY,
                   StudentID INT,
                   FolderID INT,
                   FileName VARCHAR(50) NOT NULL,
                   FilePath VARCHAR(260) NOT NULL,
                   FileType VARCHAR(10) NOT NULL,
                   FileStatus VARCHAR(20) DEFAULT "Incomplete" NOT NULL,
                   FOREIGN KEY (StudentID) REFERENCES Students (StudentID)
                   FOREIGN KEY (FolderID) REFERENCES Folders (FolderID)
                   )
                   """)
    
    # Creating the Student table which includes every student that is assigned to files
    cursor.execute(f"""
                   {table_create} Students (
                   StudentID INTEGER PRIMARY KEY,
                   StudentName VARCHAR(50),
                   StudentType VARCHAR(50)
                   )
                   """)
    
    # Creating the Folders table which includes every folder representing a child in the dataset
    cursor.execute(f"""
                   {table_create} Folders (
                   FolderID INTEGER PRIMARY KEY,
                   TotalFiles INT NOT NULL,
                   FolderName VARCHAR(50),
                   FolderPath VARCHAR(260)
                   )
                   """)
    
    for folderpath in cycle_folders(data_folder):
        foldername = os.path.basename(folderpath)
        cursor.execute(f"""
            SELECT exists(SELECT 1 FROM Folders WHERE FolderName = '{foldername}') AS row_exists;
            """
        )
        totalfiles = 0
        for _, _, files in os.walk(folderpath):
            totalfiles += len(files)
        if cursor.fetchall()[0][0] == 0:
            cursor.execute(f"""
            INSERT INTO Folders (TotalFiles, FolderName, FolderPath) VALUES ('{totalfiles}', '{foldername}', '{folderpath}')
            """
            )
    
    rows = cursor.execute("SELECT FolderID, FolderName FROM Folders").fetchall()
    print(rows)

    conn.commit()
    cursor.close()
    if conn:
        conn.close()

if __name__ == "__main__":
    init_db('Data', True)

