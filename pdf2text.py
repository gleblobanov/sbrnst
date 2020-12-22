from pdf2image import convert_from_path
import importlib
import config
import db

# connect to db
import psycopg2
import os
import os.path as p
from termcolor import colored


def pdf_to_images(source_file_id):
    
    try:
        connection, cursor = db.connect()

        sql = """\
            SELECT file_path
            FROM file
            WHERE file_id = %s;"""

        cursor.execute(sql, [source_file_id])
        record = cursor.fetchone()

        source_path = p.join(config.dirs()["texts_dir"], record[0])
        print('Processing file_id ' + str(source_file_id)
              + '\nfilepath ' + source_path)

        if p.isfile(source_path) == False:
            print("File doesn't exist.")
            return

        images = convert_from_path(source_path)
        print('Number of pages: ' + str(len(images)))

        filename = p.splitext(record[0])[0]
        count = 0
        for img in images:
            filename_ext = filename + ' - ' + str(count) + '.png'
            result_path = p.join(config.dirs()["images_dir"], filename_ext)
            img.save(result_path, 'PNG')
            print(colored('[SAVED] ', 'green'), result_path)

            count = count + 1

            sql = """\
                INSERT INTO file (file_path,
                                  source_file_id,
                                  page_order,
                                  format)
                    VALUES (%s,
                            %s,
                            %s,
                            %s);"""

            cursor.execute(sql, (result_path,
                                 source_file_id,
                                 count,
                                 "PNG"))
            connection.commit()

        sql = """\
            UPDATE file
                SET images_extracted = TRUE
                WHERE file_id = %s;"""

        cursor.execute(sql, [source_file_id])
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print(error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print('PostgreSQL connection is closed\a')


def get_texts(source_file_id):
    global cursor
    try:
        connection = psycopg2.connect(user='postgres',
                                      password='dZFa33YL6gHpQOdBpJiC',
                                      host='127.0.0.1',
                                      port='5432',
                                      database='sbrnst')
        cursor = connection.cursor()

        sql = """SELECT file_path,
                       file_id,
                       page_order
        FROM file
        WHERE source_file_id = %s
        ORDER BY page_order"""

        cursor.execute(sql, [source_file_id])
        records = cursor.fetchall()

        for record in records:
            file_path = record[0]
            file_id = record[1]

            source_path = os.path.join(config.dirs()["images_dir"], file_path)

            print('Processing file ' + source_path)

            os.system('tesseract ' +
                      '"' + source_path + '" ' +
                      '"' + source_path + '" ' +
                      '--dpi 300 -l rus+eng')

            f = open(source_path + '.txt')
            content = f.read()
            f.close()

            os.system('rm "' + source_path + '.txt"')

            sql = """UPDATE file
            SET text_extracted = TRUE
            WHERE file_id = %s;"""

            cursor.execute(sql, [file_id])
            cursor.execute(sql, [source_file_id])

            sql = """INSERT INTO text (file_id, content)
            VALUES (%s, %s);"""

            cursor.execute(sql, [file_id, content])

        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print(error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print('PostgreSQL connection is closed\a')


def get_all_texts():
    try:
        connection = psycopg2.connect(user='postgres',
                                      password='dZFa33YL6gHpQOdBpJiC',
                                      host='127.0.0.1',
                                      port='5432',
                                      database='sbrnst')
        cursor = connection.cursor()

        sql = """SELECT file_id
                       FROM file
                WHERE text_extracted = FALSE
                AND   format = 'PDF';"""

        cursor.execute(sql)
        records = cursor.fetchall()
        for record in records:
            get_texts(record[0])

    except (Exception, psycopg2.Error) as error:
        print(error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            print('PostgreSQL connection is closed')