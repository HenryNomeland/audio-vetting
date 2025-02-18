import sqlite3
import os
from sys import platform


def make_conn():
    conn = sqlite3.connect(
        os.path.join(get_directorypath("X:\\CHILD TD RSCH\\PRP"), "audio.db"),
        timeout=10,
    )
    conn.execute("PRAGMA journal_mode=DELETE;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA locking_mode=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    return conn


def execute_write(cursor, query, params=None):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        cursor.connection.commit()
        cursor.close()
        cursor.connection.close()
    except sqlite3.DatabaseError as e:
        print(f"Error during write operation: {e}")
        cursor.connection.rollback()


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
    elif os.path.exists("\\\\wcs-cifs\\waisman.wisc.edu\\speech_data" + directory[2:]):
        return "\\\\wcs-cifs\\waisman.wisc.edu\\speech_data" + directory[2:]
    elif os.path.exists(
        "\\\\wcs-cifs.waisman.wisc.edu\\wc\\speech_data" + directory[2:]
    ):
        return "\\\\wcs-cifs.waisman.wisc.edu\\wc\\speech_data" + directory[2:]


def get_filepath(filename):
    conn = make_conn()
    cursor = conn.cursor()
    filepath = cursor.execute(
        """
        SELECT FilePath from Files
        WHERE FileName = ?
        """,
        (filename,),
    ).fetchone()[0]
    cursor.close()
    conn.close()
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
    conn = make_conn()
    cursor = conn.cursor()
    execute_write(
        cursor,
        """
        INSERT INTO Workers (WorkerName, WorkerType) VALUES (?, ?)
        """,
        params=(name, type),
    )


def assign_files(fileID_list, workerID):
    conn = make_conn()
    cursor = conn.cursor()
    for fileID in fileID_list:
        execute_write(
            cursor,
            """
            UPDATE Files
            SET WorkerID = ? 
            WHERE FileID = ?
            """,
            params=(workerID, fileID),
        )


def assign_folders(folderID_list, workerID):
    conn = make_conn()
    cursor = conn.cursor()
    for folderID in folderID_list:
        execute_write(
            cursor,
            """
            UPDATE Files
            SET WorkerID = ?
            WHERE FolderID = ?
            """,
            params=(workerID, folderID),
        )


def file_complete(fileID):
    conn = make_conn()
    cursor = conn.cursor()
    execute_write(
        cursor,
        """
        UPDATE Files
        SET FileStatus = 'Complete'
        WHERE fileID = ?
        """,
        params=(fileID),
    )


def file_flag(fileID):
    conn = make_conn()
    cursor = conn.cursor()
    execute_write(
        cursor,
        """
        UPDATE Files
        SET FileStatus = 'Flagged'
        WHERE fileID = ?
        """,
        params=(fileID),
    )


def clear_assignments(workerID):
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        cursor,
        """
        UPDATES Files
        SET WorkerID = NULL
        WHERE WorkerID = ?
        """,
        params=(workerID,),
    )


def update_comments(filename, foldername, filetype, comments):
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT FolderID FROM Folders
        WHERE FolderName = '{foldername}'
        """,
    )
    folderid = cursor.fetchone()[0]
    execute_write(
        cursor,
        f"""
        UPDATE Files
        SET Comments = '{comments}'
        WHERE 
            FileName = '{filename}' AND
            FileType = '{filetype}' AND
            FolderID = '{folderid}'
        """,
    )


def generate_dropdown_options():
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT WorkerName FROM Workers")
    worker_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return sorted(worker_list, key=str.lower)


def generate_visitdropdown_options(worker):
    conn = make_conn()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return sorted(visit_list, key=str.lower)


def generate_incompletevisitdropdown_options(worker):
    conn = make_conn()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return sorted(visit_list, key=str.lower)


def generate_completevisitdropdown_options(worker):
    conn = make_conn()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return sorted(visit_list, key=str.lower)


def generate_foldergroupdropdown_options():
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT FolderGroup FROM Folders")
    group_list = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return sorted(group_list, key=str.lower)


def delete_worker(worker_name):
    conn = make_conn()
    cursor = conn.cursor()
    execute_write(
        cursor, "DELETE FROM Workers WHERE WorkerName = ?", params=(worker_name,)
    )


def update_folder_assignments(worker_name, folderlist):
    conn = make_conn()
    cursor = conn.cursor()
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
    execute_write(
        cursor,
        f"""
         UPDATE Files
         SET WorkerID = '{worker_id}' 
         WHERE FolderID IN ({','.join(['?'] * len(folder_ids))})
         """,
        params=folder_ids,
    )


def update_file_assignments(worker_name, filelist):
    conn = make_conn()
    cursor = conn.cursor()
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
    execute_write(
        cursor,
        f"""
         UPDATE Files
         SET WorkerID = '{worker_id}' 
         WHERE FileID IN ({','.join(['?'] * len(file_ids))})
         """,
        params=file_ids,
    )


def scrub_folder_assignments(folderlist):
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
         SELECT FolderID
         FROM Folders 
         WHERE FolderPath IN ({','.join(['?'] * len(folderlist))})
         """,
        folderlist,
    )
    folder_ids = [row[0] for row in cursor.fetchall()]
    execute_write(
        cursor,
        f"""
         UPDATE Files
         SET WorkerID = '' 
         WHERE FolderID IN ({','.join(['?'] * len(folder_ids))})
         """,
        folder_ids,
    )


def scrub_file_assignments(filelist):
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        cursor,
        f"""
         SELECT FileID 
         FROM Files 
         WHERE FileName IN ({','.join(['?'] * len(filelist))})
         """,
        params=filelist,
    )
    file_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        cursor,
        f"""
         UPDATE Files
         SET WorkerID = '' 
         WHERE FileID IN ({','.join(['?'] * len(file_ids))})
         """,
        params=file_ids,
    )
    cursor.close()
    conn.close()


def get_file_status(filename, foldername, filetype):
    conn = make_conn()
    cursor = conn.cursor()
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
    cursor.close()
    conn.close()
    return status


def refresh_db_status(filename, foldername, filetype, filestatus):
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT FolderID FROM Folders
        WHERE FolderName = '{foldername}'
        """
    )
    folderid = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    conn = make_conn()
    cursor = conn.cursor()
    execute_write(
        cursor,
        f"""
        UPDATE Files
        SET FileStatus = '{filestatus}'
        WHERE 
            FileName = '{filename}' AND
            FileType = '{filetype}' AND
            FolderID = '{folderid}'
        """,
    )


def get_default_visit():
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT DISTINCT FolderName 
        FROM Folders
        """
    )
    foldername = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return foldername


def get_default_foldergroup():
    conn = make_conn()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT DISTINCT FolderGroup 
        FROM Folders
        """
    )
    foldergroup = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return foldergroup
