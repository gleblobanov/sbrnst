import db
import config
import random
import os
import codecs
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
import config

def find_word():
    try:
        connection, cursor = db.connect()
        sql = "SELECT to_tsvector('Я изучаю соборность. Концепт соборности. Сборности.');"
        cursor.execute(sql)
        record = cursor.fetchone()
        print(record)
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()


def get_file(file_id, file_path):
    try:
        connection, cursor = db.connect()
        sql = """\
            SELECT string_agg(content, E'\n')
            FROM text
            WHERE file_id IN (SELECT file_id FROM file WHERE source_file_id = %s ORDER BY page_order);
            """
        cursor.execute(sql, [file_id])
        record = cursor.fetchone()

        hash = random.getrandbits(128)
        #temp_filename = str(hash) + '.txt'
        temp_filename = file_path + '.txt'
        temp_filepath = os.path.join(config.dirs()["temp_dir"], temp_filename)
        
        with codecs.open(temp_filepath, 'w', encoding='utf8') as f:
            f.write(record[0])
        
        return temp_filepath
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

def get_files(author_id, year):
    try:
        connection, cursor = db.connect()
        sql = """\
            SELECT file.file_id, file_path, author_id, year
	        FROM file            

	        LEFT JOIN file_author as fa
		    ON file.file_id = fa.file_id

	        WHERE format in ('PDF', 'DOCX')
		        AND author_id = %s
                AND year = %s
	
	        ORDER BY year
			
			;"""

        cursor.execute(sql, [author_id, year])
        records = cursor.fetchall()

        filespaths = []
        
        for record in records: 
            filepath = get_file(record[0], record[1])
            filespaths.append(filepath)

        return filespaths
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

def get_files_all():
    try:
        connection, cursor = db.connect()
        sql = """\
            SELECT file.file_id, file_path, author_id, year
	        FROM file            

	        LEFT JOIN file_author as fa
		    ON file.file_id = fa.file_id

	        WHERE format in ('PDF', 'DOCX')
	
			;"""

        cursor.execute(sql)
        records = cursor.fetchall()

        filespaths = []
        
        for record in records: 
            filepath = get_file(record[0], record[1])
            filespaths.append(filepath)

        return filespaths
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

def get_files_author(author_id):
    try:
        connection, cursor = db.connect()
        sql = """\
            SELECT file.file_id, file_path, author_id, year
	        FROM file            

	        LEFT JOIN file_author as fa
		    ON file.file_id = fa.file_id

	        WHERE format in ('PDF', 'DOCX')
		        AND author_id = %s
	
	        ORDER BY year
			
			;"""

        cursor.execute(sql, [author_id])
        records = cursor.fetchall()

        filespaths = []
        
        for record in records: 
            filepath = get_file(record[0], record[1])
            filespaths.append(filepath)

        return filespaths
    except Exception as error:
        print(error)
    finally:
        cursor.close()
        connection.close()

def create_corpus(author_id, year):
    filelist = [f for f in os.listdir(config.dirs()["temp_dir"])]
    for f in filelist:
        os.remove(os.path.join(config.dirs()["temp_dir"], f))
    get_files(author_id, year)    
    newcorpus = PlaintextCorpusReader(config.dirs()["temp_dir"], '.*')
    return newcorpus

def create_corpus_all():
    filelist = [f for f in os.listdir(config.dirs()["temp_dir"])]
    for f in filelist:
        os.remove(os.path.join(config.dirs()["temp_dir"], f))
    get_files_all()    
    newcorpus = PlaintextCorpusReader(config.dirs()["temp_dir"], '.*')
    return newcorpus

def create_corpus_author(author_id):
    filelist = [f for f in os.listdir(config.dirs()["temp_dir"])]
    for f in filelist:
        os.remove(os.path.join(config.dirs()["temp_dir"], f))
    get_files_author(author_id)    
    newcorpus = PlaintextCorpusReader(config.dirs()["temp_dir"], '.*')
    return newcorpus