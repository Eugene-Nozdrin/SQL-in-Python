import psycopg2
host = '127.0.0.1'
user = 'postgres'
password = '220488'
db_name = 'home_work3'

# проверка клиента по client_id
def info_client_id(cursor, client_id):
    cursor.execute('''
        SELECT * FROM client
        WHERE client_id = %s
    ''', (client_id,))
    return cursor.fetchall()

# проверка клиента по номеру телефона
def info_phone(cursor, phone_number):
    cursor.execute('''
        SELECT * FROM phone
        WHERE phone_number = %s
    ''', (phone_number,))
    return cursor.fetchall()

def info_client_and_phone(cursore, client_id, phone_number):
    if info_client_id(cursore, client_id):
        cursore.execute('''
        SELECT * FROM phone
        WHERE phone_number = %s AND client_id = %s
    ''', (phone_number, client_id))
    return cursore.fetchall()

# проверка клиента по email
def info_email(cursor, email):
    cursor.execute('''
        SELECT * FROM client
        WHERE email = %s
    ''', (email,))
    return cursor.fetchall()


# удаление таблиц
def drop_table(cursor):
    cursor.execute('''
        DROP TABLE IF EXISTS phone;
        DROP TABLE IF EXISTS client;
    ''')
    return print('Таблицы удалены.')

# создание таблиц
def create_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(20) NOT NULL,    
        surname VARCHAR(30) NOT NULL,
        email VARCHAR(50) UNIQUE NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone (
        phone_id SERIAL PRIMARY KEY,
        phone_number INTEGER UNIQUE,
        client_id INTEGER REFERENCES client(client_id)
        );
    ''')
    return print('Таблицы client и phone созданы.')


#добавление нового клиента
def add_client(cursor, first_name, surname, email, phone_number=None):
    if not info_email(cursor, email):
        if not info_phone(cursor, phone_number):
            cursor.execute('''
                INSERT INTO client(first_name, surname, email)
                VALUES (%s, %s, %s) 
                RETURNING client_id, first_name, surname, email;
                ''', (first_name, surname, email))
            res = cursor.fetchall()[0]
            if phone_number is not None:
                cursor.execute('''
                    INSERT INTO phone(phone_number, client_id)
                    VALUES (%s, %s)
                    RETURNING phone_number;
                    ''', (phone_number, res[0]))
                res += cursor.fetchone()
        else:
            return print(f'Клиент с номером {phone_number} уже существует')
        return print(f'Добавлен новый клиент {res}')
    else:
        return print(f'Клиент с email {email} уже существует')


#добавить телефон для существующего клиента
def add_phone(cursor, client_id, phone_number):
    if info_client_id(cursor, client_id):
        if not info_phone(cursor, phone_number):
            cursor.execute('''
                INSERT INTO phone(phone_number, client_id)
                VALUES (%s, %s)
                ''', (phone_number, client_id))
            return print(f'Клиенту с ID {client_id} добавлен номер телефона {phone_number}')
        else:
            return print(f'Клиент с номером {phone_number} уже существует')
    else:
        return print(f'Клиента с ID {client_id} не существует')

#изменение данных клиента(поиск клиента по ID, данные которые не будут указаны(None), останутся без изменения)
#номер телефона будет добавлен к уже существующим
def update_client(cursor, client_id = None, first_name = None, surname = None, email = None, phone_number=None):
    if client_id is not None:
        if info_client_id(cursor, client_id):
            if first_name is not None:
                cursor.execute('''
                    UPDATE client
                    SET first_name = %s 
                    WHERE client_id = %s
                    RETURNING client_id, first_name, surname, email;
                    ''', (first_name, client_id))
            if surname is not None:
                cursor.execute('''
                    UPDATE client
                    SET surname = %s
                    WHERE client_id = %s
                    RETURNING client_id, first_name, surname, email;
                    ''', (surname, client_id))
            if email is not None:
                cursor.execute('''
                    UPDATE client
                    SET email = %s
                    WHERE client_id = %s
                    RETURNING client_id, first_name, surname, email;
                    ''', (email, client_id))
            res = cursor.fetchall()[0]
            if phone_number is not None:
                if not info_phone(cursor, phone_number):
                    cursor.execute('''
                        INSERT INTO phone(phone_number, client_id)
                        VALUES (%s, %s)
                        RETURNING phone_number
                        ''', (phone_number, client_id))
                    res += cursor.fetchall()[0]
            return print(f'Указанные данные обновлены {res}')
        else:
            return print(f'Клиента с ID {client_id} не существует.')
    return print('нет ID для поиска')


# удаление телефона клиента
# (удаляет указанный телефон, если указан только id клиента, удалит все тефоны клиента)
def delete_phone(cursor, client_id, phone_number = None):
    if info_client_id(cursor, client_id):
        if phone_number is not None:
            if info_phone(cursor, phone_number):
                if info_client_id(cursor, client_id)[0][0] == info_phone(cursor, phone_number)[0][2]:
                    cursor.execute('''
                        DELETE FROM phone 
                        WHERE phone_number = %s AND client_id = %s
                        ''', (phone_number, client_id))
                    return print(f'У клиета с ID {client_id} удален номер {phone_number}.')
                else:
                    return print(f'У клиента с ID {client_id} нет номера {phone_number}.')
            else:
                return print(f'У клиента с ID {client_id} нет номера {phone_number}.')
        else:
            cursor.execute('''
                DELETE FROM phone 
                WHERE client_id = %s;
                ''', (client_id,))
            return print(f'У клиента с ID {client_id} удалены все номера.')
    else:
        return print(f'Клиента с ID {client_id} нет')

#удаление существующего клиента
def del_client(cursor, client_id):
    if info_client_id(cursor, client_id):
        cursor.execute('''
            DELETE FROM phone 
            WHERE client_id = %s;
            ''', (client_id,))
        cursor.execute('''
            DELETE FROM client
            WHERE client_id = %s;
            ''', (client_id,))
        return print(f'Клиент с ID {client_id} удален.')
    else:
        return print(f'Клиента с ID {client_id} нет.')


#найти клиента по его данным (имени, фамилии, email, телефону)
def find_client(cursor, first_name=None, surname=None, email=None, phone_number=None):
    if first_name is not None or surname is not None or email is not None:
        cursor.execute('''
            SELECT client_id, first_name
            FROM client
            WHERE first_name = %s OR surname = %s OR email = %s;
            ''', (first_name, surname, email))
        res = cur.fetchall()
        if not res:
            return print('Клиент с такими данными не найден.')
        else:
            return print(res)
    else:
        cursor.execute('''
                    SELECT client.client_id, first_name
                    FROM client 
                    JOIN phone 
                    ON client.client_id = phone.client_id
                    WHERE phone_number = %s
                    ''', (phone_number,))
        res = cur.fetchall()
        if not res:
            return print('Клиент с такими номером не найден.')
        else:
            return print(res)



with psycopg2.connect(database=db_name, user=user, password=password) as conn:
    with conn.cursor() as cur:
        drop_table(cur)
        create_table(cur)
        a = info_client_id(cur, 1)
        print(a)
        #проверка функции add_client
        add_client(cur, 'Иван', 'Петров', 'petrov@mail.ru', '1111')
        add_client(cur, 'Петр', 'Иванов', 'ivanov@mail.ru')
        add_client(cur, 'Антон', 'Сергев', 'sergeev@mail.ru',)
        add_client(cur, 'Сергей', 'Антонов', 'antonov@mail.ru', '2222')
        add_client(cur, 'Михаил', 'Платонов', 'sergeev@mail.ru')
        add_client(cur, 'Андрей', 'Сапогов', 'sapogov@mail.ru', '1111')
        add_client(cur, 'Алексей', 'Свистунов', 'svistynov@mail.ru', '3333')

        #проверка функции add_phone
        add_phone(cur, 1, '4444')
        add_phone(cur, 2, '5555')
        add_phone(cur, 3, '1111')
        add_phone(cur, 3, '1122')

        add_phone(cur, 4, '6666')
        add_phone(cur, 5, '3333')
        add_phone(cur, 5, '9999')
        add_phone(cur, 6, '8888')
        add_phone(cur, 5, '6666')
        add_phone(cur, 1, '7777')
        add_phone(cur, 8, '2222')

        #проверка функции update_client
        update_client(cur, 1, 'Иван2', 'Петров2', None, '11112')
        update_client(cur, 2, 'Сергей2', 'Антонов2', 'antonov@mail2.ru2', '22223')
        update_client(cur, None, 'Андрей3', 'Сапогов3', 'sapogov@mail.ru3', '11113')
        update_client(cur, 10, 'Андрей3', 'Сапогов3', 'sapogov@mail.ru3', '11113')

        #проверка функции delete_phone
        delete_phone(cur, 1, 4444)
        delete_phone(cur, 2, )
        delete_phone(cur, 2 , 5555)
        delete_phone(cur, 9, 1111)
        delete_phone(cur, 1, 6666)
        delete_phone(cur, 3, 3333)

        # Проверка функции del_client
        # del_client(cur, 1)
        # del_client(cur, 1)
        find_client(cur, first_name='Иван2')
        find_client(cur, surname='Сергев')
        find_client(cur, phone_number=3333)
        find_client(cur, first_name='Дима')
conn.close()