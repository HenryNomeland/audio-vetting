import sqlite3
import os


def make_conn():
    conn = sqlite3.connect("audio.db")
    return conn, conn.cursor()


def commit_conn(conn, cursor):
    conn.commit()
    cursor.close()
    if conn:
        conn.close()


def cycle_folders(data_directory):
    folderpaths = []
    for path, _, _ in os.walk(data_directory):
        pathlist = path.split(os.sep)
        if len(pathlist) > 2:
            if pathlist[-3] == os.path.basename(data_directory):
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


def update_comments(filename, comments):
    conn, cursor = make_conn()
    cursor.execute(
        """
        UPDATE Files
        SET Comments = ?
        WHERE FileName = ?
        """,
        (comments, filename),
    )
    commit_conn(conn, cursor)


def generate_dropdown_options():
    conn, cursor = make_conn()
    cursor.execute("SELECT WorkerName FROM Workers")
    worker_list = [row[0] for row in cursor.fetchall()]
    commit_conn(conn, cursor)
    return worker_list


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
