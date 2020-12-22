import config
import db
import os

temp_dir = 'C:\\Workshop\\sbrnst\\temp'

def insert_files():
    files = os.listdir(temp_dir)
    try:
        connection, cursor = db.connect()
        sql = """\
                INSERT INTO file (file_path, format, lang)
                VALUES (%s, %s, %s);"""
        for f in files:
            print(f)
            (_, ext) = os.path.splitext(f)            
            cursor.execute(sql, (f, ext.upper()[1:], 'RU'))
            connection.commit()

    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()