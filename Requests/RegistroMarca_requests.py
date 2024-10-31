# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 20:55:51 2024

@author: Alexander Rios
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import localtime, strptime
from datetime import timedelta
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import relativedelta, MO
from time import localtime, strftime
import time
global pagereports
import pandas as pd
import time
import os
import io
from os.path import exists
import numpy as np
from office365.sharepoint.files.file import File
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from shareplum import Office365, Site
from shareplum.site import Version
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
from openpyxl.utils import get_column_letter
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
import uuid
import certifi
import warnings
import re
import asyncio
import sys

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None
requests.packages.urllib3.disable_warnings() 
site_url ='https://coleyco.sharepoint.com/sites/Automatizaciones/Registro%20marcas'

#Credenciales
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
document_library = os.getenv('DOCUMENT_LIBRARY')

try:
    ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
except Exception as e:
    print(f"Error al establecer conexión: {e}")

#idS = sys.argv[1]
idS = 1774
time.sleep(5)
try:
    def dataframeSP(lista):
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()

        sp_list = lista
        sp_lists = ctx.web.lists
        s_list = sp_lists.get_by_title(sp_list)
        all_items = []
        query = s_list.items

        while True:
            items_to_load = query.get().top(5000)
            ctx.load(items_to_load)
            ctx.execute_query()
            all_items.extend(items_to_load)
            if len(items_to_load) < 5000:
                break
            query = s_list.items.skip(len(all_items)) 

        if all_items:
            columnas = list(all_items[0].properties.keys())
            valores = [list(item.properties.values()) for item in all_items]
            resultado = pd.DataFrame(valores, columns=columnas)
            resultado.set_index("Id", inplace=True)
        else:
            resultado = pd.DataFrame() 

        return resultado
    
except:
    print("No hay datos")

dfRegistroMarca = dataframeSP("Marcas")
dfClases = dataframeSP("Clase_Items")

try:
    df = dfRegistroMarca.query(f"Id == {idS}")
    row = json.loads(df.iloc[0].to_json())
    
except:
    print("El id proporcionado es invalido verifique e intente nuevamemente")
    quit()
    
clases = []

# Asignación de variables con la información para la SIPI
for row, datos in df.iterrows():
    referencia = datos['Referencia']
    identidad = datos['EstoyActuando']
    idCliente = datos['Identificacion']
    cliente = datos['Nombre']
    cliente_upper = datos['Nombre'].upper()
    tipoSigno = datos['SignoDistintivo']
    naturaleza = datos['Tipo']
    denominacion = datos['Denominacion']
    reivindicacion = datos['ColoresReivindicacion']
    descReivindicacion = datos['DescripcionReivindicacion']
    alcance = datos['Alcance']
    transliteracion = datos['Transliteracion']
    poder = datos['Poder']
    numeroFolios = datos['NumeroFolios']
    clase = datos['Clases']
    
print(clase)
clases = [c.strip() for c in clase.split(';')]

cliente_folder_name = cliente.replace(' ', '_')
denominacion_folder_name = denominacion.replace(' ', '_')

def verificar_carpeta_duo(base_folder, denominacion):
    carpeta_cliente = base_folder.folders.get_by_url(denominacion)
    ctx.load(carpeta_cliente)
    try:
        ctx.execute_query()
        print(f"La carpeta '{denominacion}' existe.")
        return carpeta_cliente
    except Exception as e:
        print(f"La carpeta '{denominacion}' no existe.")
        return None

def verificar_carpeta(padre, nombre_carpeta):
    try:
        carpeta = padre.folders.get_by_url(nombre_carpeta)
        ctx.load(carpeta)
        ctx.execute_query()
        return carpeta
    except Exception as e:
        return None
    
def descargar_ultimo_archivo(carpeta, extensiones_permitidas=[".png", ".jpg"]):
    ctx.load(carpeta.files)
    ctx.execute_query()
    
    for file in carpeta.files:
        print(f"Archivo disponible: {file.properties['Name']}")
    
    files = [f for f in carpeta.files if os.path.splitext(f.properties["Name"])[1].lower() in extensiones_permitidas]
    
    if files:
        ultimo_archivo = files[-1]
        file_content = bytearray()
        file_name = ultimo_archivo.properties["Name"]
        ruta_temporal = f"C:/Users/Usuario/Documents/Coleyco/RegistroMarca/temporal/{file_name}"
        
        with io.BytesIO() as output:
            ultimo_archivo.download(output)
            ctx.execute_query()
            # Guardar archivo en ruta temporal
            with open(ruta_temporal, "wb") as file:
                file.write(output.getvalue())
            print(f"Archivo '{file_name}' descargado correctamente en {ruta_temporal}")
        return ruta_temporal
    else:
        print("No se encontraron archivos PNG o JPG en la carpeta.")
        return None

base = ctx.web.lists.get_by_title("Documentos")
ctx.load(base)
ctx.execute_query()

cliente_folder_name = str(cliente).replace(' ', '_').replace('.', '_')
denominacion_folder_name = str(denominacion).replace(' ', '_')

if identidad != 'En nombre propio':
    carpeta_cliente = verificar_carpeta(base.root_folder, cliente_folder_name)
    if carpeta_cliente:
        print(f"La carpeta '{cliente_folder_name}' existe.")
        carpeta_denominacion = verificar_carpeta(carpeta_cliente, denominacion_folder_name)
        if carpeta_denominacion:
            
            ctx.load(carpeta_denominacion.files)
            ctx.execute_query()
            files = carpeta_denominacion.files
            ctx.load(files)
            ctx.execute_query()
            
            def definePathFile(name_file):
                folder = r"C:/Users/Usuario/Documents/Coleyco/RegistroMarca/temporal/"
                name, extension = os.path.splitext(name_file)
                return folder+"poder"+extension

            locationFile = ""
            
            if files:
                first_file = files[0]
                file_content = bytearray()
                with io.BytesIO() as output:
                    locationFile = definePathFile(first_file.properties["Name"])
                    with open(locationFile, "wb") as file:
                        first_file.download(output)
                        ctx.execute_query()
                        file.write(output.getvalue())
                print("Descargado correctamente")
            else:
                print("No hay nada")
                
                
            print(f"La carpeta '{denominacion_folder_name}' existe.")
        
        else:
            print(f"La carpeta '{denominacion_folder_name}' no existe dentro de '{cliente_folder_name}'.")
    else:
        print(f"La carpeta '{cliente_folder_name}' no existe.")

if naturaleza != "Nominativa":
    carpeta_cliente_duo = verificar_carpeta_duo(ctx.web.get_folder_by_server_relative_url(document_library), denominacion)
    if carpeta_cliente_duo:
        print(f"La carpeta '{denominacion}' existe.")
        if carpeta_cliente_duo:
            
            ctx.load(carpeta_cliente_duo.files)
            ctx.execute_query()
            files = carpeta_cliente_duo.files
            ctx.load(files)
            ctx.execute_query()

            def definePathFile(name_file):
                folder = r"C:/Users/Usuario/Documents/Coleyco/RegistroMarca/temporal/"
                name, extension = os.path.splitext(name_file)
                return folder+"ilustracion"+extension


            locationFile_duo = ""
            
            if files:
                first_file = files[0]
                file_content = bytearray()
                with io.BytesIO() as output:
                    locationFile_duo = definePathFile(first_file.properties["Name"])
                    with open(locationFile_duo, "wb") as file:
                        first_file.download(output)
                        ctx.execute_query()
                        file.write(output.getvalue())
                print("Descargado correctamente")
            else:
                print("No hay nada")
                
                
            print(f"La carpeta '{denominacion}' existe.")
        
        else:
            print(f"La carpeta '{denominacion}' no existe dentro de '{denominacion}'.")
    else:
        print(f"La carpeta '{denominacion}' no existe.")


def headers(url):
    headers_form = {}
    if url is None:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:90.0) Gecko/20100101 Firefox/90.0',
        ]

        for user_agent in user_agents:
            headers = {
                'User-Agent': user_agent,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'sipi.sic.gov.co',
                'Origin': 'https://sipi.sic.gov.co',
                'X-MicrosoftAjax': 'Delta=true',
                'X-Requested-With': 'XMLHttpRequest',
            }
            headers_form = headers
         
    return headers_form

#Header formulario
def headers_general(url):
    headers_form = {}
    if url is None:
        headers_form = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'sipi.sic.gov.co',
        'Origin': 'https://sipi.sic.gov.co',
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'X-MicrosoftAjax': 'Delta=true',
        'X-Requested-With': 'XMLHttpRequest',
    }
    return headers_form

def headers_login(url):
    headers_form = {}
    if url is None:
        headers_form = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'sipi.sic.gov.co',
        'Origin': 'https://sipi.sic.gov.co',
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'X-MicrosoftAjax': 'Delta=true',
        'X-Requested-With': 'XMLHttpRequest',
    }
    return headers_form

#Header texto HTML plano
def headers_general_duo(url):
    headers_final = {}
    if url is None:
         headers_final = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/html; charset=utf-8',
            'Host': 'sipi.sic.gov.co',
            'Origin': 'https://sipi.sic.gov.co',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest'
        }
         
    return headers_final

#Header texto HTML plano
def headers_general_tris(url):
    headers_final = {}
    if url is None:
         headers_final = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain; charset=utf-8',
            'Host': 'sipi.sic.gov.co',
            'Origin': 'https://sipi.sic.gov.co',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest'
        }
         
    return headers_final

#Header envió de archivos
def headers_general_quattuor(url):
    headers_final = {}
    if url is None:
         headers_final = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'multipart/form-data',
            'Host': 'sipi.sic.gov.co',
            'Origin': 'https://sipi.sic.gov.co',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest'
        }
         
    return headers_final

def headers_general_quinque(url, boundary):
    headers_final = {}
    if url is None:
         headers_final = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Host': 'sipi.sic.gov.co',
            'Origin': 'https://sipi.sic.gov.co',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest'
        }
         
    return headers_final

def datae(referencia, type_natural, denominacion, transliteracion,idsid,identidad, reivindicacion, script,event, view, viewstategenerator, ct100, viewstate,descReivindicacion, SignoDistintivo):
    data = {}
    if transliteracion == None:
        transliteracion = ''
    
    if reivindicacion == True:
        reivindicacion = '1'
    else:
        reivindicacion = '0'
        
    if identidad == 'En nombre propio':
        identity = '0'
         
    elif identidad == 'Como apoderado':
        identity = '1'
   
    if view == 1:
        data = {
            'ctl00$ScriptManager': script,
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': '',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature': SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': '',
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': reivindicacion,
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'sid': idsid,
        }
    elif view == 2: 
        data = {
            'ctl00$ScriptManager': script,
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': '',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature': SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': reivindicacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': '',
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$ctl10': ct100,
            'sid': idsid,
            '__ASYNCPOST': ''
        }
        
    elif view == 3:
        data = {
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': 'true',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlAgent$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature': SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': descReivindicacion,
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': reivindicacion,
            'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$hfPosition': '',
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': '',
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$ctl10': ct100,
            'sid': idsid,
            '__VIEWSTATE': viewstate
        }
    elif view == 4:
         data = {
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': 'false',
            'ctl00$MainContent$ctrlSaveApp$ctrlPtoRequestList$gvPtoRequest$ctl02$rdbtnSelected':'rdbtnSelected',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlAgent$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature': SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': descReivindicacion,
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': reivindicacion,
            'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$hfPosition': '',
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': '',
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$ctl10': ct100,
            'sid': idsid,
            '__VIEWSTATE': viewstate
        }
         
    elif view == 5:
         data = {
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': 'true',
            'ctl00$MainContent$ctrlSaveApp$ctrlPtoRequestList$gvPtoRequest$ctl02$rdbtnSelected':'rdbtnSelected',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlAgent$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature':SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': '',
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': '',
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': '',
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$ctl10': ct100,
            'sid': idsid,
            '__VIEWSTATE': viewstate
        }
         
    elif view == 6:
        data = {
            '__EVENTTARGET': event,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$hcSaveApp$hfCollapsed': 'false',
            'ctl00$MainContent$ctrlSaveApp$ctrlPtoRequestList$gvPtoRequest$ctl02$rdbtnSelected':'rdbtnSelected',
            'ctl00$MainContent$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlAgent$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$gvCustomers$ctl04$ctl08': '-1',
            'ctl00$MainContent$txtReference': referencia,
            'ctl00$MainContent$ctrlTMEdit$headerCustomer$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity': identity,
            'ctl00$MainContent$ctrlTMEdit$HeaderPriority$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$hdrClassif$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$HeaderInfo$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ddlMarkNature': SignoDistintivo,
            'ctl00$MainContent$ctrlTMEdit$ddlType': type_natural,
            'ctl00$MainContent$ctrlTMEdit$txtDenomination':denominacion,
            'ctl00$MainContent$ctrlTMEdit$txtMarkDesc': '',
            'ctl00$MainContent$ctrlTMEdit$rbtnColor': '',
            'ctl00$MainContent$ctrlTMEdit$txtDisclaimer': '',
            'ctl00$MainContent$ctrlTMEdit$txtTransliteration': '',
            'ctl00$MainContent$ctrlTMEdit$txtTranslation': transliteracion,
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryCode': '',
            'ctl00$MainContent$ctrlTMEdit$ctrlDOAppliedLocationSearchDialog$ctrlCountrySearch$txtCountryname': '',
            'ctl00$MainContent$ctrlPayment$HeaderCollapse1$hfCollapsed': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl03$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl04$txtCertificate': '',
            'ctl00$MainContent$ctrlPayment$ctrlDiscountList$gvDiscount$ctl05$txtCertificate': '',
            'ctl00$MainContent$ctrlExportResult$tbEmail': 'notificaciones@cole-coabogados.com',
            'ctl00$ctl10': ct100,
            'sid': idsid,
            '__VIEWSTATE': viewstate
        }
        
    return data 

def datae_inbox(evento, viewstate,viewstategenerator, ct100):
    data ={}
    data = {
    '__EVENTTARGET': evento,
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    '__VIEWSTATEENCRYPTED': '',
    'ctl00$selectedCulture': '',
    'ctl00$SidebarContent$SidebarExtra$hdrUser$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrTM$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrPT$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrDS$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrProceeding$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrConsultas$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrHeaderSolicitudes$hfCollapsed': '',
    'ctl00$SidebarContent$SidebarExtra$hdrRecursosyTramites$hfCollapsed': '',
    'ctl00$MainContent$headerTask$hfCollapsed': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$hdrCriteria$hfCollapsed': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbIpNumber': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbCalCreationDateStart': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbCalCreationDateEnd': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ddlWFActivity': '-1',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbCalDueToDateStart': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbCalDueToDateEnd': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$tbClientReference': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$txtNrResolution': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlExtUserInCharge$ctrlUserSearch$hdrCriteria$hfCollapsed': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlExtUserInCharge$ctrlUserSearch$txtUsername': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlExtUserInCharge$ctrlUserSearch$ddlStatus': '1',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlWFInboxTaskList$gvWFInboxTask$ctl09$ctl08': '-1',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlWFInboxTaskList$ctrlUserSearchDialog$ctrlUserSearch$hdrCriteria$hfCollapsed': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlWFInboxTaskList$ctrlUserSearchDialog$ctrlUserSearch$txtUsername': '',
    'ctl00$MainContent$ctrlWFInboxTaskSearch$ctrlWFInboxTaskList$ctrlUserSearchDialog$ctrlUserSearch$ddlStatus': '1',
    'ctl00$MainContent$headerDiscussions$hfCollapsed': '',
    'ctl00$MainContent$ctrlDiscussionSearch$hdrCriteria$hfCollapsed': '',
    'ctl00$MainContent$ctrlDiscussionSearch$TxtTitle': '',
    'ctl00$MainContent$ctrlDiscussionSearch$TxtDtCreationFrom': '',
    'ctl00$MainContent$ctrlDiscussionSearch$TxtDtCreationTo': '',
    'ctl00$MainContent$ctrlDiscussionSearch$txtAppNr': '',
    #'ctl00$MainContent$ctrlDiscussionSearch$TxtDtUpdateFrom': '17/08/2024',
    'ctl00$MainContent$ctrlDiscussionSearch$TxtDtUpdateTo': '',
    'ctl00$MainContent$ctrlDiscussionSearch$txtClientReference': '',
    'ctl00$MainContent$ctrlDiscussionSearch$ddlDiscussionStatus': '-1',
    'ctl00$MainContent$ctrlDiscussionSearch$ddlDiscussionReadStatus': '2',
    'ctl00$MainContent$ctrlDiscussionSearch$ctrlExtUserInCharge$ctrlUserSearch$hdrCriteria$hfCollapsed': '',
    'ctl00$MainContent$ctrlDiscussionSearch$ctrlExtUserInCharge$ctrlUserSearch$txtUsername': '',
    'ctl00$MainContent$ctrlDiscussionSearch$ctrlExtUserInCharge$ctrlUserSearch$ddlStatus': '1',
    'ctl00$MainContent$ctrlDiscussionSearch$ctrlDiscussionList$gvwDiscussions$ctl13$ctl10': '10',
    'ctl00$MainContent$ctrlDiscussionSearch$ctrlDiscussionList$gvwDiscussions$ctl13$ctl11': '-1',
    'ctl00$ctl10': ct100,
    'sid': idsid
    }
    return data

def datae_class(viewstate,viewstategenerator, ct100, clase):
    data ={}
    data = {
    'ctl00$ScriptManager': 'ctl00$MainContent$ctrlClassificationEdit$upEdit|ctl00$MainContent$ctrlClassificationEdit$lnkAddClassNoDesc',
    'ctl00$selectedCulture': '',
    'ctl00$MainContent$ctrlClassificationEdit$ddlMarkClassificationNumberToAdd': clase,
    'ctl00$ctl10': ct100,
    '__EVENTTARGET': 'ctl00$MainContent$ctrlClassificationEdit$lnkAddClassNoDesc',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    '__VIEWSTATEENCRYPTED': '',
    '__ASYNCPOST': ''
    }
    return data

def data_class_duo(viewstate,viewstategenerator, ct100, clase):
    data ={}
    data = {
    'ctl00$selectedCulture': '',
    'ctl00$MainContent$ctrlClassificationEdit$hcClassif$hfCollapsed': '',
    'ctl00$MainContent$ctrlClassificationEdit$gvClassifications$ctl02$txtSpecifs': 'Prendas de vestir, calzado, artículos de sombrerería.',
    'ctl00$MainContent$ctrlClassificationEdit$ddlMarkClassificationNumberToAdd': '25',
    'ctl00$ctl10': ct100,
    '__EVENTTARGET': 'ctl00$masterNavigation$btnAccept',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    '__VIEWSTATEENCRYPTED': ''
    }
    return data

def url_converted(texto):
    url_pattern = r'href="(https?://[^"]+)"'
    match = re.search(url_pattern, texto)
    if match:
        extracted_url = match.group(1)
    else:
        print("No se encontró la URL.")
    return extracted_url
   
session = requests.Session()  

# URL de inicio de sesión
login_url = 'https://sipi.sic.gov.co/sipi/Extra/Entity/User/Login.aspx?sid='
base_url = 'https://sipi.sic.gov.co/sipi/Extra/Default.aspx'
baseGet = session.get(base_url, headers=headers(base_url), allow_redirects=False)

if baseGet.status_code == 302:  
    url_final = url_converted(baseGet.text)
    idTransaction = url_final.split("?sid=")[1]
    cookies = session.cookies.get_dict() # Cookies sesión actual
    response_default = session.get(url_final, headers=headers_general_duo(url_final), allow_redirects=False)
    current_url = response_default.url
    idsid = current_url.split("?sid=")[1] if "?sid=" in current_url else None

    print(f"URL actual: {current_url}")
    print(f"SID actual: {idsid}")
else:
    print(f"No se produjo redirección. Código de estado: {baseGet.status_code}")

soup= BeautifulSoup(response_default.text, 'html.parser')
viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
ct100 = soup.find('input', {'name': 'ctl00$ctl05'})['value']
boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
# Definir las cookies, headers y datos para el request
print("Cookies:", cookies)
print("ID Sid:", idsid)

url_defaul_post= f'https://sipi.sic.gov.co/sipi/Extra/Default.aspx?sid={idsid}'

data_default_post ={
    '__EVENTTARGET': 'ctl00$MainContent$lnkLogin',
    '__EVENTARGUMENT': '',
    'sid': idsid,
    'ctl00$ctl05': ct100,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    '__VIEWSTATE': viewstate
}

response_default_login = session.post(url=url_defaul_post,headers=headers_general_quinque(url_defaul_post,boundary), data=data_default_post, allow_redirects=False)
url_final = url_converted(response_default_login.text)
response_default_login_duo = session.get(url_final, headers=headers_general(url_final), allow_redirects=False)
contect_login_text = response_default_login_duo.text
soup= BeautifulSoup(response_default_login_duo.text, 'html.parser') 
viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
ctl00 = soup.find('input', {'name': 'ctl00$ctl10'})['value']

####### LOGIN #########
data_login = {
    '__EVENTTARGET': 'ctl00$MainContent$lnkBtnLogin',
    'ctl00$MainContent$tbLogin': 'coleyco2019',
    'ctl00$MainContent$tbPassword': 'coleyco2019',
    'sid': idsid,
    '__VIEWSTATEENCRYPTED':'',
    '__EVENTARGUMENT':'',
    '__LASTFOCUS':'',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator
}
boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
url_login = f'https://sipi.sic.gov.co/sipi/Extra/Entity/User/Login.aspx?sid={idsid}'
# Estando en pagina de LOGIN mandamos datos de autenticacion
response_login = session.post(url_login,headers=headers_general_quinque(url_login,boundary), data=data_login, allow_redirects=False)
url_final = url_converted(response_login.text)
response_login_more = session.get(url_final, headers=headers_login(url_login), allow_redirects=False)
url_final = url_converted(response_login_more.text)
response_login_inbox = session.get(url_final, headers=headers_login(url_login), allow_redirects=False)
soup= BeautifulSoup(response_login_inbox.text, 'html.parser') 
viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
ctl00 = soup.find('input', {'name': 'ctl00$ctl10'})['value']

url_inbox = url_final

boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
data_inbox = datae_inbox('ctl00$SidebarContent$SidebarExtra$lnkTMKeyin', viewstate, viewstategenerator, ctl00)

response_inbox_unus = session.post(url_inbox, headers=headers_general_quinque(url_inbox,boundary), data= data_inbox)
soup= BeautifulSoup(response_inbox_unus.text, 'html.parser') 
viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
ctl00 = soup.find('input', {'name': 'ctl00$ctl10'})['value']

boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
data_inbox_duo = datae_inbox('ctl00$SidebarContent$SidebarExtra$popup$lnkBtnCancel', viewstate, viewstategenerator, ctl00)

response_inbox_duo = session.post(url_inbox, headers=headers_general_quinque(url_inbox,boundary), data= data_inbox_duo, allow_redirects=False)
url_final = url_converted(response_inbox_duo.text)
url_form= f'https://sipi.sic.gov.co/sipi/Extra/IP/TM/Keyin.aspx?sid={idsid}'
response_form = session.get(url_final, headers=headers_general_duo(url_inbox))
soup= BeautifulSoup(response_form.text, 'html.parser') 
viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
ctl00 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
print("Estado de la respuesta Solicitud Formulario:", response_form.status_code)

if naturaleza == "Mixta":
    type_natural = '3'
    
elif naturaleza == "Figurativa":
    type_natural = '2'

elif naturaleza == "Nominativa":
    type_natural = '1'
    
if tipoSigno == "Marca":
    tipoSigno = '1'
elif tipoSigno == "Marca Colectiva":
    tipoSigno = '2'
elif tipoSigno == "Marca de Certificación":
    tipoSigno = '3'
elif tipoSigno == "Enseña Comercial":
    tipoSigno = '4'
elif tipoSigno == "Lema Comercial":
    tipoSigno = '5'
elif tipoSigno == "Nombre Comercial":
    tipoSigno = '6'
elif tipoSigno == "Denominacion de Origen":
    tipoSigno = '7'
else:
    tipoSigno = '0'
    
######## Registro de Marca en nombre propio ############
if identidad == 'En nombre propio':
    
    if naturaleza == "Nominativa":
        url_search= f'https://sipi.sic.gov.co/sipi/Extra/Entity/Customer/Qbe.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion, script,event,2,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_datae = session.post(url_form,headers=headers_general(url_form), data=data)
        #redirect_response = session.get(url_form, headers=headers_general(url_form))
        print("Estado de la respuesta identidadad como apoderado':", response_datae.status_code)
        content=response_datae.text
        response_datae_duo = session.get(url_form, headers=headers_general(url_form))
        time.sleep(2)
        soup_logo= BeautifulSoup(response_datae_duo.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        #########Agregando Clases###########
        script = 'ctl00$MainContent$ctrlTMEdit$upClassif|ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        data_clase = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_class= session.post(url_form,headers=headers_general(url_form), data=data_clase)
        content_2=response_form_class.text
        url_clase = response_form_class.url
        print("Estado de la respuesta entrada a la clases':", response_form_class.status_code)
        soup= BeautifulSoup(response_form_class.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        if len(clases) == 1:
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico = datae_class(viewstate,viewstategenerator,ct100,clases[0])
            response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
            content_class=response_class.text
            soup= BeautifulSoup(response_class.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            #Subimos la clase
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        else:
            for clasea in clases:
                datico = datae_class(viewstate,viewstategenerator,ct100,clasea)
                response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
                content_class=response_class.text
                soup= BeautifulSoup(response_class.text, 'html.parser')
                viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
                viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
                ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
                
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        # FINAL PARA GUARDAR LA SOLICITUD
        script = ''
        event = 'ctl00$masterNavigation$btnSave'
        datae_save_confirm_close = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm_close = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm_close, allow_redirects=False)
        content_save_confirm_close=response_save_confirm_close.text
        time.sleep(2)
        
        soup_logo= BeautifulSoup(response_save_confirm_close.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        script = ''
        event = 'ctl00$MainContent$ctrlSaveAppConfirm$lnkBtnAccept'
        datae_save_confirm = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm, allow_redirects=False)
        content_save_confirm=response_save_confirm.text
        time.sleep(2)
        print("Estado de la respuesta solicitud confirmar':", response_save_confirm.status_code)
        print("Solicitud de registro de marca realizada con éxito")
        
        #------------------------------ Cambio de estado despues de guardar ----------------------------#
        list_name = "Marcas"
        column_name = "EstadoRobot"
        
        item_id = idS 
        list_obj = ctx.web.lists.get_by_title(list_name)
        item = list_obj.get_item_by_id(item_id)
        item.set_property(column_name, 'Sin revisar por el robot')
        item.update()
        ctx.execute_query() 
       
    elif naturaleza == "Mixta" or naturaleza == "Figurativa":
        
        url_search= f'https://sipi.sic.gov.co/sipi/Extra/Entity/Customer/Qbe.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion, script,event,2,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_datae = session.post(url_form,headers=headers_general(url_form), data=data)
        #redirect_response = session.get(url_form, headers=headers_general(url_form))
        print("Estado de la respuesta identidadad como apoderado':", response_datae.status_code)
        content=response_datae.text
        response_datae_duo = session.get(url_form, headers=headers_general(url_form))
        time.sleep(2)
        soup_logo= BeautifulSoup(response_datae_duo.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']

        #SUBIMO EL LOGOTIPO - ILUSTRACION
        url_logo = f'https://sipi.sic.gov.co/sipi/Extra/Entity/Document/Keyin.aspx?sid={idsid}'

        script = 'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$upDocGrid|ctl00$MainContent$ctrlTMEdit$ctrlPictureList$lnkbtnAddDocument'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$lnkbtnAddDocument'
        dataLogo = datae(referencia,type_natural,denominacion,transliteracion,idsid,identidad,reivindicacion,script,event,2,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_logo = session.post(url_form, headers=headers_general(url_form), data=dataLogo, allow_redirects=False)
        print("Estado de la respuesta logotipo':", response_logo.status_code)
        redirect_response = session.get(url_logo, headers=headers_general(url_form))
        content_poder = redirect_response.text

        soup_logo= BeautifulSoup(redirect_response.text, 'html.parser')
        viewstate_logo= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator_logo = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100_logo = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        name_logo = os.path.basename(locationFile_duo)
        with open(locationFile_duo, 'rb') as f:
            binary_file_duo = f.read()

        # Parámetros del formulario
        data_logo = {
            "__EVENTTARGET": "ctl00$masterNavigation$btnAccept",
            "__EVENTARGUMENT": "",
            "__VIEWSTATEENCRYPTED": "",
            "ctl00$selectedCulture": "",
            "ctl00$ctl10": ct100_logo,
            '__VIEWSTATEGENERATOR': viewstategenerator_logo,
            '__VIEWSTATE': viewstate_logo,
        }
        
        file_logo = {
           'ctl00$MainContent$ctrlDocumentEdit0nputFile': (name_logo,binary_file_duo,'application/jpg')
            }
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        response_logo_duo = session.post(url_logo, headers=headers_general_quinque(url_logo,boundary), data=data_logo, files=file_logo, allow_redirects=False)
        print("Estado de la respuesta logotipo':", response_logo.status_code)
        redirect_response = requests.get(url_form, cookies=cookies, headers=headers_general(url_logo))
        content_logo= redirect_response.text
        time.sleep(2)
        soup_logo= BeautifulSoup(redirect_response.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        #########Agregando Clases###########
        script = 'ctl00$MainContent$ctrlTMEdit$upClassif|ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        data_clase = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_class= session.post(url_form,headers=headers_general(url_form), data=data_clase)
        content_2=response_form_class.text
        url_clase = response_form_class.url
        print("Estado de la respuesta entrada a la clases':", response_form_class.status_code)
        soup= BeautifulSoup(response_form_class.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        if len(clases) == 1:
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico = datae_class(viewstate,viewstategenerator,ct100,clases[0])
            response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
            content_class=response_class.text
            soup= BeautifulSoup(response_class.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            #Subimos la clase
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        else:
            for clasea in clases:
                datico = datae_class(viewstate,viewstategenerator,ct100,clasea)
                response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
                content_class=response_class.text
                soup= BeautifulSoup(response_class.text, 'html.parser')
                viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
                viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
                ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
                
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        # FINAL PARA GUARDAR LA SOLICITUD
        script = ''
        event = 'ctl00$masterNavigation$btnSave'
        datae_save_confirm_close = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm_close = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm_close, allow_redirects=False)
        content_save_confirm_close=response_save_confirm_close.text
        time.sleep(2)
        
        soup_logo= BeautifulSoup(response_save_confirm_close.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        script = ''
        event = 'ctl00$MainContent$ctrlSaveAppConfirm$lnkBtnAccept'
        datae_save_confirm = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm, allow_redirects=False)
        content_save_confirm=response_save_confirm.text
        time.sleep(2)
        print("Estado de la respuesta solicitud confirmar':", response_save_confirm.status_code)
        print("Solicitud de registro de marca realizada con éxito")
        
        #------------------------------ Cambio de estado despues de guardar ----------------------------#
        list_name = "Marcas"
        column_name = "EstadoRobot"
        
        item_id = idS 
        list_obj = ctx.web.lists.get_by_title(list_name)
        item = list_obj.get_item_by_id(item_id)
        item.set_property(column_name, 'Sin revisar por el robot')
        item.update()
        ctx.execute_query() 
        

        
## Registro de Marca como apoderado ############
elif identidad == 'Como apoderado': 
    
    if naturaleza == "Nominativa":
        url_search= f'https://sipi.sic.gov.co/sipi/Extra/Entity/Customer/Qbe.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion, script,event,2,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_datae = session.post(url_form,headers=headers_general(url_form), data=data)
        #redirect_response = session.get(url_form, headers=headers_general(url_form))
        print("Estado de la respuesta identidadad como apoderado':", response_datae.status_code)
        content=response_datae.text
        response_datae_duo = session.get(url_form, headers=headers_general(url_form))
        time.sleep(2)
        soup_logo= BeautifulSoup(response_datae_duo.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$lnkBtnSearch'
        data_customer = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_duo = session.post(url_form,headers=headers_general(url_form), data=data_customer)
        content_2=response_form_duo.text
        time.sleep(2)
        print("Estado de la respuesta cliente':", response_form_duo.status_code)
        soup= BeautifulSoup(response_form_duo.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']

        data_customer_search = {
        'ctl00$ScriptManager': 'ctl00$ScriptManager|ctl00$MainContent$ctrlCustomerSearch$lnkbtnSearch',
        '__EVENTTARGET': 'ctl00$MainContent$ctrlCustomerSearch$lnkbtnSearch',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$selectedCulture':'' ,
        'ctl00$MainContent$ctrlCustomerSearch$hdrCriteria$hfCollapsed': '',
        'ctl00$MainContent$ctrlCustomerSearch$ddlType': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$tbName': cliente_upper,
        'ctl00$MainContent$ctrlCustomerSearch$ddlIdType': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$tbCodeNr': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbPhone': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbMobile': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbEmail': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbAddress': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbZipCode': '',
        'ctl00$MainContent$ctrlCustomerSearch$ddlCountry': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlRegion': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlCity':'-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlTyProfile': '-1',
        'sid': idsid,
        'ctl00$ctl10': ct100,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__VIEWSTATE': viewstate
        }
        response_search = session.post(url_search, headers=headers_general(url_search), data=data_customer_search)
        content_6=response_search.text
        print("Estado de la respuesta cliente encontrado':", response_search.status_code)
        soup= BeautifulSoup(response_search.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        data_selection_custormer = {
            #'scriptManager': 'ctl00$MainContent$ctrlCustomerSearch$upCustomerList|ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl04$ctl03',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$ctrlCustomerSearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlCustomerSearch$ddlType': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$tbName': cliente_upper,
            'ctl00$MainContent$ctrlCustomerSearch$ddlIdType': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$tbCodeNr': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbPhone': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbMobile': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbEmail': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbAddress': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbZipCode': '',
            'ctl00$MainContent$ctrlCustomerSearch$ddlCountry': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlRegion': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlCity': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlTyProfile': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl02$chckbxSelected': 'on',
            'ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl04$ctl08': '-1',
            '__EVENTTARGET': 'ctl00$masterNavigation$btnSelect',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'sid': idsid,
            'ctl00$ctl10': ct100,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEENCRYPTED': ''
        }
        # Generar un boundary único
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        
        ### Seleccion solicitante
        response_selection_custormer = session.post(url_search, headers=headers_general_quinque(url_search,boundary), data=data_selection_custormer, allow_redirects=False)
        print("Estado de la respuesta cliente seleccionado':", response_selection_custormer.status_code)
        response_get_form = session.get(url_form, headers=headers_general(url_search))
        content_7=response_get_form.text
        
        
        soup_poder= BeautifulSoup(response_get_form.text, 'html.parser')
        viewstate_poder= soup_poder.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_poder.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_poder.find('input', {'name': 'ctl00$ctl10'})['value']
        
        # SUBIMO EL PODER
        url_poder = f'https://sipi.sic.gov.co/sipi/Extra/Entity/Document/Keyin.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlDocumentList$lnkBtnAdd'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlDocumentList$lnkBtnAdd'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate_poder,descReivindicacion,tipoSigno)
        response_poder_unus = session.post(url_form,headers=headers_general(url_form), data=data, allow_redirects=False)
        get_customer_duo = session.get(url_poder, headers=headers_general(url_form))
        soup= BeautifulSoup(get_customer_duo.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
    
        with open(locationFile, 'rb') as f:
            binary_file = f.read()
            
        name_file = os.path.basename(locationFile)
        payload = {
            '__EVENTTARGET': 'ctl00$masterNavigation$btnAccept',
            '__EVENTARGUMENT': '',
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$ctrlDocumentEdit$txtPageNumber': '1',
            'sid': idsid,
            'ctl00$ctl10': ct100,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATE': viewstate
            
        }
       
        file_poder = {
           'ctl00$MainContent$ctrlDocumentEdit0nputFile': (name_file,binary_file,'application/pdf')
            }
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        
        try:
            response_poder_tris = session.post(url_poder, cookies=cookies, headers=headers_general_quinque(url_poder,boundary),data=payload,allow_redirects=False, files=file_poder)
            content_duo = response_poder_tris.text
            response_poder_qud = session.get(url_form, headers=headers_general(url_poder))
            soup_logo= BeautifulSoup(response_poder_qud.text, 'html.parser')
            viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
            response_poder_tris.raise_for_status()  
            print('Contenido de la respuesta:', response_poder_tris.text)
        except requests.exceptions.RequestException as e:
            print('Error en la solicitud:', e)
        finally:
            print("archivo subido")
            
        time.sleep(2)
        
        #########Agregando Clases###########
        script = 'ctl00$MainContent$ctrlTMEdit$upClassif|ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        data_clase = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_class= session.post(url_form,headers=headers_general(url_form), data=data_clase)
        content_2=response_form_class.text
        url_clase = response_form_class.url
        print("Estado de la respuesta entrada a la clases':", response_form_class.status_code)
        soup= BeautifulSoup(response_form_class.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        if len(clases) == 1:
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico = datae_class(viewstate,viewstategenerator,ct100,clases[0])
            response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
            content_class=response_class.text
            soup= BeautifulSoup(response_class.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            #Subimos la clase
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        else:
            for clasea in clases:
                datico = datae_class(viewstate,viewstategenerator,ct100,clasea)
                response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
                content_class=response_class.text
                soup= BeautifulSoup(response_class.text, 'html.parser')
                viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
                viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
                ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
                
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        # FINAL PARA GUARDAR LA SOLICITUD
        script = ''
        event = 'ctl00$masterNavigation$btnSave'
        datae_save_confirm_close = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,5,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm_close = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm_close, allow_redirects=False)
        redirect_response = session.get(url_form, headers=headers_general(url_form))
        content_save_confirm_close=redirect_response.text
        time.sleep(2)
        
        soup_logo= BeautifulSoup(redirect_response.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        script = ''
        event = 'ctl00$MainContent$ctrlSaveAppConfirm$lnkBtnAccept'
        datae_save_confirm = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,6,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm, allow_redirects=False)
        redirect_response = session.get(url_form, headers=headers_general(url_form))
        content_save_confirm=redirect_response.text
        time.sleep(2)
        print("Estado de la respuesta solicitud confirmar':", redirect_response.status_code)
        print("Solicitud de registro de marca realizada con éxito")
        
        #------------------------------ Cambio de estado despues de guardar ----------------------------#
        list_name = "Marcas"
        column_name = "EstadoRobot"
        
        item_id = idS 
        list_obj = ctx.web.lists.get_by_title(list_name)
        item = list_obj.get_item_by_id(item_id)
        item.set_property(column_name, 'Sin revisar por el robot')
        item.update()
        ctx.execute_query() 
        

        
    elif naturaleza == "Mixta" or naturaleza == "Figurativa":
        
        url_search= f'https://sipi.sic.gov.co/sipi/Extra/Entity/Customer/Qbe.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$rbtnlIdentity$1'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion, script,event,2,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_datae = session.post(url_form,headers=headers_general(url_form), data=data)
        #redirect_response = session.get(url_form, headers=headers_general(url_form))
        print("Estado de la respuesta identidadad como apoderado':", response_datae.status_code)
        content=response_datae.text
        response_datae_duo = session.get(url_form, headers=headers_general(url_form))
        time.sleep(2)
        soup_logo= BeautifulSoup(response_datae_duo.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlApplicant$lnkBtnSearch'
        data_customer = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_duo = session.post(url_form,headers=headers_general(url_form), data=data_customer)
        content_2=response_form_duo.text
        time.sleep(2)
        print("Estado de la respuesta cliente':", response_form_duo.status_code)
        soup= BeautifulSoup(response_form_duo.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']

        data_customer_search = {
        'ctl00$ScriptManager': 'ctl00$ScriptManager|ctl00$MainContent$ctrlCustomerSearch$lnkbtnSearch',
        '__EVENTTARGET': 'ctl00$MainContent$ctrlCustomerSearch$lnkbtnSearch',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$selectedCulture':'' ,
        'ctl00$MainContent$ctrlCustomerSearch$hdrCriteria$hfCollapsed': '',
        'ctl00$MainContent$ctrlCustomerSearch$ddlType': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$tbName': cliente_upper,
        'ctl00$MainContent$ctrlCustomerSearch$ddlIdType': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$tbCodeNr': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbPhone': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbMobile': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbEmail': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbAddress': '',
        'ctl00$MainContent$ctrlCustomerSearch$tbZipCode': '',
        'ctl00$MainContent$ctrlCustomerSearch$ddlCountry': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlRegion': '-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlCity':'-1',
        'ctl00$MainContent$ctrlCustomerSearch$ddlTyProfile': '-1',
        'sid': idsid,
        'ctl00$ctl10': ct100,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__VIEWSTATE': viewstate
        }
        response_search = session.post(url_search, headers=headers_general(url_search), data=data_customer_search)
        content_6=response_search.text
        print("Estado de la respuesta cliente encontrado':", response_search.status_code)
        soup= BeautifulSoup(response_search.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        data_selection_custormer = {
            #'scriptManager': 'ctl00$MainContent$ctrlCustomerSearch$upCustomerList|ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl04$ctl03',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$ctrlCustomerSearch$hdrCriteria$hfCollapsed': '',
            'ctl00$MainContent$ctrlCustomerSearch$ddlType': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$tbName': cliente_upper,
            'ctl00$MainContent$ctrlCustomerSearch$ddlIdType': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$tbCodeNr': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbPhone': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbMobile': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbEmail': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbAddress': '',
            'ctl00$MainContent$ctrlCustomerSearch$tbZipCode': '',
            'ctl00$MainContent$ctrlCustomerSearch$ddlCountry': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlRegion': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlCity': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ddlTyProfile': '-1',
            'ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl02$chckbxSelected': 'on',
            'ctl00$MainContent$ctrlCustomerSearch$ctrlCustomerList$gvCustomers$ctl04$ctl08': '-1',
            '__EVENTTARGET': 'ctl00$masterNavigation$btnSelect',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'sid': idsid,
            'ctl00$ctl10': ct100,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEENCRYPTED': ''
        }
        # Generar un boundary único
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        
        ### Seleccion solicitante
        response_selection_custormer = session.post(url_search, headers=headers_general_quinque(url_search,boundary), data=data_selection_custormer, allow_redirects=False)
        print("Estado de la respuesta cliente seleccionado':", response_selection_custormer.status_code)
        response_get_form = session.get(url_form, headers=headers_general(url_search))
        content_7=response_get_form.text
        
        
        soup_poder= BeautifulSoup(response_get_form.text, 'html.parser')
        viewstate_poder= soup_poder.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_poder.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_poder.find('input', {'name': 'ctl00$ctl10'})['value']
        
        # SUBIMO EL PODER
        url_poder = f'https://sipi.sic.gov.co/sipi/Extra/Entity/Document/Keyin.aspx?sid={idsid}'
        
        script = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$UpdatePanel1|ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlDocumentList$lnkBtnAdd'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlApplicant$ctrlDocumentList$lnkBtnAdd'
        data = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate_poder,descReivindicacion,tipoSigno)
        response_poder_unus = session.post(url_form,headers=headers_general(url_form), data=data, allow_redirects=False)
        get_customer_duo = session.get(url_poder, headers=headers_general(url_form))
        soup= BeautifulSoup(get_customer_duo.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
    
        with open(locationFile, 'rb') as f:
            binary_file = f.read()
            
        name_file = os.path.basename(locationFile)
        payload = {
            '__EVENTTARGET': 'ctl00$masterNavigation$btnAccept',
            '__EVENTARGUMENT': '',
            '__VIEWSTATEENCRYPTED': '',
            'ctl00$selectedCulture': '',
            'ctl00$MainContent$ctrlDocumentEdit$txtPageNumber': '1',
            'sid': idsid,
            'ctl00$ctl10': ct100,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__VIEWSTATE': viewstate
            
        }
       
        file_poder = {
           'ctl00$MainContent$ctrlDocumentEdit0nputFile': (name_file,binary_file,'application/pdf')
            }
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        
        try:
            response_poder_tris = session.post(url_poder, cookies=cookies, headers=headers_general_quinque(url_poder,boundary),data=payload,allow_redirects=False, files=file_poder)
            content_duo = response_poder_tris.text
            response_poder_qud = session.get(url_form, headers=headers_general(url_poder))
            soup_logo= BeautifulSoup(response_poder_qud.text, 'html.parser')
            viewstate_logo= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator_logo = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100_logo = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
            response_poder_tris.raise_for_status()  
            print('Contenido de la respuesta:', response_poder_tris.text)
        except requests.exceptions.RequestException as e:
            print('Error en la solicitud:', e)
        finally:
            print("archivo subido")
            

        #SUBIMO EL LOGOTIPO - ILUSTRACION
        url_logo = f'https://sipi.sic.gov.co/sipi/Extra/Entity/Document/Keyin.aspx?sid={idsid}'

        script = 'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$upDocGrid|ctl00$MainContent$ctrlTMEdit$ctrlPictureList$lnkbtnAddDocument'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlPictureList$lnkbtnAddDocument'
        dataLogo = datae(referencia,type_natural,denominacion,transliteracion,idsid,identidad,reivindicacion,script,event,2,viewstategenerator_logo,ct100_logo,viewstate_logo,descReivindicacion,tipoSigno)
        response_logo = session.post(url_form, headers=headers_general(url_form), data=dataLogo, allow_redirects=False)
        print("Estado de la respuesta logotipo':", response_logo.status_code)
        redirect_response = session.get(url_logo, headers=headers_general(url_form))
        content_poder = redirect_response.text

        soup_logo= BeautifulSoup(redirect_response.text, 'html.parser')
        viewstate_logo= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator_logo = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100_logo = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        name_logo = os.path.basename(locationFile_duo)
        with open(locationFile_duo, 'rb') as f:
            binary_file_duo = f.read()

        # Parámetros del formulario
        data_logo = {
            "__EVENTTARGET": "ctl00$masterNavigation$btnAccept",
            "__EVENTARGUMENT": "",
            "__VIEWSTATEENCRYPTED": "",
            "ctl00$selectedCulture": "",
            "ctl00$ctl10": ct100_logo,
            '__VIEWSTATEGENERATOR': viewstategenerator_logo,
            '__VIEWSTATE': viewstate_logo,
        }
        
        file_logo = {
           'ctl00$MainContent$ctrlDocumentEdit0nputFile': (name_logo,binary_file_duo,'application/jpg')
            }
        
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        response_logo_duo = session.post(url_logo, headers=headers_general_quinque(url_logo,boundary), data=data_logo, files=file_logo, allow_redirects=False)
        print("Estado de la respuesta logotipo:", response_logo.status_code)
        redirect_response = requests.get(url_form, cookies=cookies, headers=headers_general(url_logo))
        content_logo= redirect_response.text
        time.sleep(2)
        soup_logo= BeautifulSoup(redirect_response.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        
        #########Agregando Clases###########
        script = 'ctl00$MainContent$ctrlTMEdit$upClassif|ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        event = 'ctl00$MainContent$ctrlTMEdit$ctrlClassif$lnkBtnSearch'
        data_clase = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad,reivindicacion,script,event, 2, viewstategenerator, ct100, viewstate,descReivindicacion,tipoSigno)
        response_form_class= session.post(url_form,headers=headers_general(url_form), data=data_clase)
        content_2=response_form_class.text
        url_clase = response_form_class.url
        print("Estado de la respuesta entrada a la clases':", response_form_class.status_code)
        soup= BeautifulSoup(response_form_class.text, 'html.parser')
        viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        
        if len(clases) == 1:
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico = datae_class(viewstate,viewstategenerator,ct100,clases[0])
            response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
            content_class=response_class.text
            soup= BeautifulSoup(response_class.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            #Subimos la clase
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
        else:
            for clasea in clases:
                datico = datae_class(viewstate,viewstategenerator,ct100,clasea)
                response_class = session.post(url_clase,headers=headers_general(url_clase), data=datico)
                content_class=response_class.text
                soup= BeautifulSoup(response_class.text, 'html.parser')
                viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
                viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
                ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
                
            boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
            datico_duo = data_class_duo(viewstate,viewstategenerator,ct100,clases[0])
            response_class_duo = session.post(url_clase,headers=headers_general_quinque(url_clase,boundary), data=datico_duo)
            soup= BeautifulSoup(response_class_duo.text, 'html.parser')
            viewstate= soup.find('input', {'id': '__VIEWSTATE'})['value']
            viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
            ct100 = soup.find('input', {'name': 'ctl00$ctl10'})['value']
            
        
        ##### FINAL PARA GUARDAR LA SOLICITUD ######################
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'
        script = ''
        event = 'ctl00$masterNavigation$btnSave'
        datae_save_confirm_close = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm_close = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm_close, allow_redirects=False)
        content_save_confirm_close=response_save_confirm_close.text
        time.sleep(2)
        
        soup_logo= BeautifulSoup(response_save_confirm_close.text, 'html.parser')
        viewstate= soup_logo.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup_logo.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        ct100 = soup_logo.find('input', {'name': 'ctl00$ctl10'})['value']
        boundary = f'----WebKitFormBoundary{uuid.uuid4().hex}'

        script = ''
        event = 'ctl00$MainContent$ctrlSaveAppConfirm$lnkBtnAccept'
        datae_save_confirm = datae(referencia, type_natural, denominacion, transliteracion, idsid,identidad, reivindicacion,script,event,3,viewstategenerator,ct100,viewstate,descReivindicacion,tipoSigno)
        response_save_confirm = session.post(url_form,headers=headers_general_quinque(url_form,boundary), data=datae_save_confirm, allow_redirects=False)
        content_save_confirm=response_save_confirm.text
        time.sleep(2)
        print("Estado de la respuesta solicitud confirmar':", response_save_confirm.status_code)
        print("Solicitud de registro de marca realizada con éxito")
        
        #------------------------------ Cambio de estado despues de guardar ----------------------------#
        list_name = "Marcas"
        column_name = "EstadoRobot"
        
        item_id = idS 
        list_obj = ctx.web.lists.get_by_title(list_name)
        item = list_obj.get_item_by_id(item_id)
        item.set_property(column_name, 'Sin revisar por el robot')
        item.update()
        ctx.execute_query() 
        
