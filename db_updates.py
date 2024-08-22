from db_initialization import make_conn, commit_conn

def add_worker(name, type):
    conn, cursor = make_conn()
    cursor.execute("""
                   INSERT INTO Workers (WorkerName, WorkerType) VALUES (?, ?)
                   """, (name, type))
    commit_conn(conn, cursor)

def assign_files(fileID_list, workerID):
    conn, cursor = make_conn()
    for fileID in fileID_list:
        cursor.execute("""
                       UPDATE Files
                       SET WorkerID = ? 
                       WHERE FileID = ?
                       """, (workerID, fileID))
    commit_conn(conn, cursor)

def assign_folders(folderID_list, workerID):
    conn, cursor = make_conn()
    for folderID in folderID_list:
        cursor.execute("""
                       UPDATE Files
                       SET WorkerID = ?
                       WHERE FolderID = ?
                       """, (workerID, folderID))
    commit_conn(conn, cursor)

def file_complete(fileID):
    conn, cursor = make_conn()
    cursor.execute("""
                   UPDATE Files
                   SET FileStatus = 'Complete'
                   WHERE fileID = ?
                   """, (fileID))
    commit_conn(conn, cursor)

def file_flag(fileID):
    conn, cursor = make_conn()
    cursor.execute("""
                   UPDATE Files
                   SET FileStatus = 'Flagged'
                   WHERE fileID = ?
                   """, (fileID))
    commit_conn(conn, cursor)

def clear_assignments(workerID):
    conn, cursor = make_conn()
    cursor.execute("""
                   UPDATES Files
                   SET WorkerID = NULL
                   WHERE WorkerID = ?
                   """, (workerID, ))
    commit_conn(conn, cursor)