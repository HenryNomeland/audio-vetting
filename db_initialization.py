import sqlite3

# Initializing the database with 3 tables of things that we need to keep track of
def init_db():
    conn = sqlite3.connect("prp.db")
    cursor = conn.cursor()

    # Creating the Files table which includes every file, their assignments, and their status
    cursor.execute("""
                   CREATE TABLE Files (
                   FileID INT NOT NULL PRIMARY KEY,
                   StudentID INT FOREIGN KEY,
                   FolderID INT FOREIGN KEY,
                   FileName VARCHAR(50) NOT NULL,
                   FilePath VARCHAR(260) NOT NULL,
                   FileType VARCHAR(10) NOT NULL,
                   FileStatus VARCHAR(20) DEFAULT "Incomplete" NOT NULL
                   )
                   """)
    
    # Creating the Student table which includes every student that is assigned to files
    cursor.execute("""
                   CREATE TABLE Students (
                   StudentID INT NOT NULL PRIMARY KEY,
                   StudentName VARCHAR(50),
                   StudentType VARCHAR(50)
                   )
                   """)
    
    # Creating the Folders table which includes every folder representing a child in the dataset
    cursor.execute("""
                   CREATE TABLE Folders (
                   FolderID INT NOT NULL PRIMARY KEY
                   TotalFiles INT NOT NULL,
                   FolderName VARCHAR(50),
                   FolderPath VARCHAR(260)
                   )
                   """)
    

    

if __name__ == "__main__":
    init_db()

