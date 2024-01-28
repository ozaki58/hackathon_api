
import pymysql.cursors

#データベース設定
def get_db_connection():
    return pymysql.connect(host='tutorial.clmkyaosgimn.ap-northeast-1.rds.amazonaws.com',
                    user='admin',
                    db='hackathon_project',
                    charset='utf8mb4',
                    password='OZaKi1030',
                    cursorclass=pymysql.cursors.DictCursor)