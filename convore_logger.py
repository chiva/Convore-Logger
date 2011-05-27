#!/usr/bin/python
#-*- coding: utf-8 -*-

import requests
import json
import argparse
import sys

def request(url,conv_auth):
    r = requests.get(url, auth=conv_auth)
    return json.loads(r.content)

parser = argparse.ArgumentParser(description='Dumps a Convore topic.',
                                 epilog='For all the Ardumaniacs out there')
parser.add_argument('-u', help='user name @ Convore', dest='username', required=True)
parser.add_argument('-p', help='password', dest='password', required=True, nargs='+')
parser.add_argument('-g', help='group name', dest='group', required=True, nargs='+')
parser.add_argument('-t', help='topic title', dest='topic', required=True, nargs='+')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

conv_auth = (args.username, ' '.join(args.password))
r = requests.get('https://convore.com/api/account/verify.json', auth=conv_auth)
try:
    assert r.status_code == 200
except AssertionError:
    print "Error de conexion o de credenciales"
    sys.exit(1)
print "Inicio sesion correcto"

response = request('https://convore.com/api/groups.json', conv_auth)

print "Buscando grupo: "+' '.join(args.group)
for message in response['groups']:
    if message['name'] == ' '.join(args.group).encode('utf-8'):
        print "Grupo:",message['id']
        group_id=message['id']
try:
    assert group_id
except NameError:
    print "Grupo no encontrado"
    sys.exit(2)

print "Buscando tema: "+' '.join(args.topic)
response = request('https://convore.com/api/groups/'+group_id+'/topics.json', conv_auth)
for message in response['topics']:
    if message['name'] == ' '.join(args.topic).encode('utf-8'):
        print "Tema:",message['id']
        topic_id=message['id']
try:
    assert topic_id
except NameError:
    print "Tema no encontrado"
    sys.exit(3)

#obtener todos los fragmentos de conversacion
print "Obteniendo fragmentos conversacion"
fragments=[]
response = request('https://convore.com/api/topics/'+topic_id+'/messages.json', conv_auth)
print "1 pagina -> id="+response['until_id']

if response['until_id'] != None:
    fragments.append(response['until_id'])
    while True:
        response = request('https://convore.com/api/topics/'+topic_id+'/messages.json?until_id='+fragments[-1], conv_auth)
        if response['until_id'] != None:
            fragments.append(response['until_id'])
            print str(len(fragments))+" paginas -> id="+fragments[-1]
        else:
            print str(len(fragments)+1)+" paginas"
            break

#obtener la conversacion desde el principio
print "Creando archivo de log"
f = open('log.txt', 'w')
try:
    while True:
        response = request('https://convore.com/api/topics/'+topic_id+'/messages.json?until_id='+fragments.pop(), conv_auth)
        print "Guardando pagina "+str(len(fragments)+2)
        for message in response['messages']:
            line = message['user']['username']+u': '+message['message']+u'\n\r'
            f.write(line.encode('utf-8'))
except IndexError:
    response = request('https://convore.com/api/topics/'+topic_id+'/messages.json', conv_auth)
    print "Guardando pagina 1"
    for message in response['messages']:
            line = message['user']['username']+u': '+message['message']+u'\n\r'
            f.write(line.encode('utf-8'))
print "Cerrando archivo de log"
f.close()
print "----Backup realizado exitosamente----"