#!/usr/bin/env python3
"""
Script para explorar la estructura específica de lcd.exactas.uba.ar/materias
y entender cómo están organizadas las materias
"""

import requests
from bs4 import BeautifulSoup
import re


def explorar_estructura_pagina():
    """Explora la estructura de la página LCD materias"""
    url = "https://lcd.exactas.uba.ar/materias"
    
    try:
        print(f"Explorando estructura de: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n=== ESTRUCTURA GENERAL ===")
        
        # Encontrar elementos principales
        title = soup.find('title')
        if title:
            print(f"Titulo: {title.get_text().strip()}")
        
        # Buscar encabezados
        print("\n=== ENCABEZADOS ENCONTRADOS ===")
        for i, header in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])[:10], 1):
            texto = header.get_text().strip()
            if texto:
                print(f"{i}. {header.name.upper()}: {texto[:100]}")
        
        # Buscar párrafos que mencionen materias específicas
        print("\n=== PARRAFOS CON MATERIAS MENCIONADAS ===")
        paragrafos = soup.find_all('p')
        materias_keywords = ['álgebra', 'análisis', 'algoritmos', 'probabilidad', 'laboratorio', 'datos']
        
        contador = 0
        for p in paragrafos:
            texto = p.get_text().strip().lower()
            if any(keyword in texto for keyword in materias_keywords):
                contador += 1
                if contador <= 5:  # Mostrar solo los primeros 5
                    print(f"{contador}. {p.get_text().strip()[:150]}...")
        
        # Buscar listas
        print("\n=== LISTAS ENCONTRADAS ===")
        listas = soup.find_all(['ul', 'ol'])
        for i, lista in enumerate(listas[:3], 1):
            print(f"\nLista {i}:")
            items = lista.find_all('li')[:5]  # Primeros 5 items
            for j, item in enumerate(items, 1):
                texto = item.get_text().strip()
                if texto:
                    print(f"  {j}. {texto[:100]}")
        
        # Buscar divs con clases específicas
        print("\n=== DIVS CON CLASES RELEVANTES ===")
        divs_con_clase = soup.find_all('div', class_=True)
        clases_relevantes = []
        for div in divs_con_clase:
            clases = div.get('class', [])
            for clase in clases:
                if any(keyword in clase.lower() for keyword in ['content', 'main', 'body', 'materias', 'plan']):
                    clases_relevantes.append(clase)
        
        clases_unicas = list(set(clases_relevantes))[:10]
        for clase in clases_unicas:
            print(f"  - {clase}")
        
        # Buscar links específicos
        print("\n=== LINKS RELEVANTES ===")
        links = soup.find_all('a', href=True)
        links_materias = []
        for link in links:
            href = link.get('href', '')
            texto = link.get_text().strip()
            if any(keyword in href.lower() or keyword in texto.lower() 
                   for keyword in ['materia', 'plan', 'correlativa', 'horario']):
                links_materias.append((texto[:50], href))
        
        for i, (texto, href) in enumerate(links_materias[:5], 1):
            print(f"{i}. {texto} -> {href}")
        
        # Examinar contenido de texto específicamente
        print("\n=== BUSQUEDA ESPECIFICA DE MATERIAS ===")
        todo_texto = soup.get_text()
        
        # Buscar patrones específicos de plan de estudios
        patrones_plan = [
            r'Álgebra\s+I[^\w]',
            r'Análisis\s+[IVX]+[^\w]',
            r'Algoritmos\s+y\s+Estructuras\s+de\s+Datos\s+[IVX]+',
            r'Laboratorio\s+de\s+Datos',
            r'Probabilidad\s+y\s+Estadística',
            r'CBC.*Análisis.*Álgebra'
        ]
        
        for patron in patrones_plan:
            matches = re.finditer(patron, todo_texto, re.IGNORECASE)
            for match in matches:
                inicio = max(0, match.start() - 50)
                fin = min(len(todo_texto), match.end() + 50)
                contexto = todo_texto[inicio:fin].replace('\n', ' ')
                print(f"ENCONTRADO: {match.group()} en contexto: ...{contexto}...")
                break  # Solo el primer match de cada patrón
        
        print(f"\n=== RESUMEN ===")
        print(f"Total de párrafos: {len(paragrafos)}")
        print(f"Total de listas: {len(listas)}")
        print(f"Total de links: {len(links)}")
        print(f"Longitud total del texto: {len(todo_texto)} caracteres")
        
    except Exception as e:
        print(f"Error explorando estructura: {e}")


if __name__ == "__main__":
    explorar_estructura_pagina()