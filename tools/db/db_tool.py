# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:47:50 2026

@author: Dmytro
"""
import sqlalchemy
from sqlalchemy import text
import os

engine = sqlalchemy.create_engine(os.environ['DB_DIALECT'] + '+'
                                  + os.environ['DB_DRIVER'] + '://' 
                                  + os.environ['DB_USER'] + ':'
                                  + os.environ['DB_PASS'] + '@'
                                  + os.environ['DB_HOST'] + ':'
                                  + os.environ['DB_PORT'] + '/citrus_nursery')

def search_citrus_trees(type = None, variety = None, min_price = None, 
                        max_price = None, quantity = None):
    query = 'SELECT * FROM citrus_trees'
    where_conditions = []
    result = None
    if(not(type == None)):
        where_conditions.append('type LIKE \'' + type + '\'')
    if(not(variety == None)):
        where_conditions.append('variety LIKE \'' + variety + '\'')
    if(not(min_price == None)):
        where_conditions.append('price >= ' + str(min_price))
    if(not(max_price == None)):
        where_conditions.append('price <= ' + str(max_price))
    if(not(quantity == None)):
        where_conditions.append('quantity >= ' + str(quantity))
    if(len(where_conditions) >0):
        query += ' WHERE '
    with engine.connect() as conn:
        result = conn.execute(
            text(query + ' AND '.join(where_conditions))).mappings().all()
    return result

def create_order(customer_email : str, customer_name : str, 
                 citrus_trees_ids : list):
    with engine.connect() as conn:
        customer_query_result = conn.execute(
            text('SELECT * FROM customers WHERE email LIKE \''
                 + customer_email + '\'')).mappings().all()
        customer_id = None
        if(len(customer_query_result) > 0):
            customer_id = customer_query_result[0]['customer_id']
        else:
            customer_id = conn.execute(text(
                'INSERT INTO customers(email, name) VALUES(\'{}\', \'{}\')'
                .format(customer_email, customer_name))).lastrowid
        order_id = conn.execute(text('INSERT INTO orders(customer_id) VALUES({})'
                                     .format(customer_id))).lastrowid
        for citrus_tree_id in citrus_trees_ids:
            conn.execute(text('''INSERT INTO citrus_trees_to_orders(order_id, 
                              citrus_tree_id) VALUES({}, {})'''.format(order_id,
                         citrus_tree_id)))
        conn.commit()
        return order_id
        

with engine.connect() as conn:

    conn.execute(text('DROP TABLE IF EXISTS citrus_trees_to_orders'))
    conn.execute(text('DROP TABLE IF EXISTS orders'))
    conn.execute(text('DROP TABLE IF EXISTS customers'))
    conn.execute(text('DROP TABLE IF EXISTS citrus_trees'))

    conn.execute(text('''CREATE TABLE citrus_trees(tree_id INT PRIMARY KEY AUTO_INCREMENT, 
                    variety VARCHAR(30), type VARCHAR(30), 
                    price INT NOT NULL CHECK(price > 0),
                    quantity INT DEFAULT 0 CHECK(quantity >= 0))'''))
    conn.execute(text('''CREATE TABLE customers(customer_id INT PRIMARY KEY AUTO_INCREMENT, 
                    email VARCHAR(50) NOT NULL UNIQUE, name VARCHAR(30))''')) 
    conn.execute(text('''CREATE TABLE orders(order_id INT PRIMARY KEY AUTO_INCREMENT, 
                    customer_id INT, 
                    status ENUM('IN_PROGRESS', 'FULFILLED', 'CANCELLED') NOT NULL
                    DEFAULT 'IN_PROGRESS',
                    CONSTRAINT customer_refer FOREIGN KEY(customer_id) 
                    REFERENCES customers(customer_id))'''))               
    conn.execute(text('''CREATE TABLE citrus_trees_to_orders(id INT PRIMARY KEY AUTO_INCREMENT, 
                    citrus_tree_id INT, order_id INT,
                    CONSTRAINT citrus_tree_refer FOREIGN KEY(citrus_tree_id)
                    REFERENCES citrus_trees(tree_id),
                    CONSTRAINT order_refer FOREIGN KEY(order_id)
                    REFERENCES orders(order_id))'''))
               
    citruses = {'mandarin' : [
                {'variety' : 'Owari Satsuma', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Minneola Tangelo', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Nova Clementine', 'price' : 25, 'quantity' : 5},
                {'variety' : 'Murcott', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Mandared', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Corsican Clementine', 'price' : 25, 'quantity' : 5}
                ],
            'orange' : [
                {'variety' : 'Washington Navel', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Valencia', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Hamlin', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Cara Cara', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Chocolate Navel', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Tarocco', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Moro', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Sanguinelli', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Line Late', 'price' : 25, 'quantity' : 5},
                {'variety' : 'Navelatte', 'price' : 25, 'quantity' : 5},
                {'variety' : 'Four seasons', 'price' : 25, 'quantity' : 5}
                ],
            'lemon' : [
                {'variety' : 'Eureka', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Lisbon', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Ponderosa', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Meyer', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Pink Variegated', 'price' : 30, 'quantity' : 5}                
                ],
            'grapefruit' : [
                {'variety' : 'Star Ruby', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Rio Red', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Red Ruby', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Marsh', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Tomphson', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Oroblanco', 'price' : 40, 'quantity' : 5},
                {'variety' : 'Duncan', 'price' : 20, 'quantity' : 5}
                ],
            'kumquat' : [
                {'variety' : 'Nagami', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Meywa', 'price' : 25, 'quantity' : 5},
                {'variety' : 'Marumi', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Orangequat Nippon', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Limequat Eulis', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Limequaat Tavares', 'price' : 30, 'quantity' : 5},
                {'variety' : 'Orangequat Indio', 'price' : 35, 'quantity' : 5},
                {'variety' : 'Lemonquat', 'price' : 25, 'quantity' : 5}
                ],
            'lime' : [
                {'variety' : 'Persian', 'price' : 20, 'quantity' : 5},
                {'variety' : 'Mexican', 'price' : 20, 'quantity' : 5}
                ]
            }

    statement = '''INSERT INTO citrus_trees(variety, type, price, quantity)
                 VALUES('{}', '{}', {}, {})'''
    for citrus_type in citruses.keys():
        for citrus in citruses[citrus_type]:
            result = conn.execute(text(statement.format(citrus['variety'], citrus_type, 
                                          citrus['price'], 
                                          citrus['quantity'])))
    conn.commit()
    
for record in search_citrus_trees(type = 'Mandarin', min_price = 20, 
                                      max_price = 25, quantity = 3):
    print(record)
        
print(create_order('dmytro@mail.com', 'Dmytro', [1, 7, 10, 20]))
print(create_order('johnodonnel@mail.com', 'John O\\\'Donnel', [5, 14, 22]))
print(create_order('dmytro@mail.com', 'Dmytro', [12, 9, 11, 32]))