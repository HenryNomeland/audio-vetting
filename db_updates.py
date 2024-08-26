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


def update_comments(comment, fileID):
    conn, cursor = make_conn()
    cursor.execute(
        """
                   UPDATE Files
                   SET Comments = ?
                   WHERE fileID = ?
                   """,
        (comment, fileID),
    )
    commit_conn(conn, cursor)
