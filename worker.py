# -*- coding: cp1251 -*-

import sys
import json
import time
import math
import datetime
import requests
import psycopg2


rows_count = 20000

"""
����������� ���������� �������
"""
if 1 < len(sys.argv):
    rows_count = sys.argv[1]
    print(rows_count)


"""
������� ��� ����������� � ���� ������
"""
def sql_connect():
    return psycopg2.connect(
        host="192.168.77.66", port="5432", 
        dbname="postgres", 
        user="hackaton", password="p2eEK)J34YMfsJa"
    )


"""
��������� ������ � API
kwards: ��������� url
return: ������ ����������
"""
def get_data(kwards={}):

    req = "https://ads-api.ru/main/api?user=valerazbanovqs@gmail.com&token=18d79b6cf2715733470f43c0c18d2575&category_id=2&source=1&city=������&is_actual=1"

    for key in kwards:
        val = kwards[key]

        if not val is None:
            req += "&{0}={1}".format(key, val)
        
    obj = json.loads(requests.get(req).content)

    if obj["code"] != 200:
        print(req, obj["code"])
        return []

    print(req, obj["code"], len(obj["data"]))
    return obj["data"]


"""
�������� ��� ������ �������� �������� � �������� �������
conn: ����������� � ���� ������
table_name: �������� �������
value: ������� ��������
return: ����, ��������������� ��������
"""
def get_param_id(conn, table_name, value):

    if value is None:
        raise Exception("�������� ������ ���� ����������")

    cursor = conn.cursor()
    sql  = "SELECT id from {0} WHERE �������� = '{1}'".format(table_name, value)
    cursor.execute(sql)
    rows = cursor.fetchall()

    if len(rows) <= 0:
        sql  = "INSERT INTO {0}(��������) VALUES (%s) RETURNING Id;".format(table_name);
        cursor.execute(sql, [value])
        conn.commit()

        print("Add", value, "to", table_name)
        return cursor.fetchone()[0]

    return rows[0][0]

"""
�������� ������� ����������
encoder: ������������ �������� ��������� � ������ ���
path: �������� �������
obj: ������������� ������
default: �������� �� ���������
return: ������� ����������
"""
def get_param(encoder, path, obj, default):

    for key in path.split('/'):
        if key in obj:
            obj = obj[key]
        else:
            return default;

    return encoder(obj)

"""
����������� �������� ��������
"""
class encode_segment():

    def __init__(self, year):
        self.year = year

    def __call__(self, input):

        if input != "��������":
            return input

        if self.year is None:
            return input

        year = self.year
        cur_year = datetime.datetime.now().year

        if cur_year - 4 < year:
            return "�����������"

        if 1989 <= year:
            return "����������� �����"

        if 1930 <= year and year <= 1956:
            return "��������"

        if 1956 <= year and year <= 1985:
            return "X�������"

        if year < 1989:
            return "������ ����� ����"

        return input

"""
����������� �������� ��������� ����
"""
def encode_wall_material(input):

    if input == "����������":
        return "�������"

    if input == "���������":
        return "������"       
    
    if input == "�������":
        return "����"

    if input == "���������":
        return "������"

    if input == "����������":
        return "������"

    return None

"""
����������� �������� �������
"""
def encode_area(input):
    return float(input.split(' ')[0])

"""
����������� �������� ������� �������
"""
def encode_balcony(input):
    return 1

"""
����������� �������� ���������
"""
class encode_condition():

    def __init__(self, �������):
        self.������� = �������

    def __call__(self, input):

        if self.������� == "��� �������":
            input = "�������������"
        
        if input == "��� �������":
            return "��� �������"
        else:
            input += " ������"

        return input

"""
����������� �������� ������ (������ ����������)
"""
def read_row(row):

    if row["param_1943"] != "������":
        raise Exception("����������� ���������� � ���� ����������")

    id = get_param(int, "id", row, 0)
    coordx = get_param(float, "coords/lat", row, None)
    coordy = get_param(float, "coords/lng", row, None)
    �������������� = get_param(str, "address", row, None)
    ���������������� = get_param(str, "params/���������� ������", row, None)
    year = get_param(int, "params2/� ����/��� ���������", row, 0)
    ������� = get_param(encode_segment(year), "param_1957", row, None)
    ������������� = get_param(int, "params/������ � ����", row, None)
    ������������ = get_param(encode_wall_material, "params2/� ����/��� ����", row, None)
    ���������������� = get_param(int, "params/����", row, None)
    ��������������� = get_param(encode_area, "params/�������", row, None)
    ������������ = get_param(encode_area, "params2/� ��������/������� �����", row, ��������������� * 0.15)
    �������������������� = get_param(encode_balcony, "params2/� ��������/������ ��� ������", row, 0)
    ����� = get_param(str, "metro", row, None)
    ������� = get_param(float, "km_do_metro", row, None)
    �������� = math.ceil(������� / 5 * 60)
    ������� = get_param(str, "params2/� ��������/�������", row, None)
    ��������� = get_param(encode_condition(�������), "params2/� ��������/������", row, None)
    ��������� = get_param(float, "price", row, None)

    return {
        "id" : id, 
        "coordx" : coordx, 
        "coordy" : coordy, 
        "��������������" : ��������������,
        "����������������" : ����������������,
        "�������" : �������,
        "�������������" : �������������,  
        "������������" : ������������,
        "����������������" : ����������������,  
        "���������������" : ���������������,  
        "������������" : ������������,
        "��������������������" : ��������������������, 
        "�����" : �����,  
        "�������" : �������,  
        "��������" : ��������,  
        "���������"  : ���������, 
        "���������"  : ���������, 
    }

"""
����������� �������� ������� �������
"""
def replace_id(conn, obj):
    obj["����������������"] = get_param_id(conn, "�������������������", obj["����������������"])
    obj["�������"] = get_param_id(conn, "�����������", obj["�������"])
    obj["������������"] = get_param_id(conn, "����������������", obj["������������"])
    obj["���������"] = get_param_id(conn, "������������", obj["���������"])
    return obj


if __name__ == "__main__":

    # ���������� ����������� � ���� ������
    conn = sql_connect()
    cursor = conn.cursor()

    # ��������� ��������
    step = 30
    date1 = datetime.datetime.now() - datetime.timedelta(hours=7) - datetime.timedelta(minutes=step)
    date2 = datetime.datetime.now() - datetime.timedelta(hours=7)

    count = 0

    # ������ ��� ���������� ������ ������� ������������
    sql  = "INSERT INTO ������������ VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (Id) DO NOTHING;"

    while count < rows_count:

        # �������� ���� ������
        batch = get_data({"date1" : date1, "date2" : date2})
        time.sleep(5)

        date1 -= datetime.timedelta(minutes=step)
        date2 -= datetime.timedelta(minutes=step)

        # ���������� �������
        for row in batch:

            try:
            
                # �������� ��������
                obj = read_row(row)

                # �������� ������ ��������
                obj = replace_id(conn, obj)

                # ��������� ������ � ���� ������
                val = list(obj.values())
                cursor.execute(sql, val)
                count += 1

                # ��������� ������ 100 �������
                if count % 100 == 0:
                    conn.commit()

            except Exception as exc:
                print(exc)



    cursor.close()
    conn.close()




