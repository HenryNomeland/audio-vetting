import sqlite3
import os
from sys import platform


def make_conn():
    conn = sqlite3.connect(
        os.path.join(get_directorypath("X:\\CHILD TD RSCH\\PRP"), "audio.db")
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn, conn.cursor()


def commit_conn(conn, cursor):
    conn.commit()
    cursor.close()
    if conn:
        conn.close()


def get_directorypath(directory):
    if platform == "linux" or platform == "linux2":
        return os.path.join(
            "..", "..", "..", "LINUXTESTING", os.path.join(*directory.split("\\")[1:])
        )
    if platform == "darwin":
        directory = os.path.join(*directory.split("\\")[1:])
    if os.path.exists("C:" + directory[2:]):
        return "C:" + directory[2:]
    elif os.path.exists("X:" + directory[2:]):
        return "X:" + directory[2:]
    elif os.path.exists("Y:" + directory[2:]):
        return "Y:" + directory[2:]
    elif os.path.exists("W:" + directory[2:]):
        return "W:" + directory[2:]
    elif os.path.exists("Z:" + directory[2:]):
        return "Z:" + directory[2:]
    elif os.path.exists("\\\\wcs-cifs\\wc\\speech_data" + directory[2:]):
        return "\\\\wcs-cifs\\wc\\speech_data" + directory[2:]
    elif os.path.exists("M:\\wc\\speech_data" + directory[2:]):
        return "M:\\wc\\speech_data" + directory[2:]


def get_filepath(filename):
    conn, cursor = make_conn()
    filepath = cursor.execute(
        """
        SELECT FilePath from Files
        WHERE FileName = ?
        """,
        (filename,),
    ).fetchone()[0]
    if platform == "linux" or platform == "linux2":
        return filepath
    if os.path.exists("C:" + filepath[2:]):
        return "C:" + filepath[2:]
    elif os.path.exists("X:" + filepath[2:]):
        return "X:" + filepath[2:]
    elif os.path.exists("Y:" + filepath[2:]):
        return "Y:" + filepath[2:]
    elif os.path.exists("W:" + filepath[2:]):
        return "W:" + filepath[2:]
    elif os.path.exists("Z:" + filepath[2:]):
        return "Z:" + filepath[2:]
    elif os.path.exists(os.path.join("wcs-cifs", "wc", "speech_data", filepath[2:])):
        return os.path.join("wcs-cifs", "wc", "speech_data", filepath[2:])
    elif os.path.exists(os.path.join("M:", "wc", "speech_data", filepath[2:])):
        return os.path.join("M:", "wc", "speech_data", filepath[2:])


def cycle_folders(data_directory):
    folderpaths = []
    for path, _, _ in os.walk(data_directory):
        pathlist = path.split(os.sep)
        if len(pathlist) > 2:
            if pathlist[-4] == os.path.basename(data_directory):
                folderpaths.append(path)
    return folderpaths


def add_worker(name, type):
    conn, cursor = make_conn()
    cursor.execute(
        """
        INSERT INTO Workers (WorkerName, WorkerType) VALUES (?, ?)
        """,
        (name, type),
    )
    commit_conn(conn, cursor)


def assign_files(fileID_list, workerID):
    conn, cursor = make_conn()
    for fileID in fileID_list:
        cursor.execute(
            """
            UPDATE Files
            SET WorkerID = ? 
            WHERE FileID = ?
            """,
            (workerID, fileID),
        )
    commit_conn(conn, cursor)


def assign_folders(folderID_list, workerID):
    conn, cursor = make_conn()
    for folderID in folderID_list:
        cursor.execute(
            """
            UPDATE Files
            SET WorkerID = ?
            WHERE FolderID = ?
            """,
            (workerID, folderID),
        )
    commit_conn(conn, cursor)


def file_complete(fileID):
    conn, cursor = make_conn()
    cursor.execute(
        """
        UPDATE Files
        SET FileStatus = 'Complete'
        WHERE fileID = ?
        """,
        (fileID),
    )
    commit_conn(conn, cursor)


def file_flag(fileID):
    conn, cursor = make_conn()
    cursor.execute(
        """
        UPDATE Files
        SET FileStatus = 'Flagged'
        WHERE fileID = ?
        """,
        (fileID),
    )
    commit_conn(conn, cursor)


def clear_assignments(workerID):
    conn, cursor = make_conn()
    cursor.execute(
        """
        UPDATES Files
        SET WorkerID = NULL
        WHERE WorkerID = ?
        """,
        (workerID,),
    )
    commit_conn(conn, cursor)


def update_comments(filename, foldername, filetype, comments):
    conn, cursor = make_conn()
    cursor.execute(
        f"""
        SELECT FolderID FROM Folders
        WHERE FolderName = '{foldername}'
        """
    )
    folderid = cursor.fetchone()[0]
    cursor.execute(
        f"""
        UPDATE Files
        SET Comments = '{comments}'
        WHERE 
            FileName = '{filename}' AND
            FileType = '{filetype}' AND
            FolderID = '{folderid}'
        """
    )
    commit_conn(conn, cursor)


def generate_dropdown_options():
    conn, cursor = make_conn()
    cursor.execute("SELECT WorkerName FROM Workers")
    worker_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return worker_list


def generate_visitdropdown_options(worker):
    conn, cursor = make_conn()
    if worker != "All":
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Workers
            LEFT JOIN Files
            ON Workers.WorkerID = Files.WorkerID
            LEFT JOIN Folders
            ON Files.FolderID = Folders.FolderID
            WHERE Workers.WorkerName = '{worker}' 
            """
        )
    else:
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Folders
            """
        )
    visit_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return visit_list


def generate_incompletevisitdropdown_options(worker):
    conn, cursor = make_conn()
    if worker != "All":
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Workers
            LEFT JOIN Files
            ON Workers.WorkerID = Files.WorkerID
            LEFT JOIN Folders
            ON Files.FolderID = Folders.FolderID
            WHERE Workers.WorkerName = '{worker}' AND Files.FileStatus = 'Incomplete'
            """
        )
    else:
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Folders
            LEFT JOIN Files
            ON Folders.FolderID = Files.FolderID
            WHERE Files.FileStatus = 'Incomplete'
            """
        )
    visit_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return visit_list


def generate_completevisitdropdown_options(worker):
    conn, cursor = make_conn()
    if worker != "All":
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Workers
            LEFT JOIN Files
            ON Workers.WorkerID = Files.WorkerID
            LEFT JOIN Folders
            ON Files.FolderID = Folders.FolderID
            WHERE Workers.WorkerName = '{worker}' AND Files.FileStatus != 'Incomplete'
            """
        )
    else:
        cursor.execute(
            f"""
            SELECT DISTINCT FolderName FROM Folders
            LEFT JOIN Files
            ON Folders.FolderID = Files.FolderID
            WHERE Files.FileStatus != 'Incomplete'
            """
        )
    visit_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return visit_list


def generate_foldergroupdropdown_options():
    conn, cursor = make_conn()
    cursor.execute("SELECT DISTINCT FolderGroup FROM Folders")
    group_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return group_list


def delete_worker(worker_name):
    conn, cursor = make_conn()
    cursor.execute("DELETE FROM Workers WHERE WorkerName = ?", (worker_name,))
    commit_conn(conn, cursor)


def update_folder_assignments(worker_name, folderlist):
    conn, cursor = make_conn()
    cursor.execute("SELECT WorkerID FROM Workers WHERE WorkerName = ?", (worker_name,))
    worker_id = cursor.fetchall()[0][0]
    cursor.execute(
        f"""
         SELECT FolderID
         FROM Folders 
         WHERE FolderPath IN ({','.join(['?'] * len(folderlist))})
         """,
        folderlist,
    )
    folder_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""
         UPDATE Files
         SET WorkerID = '{worker_id}' 
         WHERE FolderID IN ({','.join(['?'] * len(folder_ids))})
         """,
        folder_ids,
    )
    commit_conn(conn, cursor)


def update_file_assignments(worker_name, filelist):
    conn, cursor = make_conn()
    cursor.execute("SELECT WorkerID FROM Workers WHERE WorkerName = ?", (worker_name,))
    worker_id = cursor.fetchall()[0][0]
    cursor.execute(
        f"""
         SELECT FileID 
         FROM Files 
         WHERE FileName IN ({','.join(['?'] * len(filelist))})
         """,
        filelist,
    )
    file_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""
         UPDATE Files
         SET WorkerID = '{worker_id}' 
         WHERE FileID IN ({','.join(['?'] * len(file_ids))})
         """,
        file_ids,
    )
    commit_conn(conn, cursor)


def scrub_folder_assignments(folderlist):
    conn, cursor = make_conn()
    cursor.execute(
        f"""
         SELECT FolderID
         FROM Folders 
         WHERE FolderPath IN ({','.join(['?'] * len(folderlist))})
         """,
        folderlist,
    )
    folder_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""
         UPDATE Files
         SET WorkerID = '' 
         WHERE FolderID IN ({','.join(['?'] * len(folder_ids))})
         """,
        folder_ids,
    )
    commit_conn(conn, cursor)


def scrub_file_assignments(filelist):
    conn, cursor = make_conn()
    cursor.execute(
        f"""
         SELECT FileID 
         FROM Files 
         WHERE FileName IN ({','.join(['?'] * len(filelist))})
         """,
        filelist,
    )
    file_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""
         UPDATE Files
         SET WorkerID = '' 
         WHERE FileID IN ({','.join(['?'] * len(file_ids))})
         """,
        file_ids,
    )
    commit_conn(conn, cursor)


def get_file_status(filename, foldername, filetype):
    conn, cursor = make_conn()
    cursor.execute(
        """
        SELECT FileStatus
        FROM Files
        LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
        WHERE Files.FileName = ? AND Folders.FolderName = ? AND Files.FileType = ?
        """,
        (filename, foldername, filetype),
    )
    status = cursor.fetchone()[0]
    return status


def refresh_db_status(filename, foldername, filetype, filestatus):
    conn, cursor = make_conn()
    cursor.execute(
        f"""
        SELECT FolderID FROM Folders
        WHERE FolderName = '{foldername}'
        """
    )
    folderid = cursor.fetchone()[0]
    cursor.execute(
        f"""
        UPDATE Files
        SET FileStatus = '{filestatus}'
        WHERE 
            FileName = '{filename}' AND
            FileType = '{filetype}' AND
            FolderID = '{folderid}'
        """
    )
    commit_conn(conn, cursor)


def get_default_visit():
    conn, cursor = make_conn()
    cursor.execute(
        f"""
        SELECT DISTINCT FolderName 
        FROM Folders
        """
    )
    foldername = cursor.fetchone()[0]
    return foldername


def get_default_foldergroup():
    conn, cursor = make_conn()
    cursor.execute(
        f"""
        SELECT DISTINCT FolderGroup 
        FROM Folders
        """
    )
    foldergroup = cursor.fetchone()[0]
    return foldergroup
