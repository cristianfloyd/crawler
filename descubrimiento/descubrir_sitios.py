#!/usr/bin/env python3
"""
Script para descubrir y mapear todos los sitios relacionados
con Licenciatura en Ciencas de Datos
"""
import asyncio
import json
import re
import os
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from typing import Dict, Set
from datetime import datetime

# URLs base conocidas - EXPANDIDAS para LCD
URLS_BASE = [
    # URLs principales LCD
    "https://lcd.exactas.uba.ar/materias/",
    
    # Departamentos clave para LCD
    "https://materias.dc.uba.ar/",      # Depto. Computación
    "https://materias.dm.uba.ar/",      # Depto. Matemática  
    "https://materias.ic.fcen.uba.ar/", # Instituto Cálculo
    "https://www.dc.uba.ar/",          # Portal DC
    "https://www.dm.uba.ar/",          # Portal DM
    
    # URLs secundarias
    "https://lcd.exactas.uba.ar/materias-optativas/",
    "https://materias.df.uba.ar/",      # Depto. Física (ya funcionaba)
]

DOMINIO = [
    "uba.ar",
    "exactas.uba.ar",
    "dc.uba.ar", 
    "dm.uba.ar",
    "df.uba.ar",
    "ic.fcen.uba.ar",
]

# Patrones de URLs de interés - MEJORADOS para LCD
PATRONES_INTERES = [
    # Patrones generales
    r"materias?",
    r"horarios?",
    r"cursadas?", 
    r"programas?",
    r"correlativas?",
    r"departamentos?",
    r"carreras?",
    r"calendario",
    r"docentes?",
    r"institutos?",
    r"plan.*estudios?",
    
    # Patrones específicos LCD
    r"algoritmos?",
    r"estructuras?.*datos?",
    r"estadistica",
    r"probabilidad",
    r"programacion",
    r"bases?.*datos?",
    r"machine.*learning",
    r"data.*science",
    r"analisis.*matematico",
    r"algebra.*lineal",
    r"calculo",
    r"optimizacion",
    r"python",
    r"r.*language",
    r"sql",
]

PATRONES_DESINTERES = [
    r"concurso.*abierto",
    r"llamado.*docente",
    r"seminario.*doctorado",
    r"posgrado",
    r"extension",
]

# Departamentos conocidos - EXPANDIDOS
DEPARTAMENTOS_CONOCIDOS = [
    "matematica", "dm",
    "computacion", "dc", 
    "fisica", "df",
    "quimica",
    "ciencias-atmosfera",
    "geologicas",
    "biodiversidad", 
    "ecologia",
    "instituto-calculo", "ic",
]

# Materias core LCD para scoring preferencial
MATERIAS_CORE_LCD = [
    "algoritmos", "estructura", "datos", 
    "analisis matematico", "algebra lineal", "calculo",
    "estadistica", "probabilidad",
    "programacion", "python", "r language",
    "bases datos", "sql",
    "machine learning", "data science",
    "optimizacion", "investigacion operativa",
]


class DescubrirSitios:
    def __init__(self):
        self.sitios_encontrados = {}
        self.urls_visitadas = set()
        self.urls_por_procesar = set()

    async def detectar_tecnologia(self, html_content: str, url: str) -> Dict[str, str]:
        """Detecta la tecnología del sitio web"""
        soup = BeautifulSoup(html_content, "html.parser")
    
        tecnologias = {
            "cms": "desconocido",
            "framework": "desconocido",
            "complejidad": "simple",
        }
    
        # Detectar Mobirise (constructor de sitios estáticos)
        if (
            "mobirise" in html_content.lower()
            or "<!-- Site made with Mobirise" in html_content
            or soup.find(string=re.compile(r"mobirise", re.I))
            or "assets/mobirise/" in html_content
            or "mbr-" in html_content  # Clases CSS típicas de Mobirise
        ):
            tecnologias["cms"] = "mobirise"
            tecnologias["framework"] = "constructor_estatico"
            tecnologias["complejidad"] = "simple"
    
        # Detectar WordPress
        elif (
            "wp-content" in html_content
            or "wordpress" in html_content.lower()
            or soup.find(
                "meta", {"name": "generator", "content": re.compile(r"wordpress", re.I)}
            )
        ):
            tecnologias["cms"] = "wordpress"
    
        # Detectar Drupal
        elif "drupal" in html_content.lower() or soup.find(
            "meta", {"name": "generator", "content": re.compile(r"drupal", re.I)}
        ):
            tecnologias["cms"] = "drupal"
        
        # Detectar Joomla
        elif (
            "joomla" in html_content.lower()
            or "/media/jui/" in html_content
            or "/templates/" in html_content
            or soup.find(
                "meta", {"name": "generator", "content": re.compile(r"joomla", re.I)}
            )
        ):
            tecnologias["cms"] = "joomla"
    
        # Detectar Laravel
        elif (
            "laravel" in html_content.lower()
            or "_token" in html_content
            or "csrf-token" in html_content
            or soup.find("meta", {"name": "csrf-token"})
            or "/vendor/laravel/" in html_content
            or "Laravel" in html_content
        ):
            tecnologias["cms"] = "laravel"
    
        # Detectar Plone
        elif (
            "plone" in html_content.lower()
            or "/portal_css/" in html_content
            or "/portal_javascripts/" in html_content
            or "portal_membership" in html_content
            or soup.find("meta", {"name": "generator", "content": re.compile(r"plone", re.I)})
            or "Plone" in html_content
        ):
            tecnologias["cms"] = "plone"
    
        # Detectar sitios estáticos/simples (solo si no se detectó Mobirise)
        elif len(soup.find_all("script")) < 5:
            tecnologias["cms"] = "estatico"
    
        # Detectar complejidad por JavaScript (excepto para Mobirise que ya se marcó como simple)
        if tecnologias["cms"] != "mobirise":
            scripts = soup.find_all("script")
            if len(scripts) > 10:
                tecnologias["complejidad"] = "compleja"
            elif len(scripts) > 3:
                tecnologias["complejidad"] = "media"
    
        return tecnologias

    def extraer_links_relevantes(self, html_content: str, base_url: str) -> Set[str]:
        """Extrae links relevantes del HTML - MEJORADO con filtros"""
        soup = BeautifulSoup(html_content, "html.parser")
        links_relevantes = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            url_completa = urljoin(base_url, href)
            texto_link = link.get_text().lower().strip()

            # Filtrar solo dominios permitidos
            dominio_permitido = any(dominio in url_completa.lower() for dominio in DOMINIO)
            if not dominio_permitido:
                continue

            # NUEVO: Filtrar patrones de desinterés primero
            es_desinteres = any(
                re.search(patron, href.lower()) or re.search(patron, texto_link) 
                for patron in PATRONES_DESINTERES
            )
            if es_desinteres:
                continue

            # NUEVO: Filtrar URLs demasiado largas o con muchos parámetros
            if len(url_completa) > 200 or url_completa.count('?') > 1:
                continue

            # Buscar patrones de interés (mejorado)
            es_relevante = False
            
            # Buscar patrones generales
            for patron in PATRONES_INTERES:
                if re.search(patron, href.lower()) or re.search(patron, texto_link):
                    es_relevante = True
                    break

            # Buscar departamentos
            if not es_relevante:
                for depto in DEPARTAMENTOS_CONOCIDOS:
                    if depto in href.lower() or depto in texto_link:
                        es_relevante = True
                        break

            # NUEVO: Buscar materias core LCD específicamente
            if not es_relevante:
                for materia in MATERIAS_CORE_LCD:
                    if materia.lower() in texto_link or materia.lower() in href.lower():
                        es_relevante = True
                        break

            if es_relevante:
                links_relevantes.add(url_completa)

        return links_relevantes

    def analizar_contenido_materias(self, html_content: str, url: str = "") -> Dict[str, any]:
        """Analiza si la página contiene información de materias - MEJORADO con scoring LCD"""
        contenido_lower = html_content.lower()
        soup = BeautifulSoup(html_content, "html.parser")

        indicadores = {
            "tiene_materias": False,
            "tiene_horarios": False,
            "tiene_correlativas": False,
            "tiene_programas": False,
            "cantidad_materias_estimada": 0,
            "tipos_informacion": [],
            "score_lcd": 0,  # NUEVO: Score específico LCD
            "es_actual": True,  # NUEVO: Si el contenido es actual
            "ano_detectado": None,  # NUEVO: Año detectado
        }

        # 1. Buscar indicadores de materias (mejorado)
        palabras_clave_materias = ["materia", "asignatura", "cátedra", "curso", "subject"]
        materias_count = 0
        for palabra in palabras_clave_materias:
            count = contenido_lower.count(palabra)
            materias_count += count
            
        if materias_count > 3:
            indicadores["tiene_materias"] = True
            indicadores["cantidad_materias_estimada"] = materias_count

        # 2. Buscar horarios (mejorado con rangos horarios)
        patrones_horarios = [
            r"\d{1,2}:\d{2}\s*[-a]\s*\d{1,2}:\d{2}",  # 14:00-16:00
            r"\d{1,2}\s*hs?\s*[-a]\s*\d{1,2}\s*hs?",  # 14hs-16hs
            "lunes", "martes", "miércoles", "miérc", "jueves", "viernes", "sábado"
        ]
        
        horarios_found = 0
        for patron in patrones_horarios:
            if re.search(patron, contenido_lower):
                horarios_found += 1
                
        if horarios_found > 0:
            indicadores["tiene_horarios"] = True
            indicadores["tipos_informacion"].append("horarios")

        # 3. Buscar correlativas (mejorado)
        patrones_correlativas = [
            "correlativa", "prerrequisito", "requiere.*aprobar", 
            "depende.*de", "prerequisite", "requiere haber", "aprobado"
        ]
        
        for patron in patrones_correlativas:
            if re.search(patron, contenido_lower):
                indicadores["tiene_correlativas"] = True
                indicadores["tipos_informacion"].append("correlativas")
                break

        # 4. Buscar programas (mejorado)
        patrones_programas = [
            "programa", "contenido", "temario", "bibliografía", "bibliography",
            r"unidad.*\d", r"bolilla.*\d", r"tema.*\d", r"cap[íi]tulo.*\d"
        ]
        
        for patron in patrones_programas:
            if re.search(patron, contenido_lower):
                indicadores["tiene_programas"] = True
                indicadores["tipos_informacion"].append("programas")
                break

        # 5. NUEVO: Calcular score LCD específico
        indicadores["score_lcd"] = self._calcular_score_lcd(contenido_lower, url)
        
        # 6. NUEVO: Detectar si el contenido es actual
        indicadores["es_actual"], indicadores["ano_detectado"] = self._detectar_actualidad(contenido_lower, url)
        
        return indicadores

    def _calcular_score_lcd(self, contenido_lower: str, url: str) -> int:
        """Calcula score específico para relevancia LCD"""
        score = 0
        
        # Bonificación por materias core LCD
        for materia in MATERIAS_CORE_LCD:
            if materia.lower() in contenido_lower:
                score += 20  # Bonificación alta por materia core
                
        # Bonificación por departamentos relevantes
        departamentos_lcd = ["computacion", "dc", "matematica", "dm", "instituto", "calculo", "ic"]
        for depto in departamentos_lcd:
            if depto in url.lower() or depto in contenido_lower:
                score += 15
                
        # Bonificación por información crítica
        if "horario" in contenido_lower:
            score += 10
        if "correlativa" in contenido_lower:
            score += 10  
        if "programa" in contenido_lower:
            score += 5
            
        # Bonificación por múltiples días de la semana (indica horarios completos)
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes"]
        dias_encontrados = sum(1 for dia in dias if dia in contenido_lower)
        score += dias_encontrados * 3
        
        return score

    def _detectar_actualidad(self, contenido_lower: str, url: str) -> tuple:
        """Detecta si el contenido es actual (2023+)"""
        # Buscar años en URL y contenido
        anos_url = re.findall(r'20(\d{2})', url)
        anos_contenido = re.findall(r'20(\d{2})', contenido_lower)
        
        anos_encontrados = []
        if anos_url:
            anos_encontrados.extend([int(f"20{ano}") for ano in anos_url])
        if anos_contenido:
            anos_encontrados.extend([int(f"20{ano}") for ano in anos_contenido])
            
        if anos_encontrados:
            ano_mas_reciente = max(anos_encontrados)
            es_actual = ano_mas_reciente >= 2023
            return es_actual, ano_mas_reciente
            
        # Si no se encuentra año, asumir actual si no hay indicadores de obsoleto
        indicadores_obsoleto = ["archivo", "historical", "backup", "old", "deprecated"]
        es_obsoleto = any(ind in contenido_lower for ind in indicadores_obsoleto)
        
        return not es_obsoleto, None

    async def procesar_url(self, crawler, url: str) -> Dict[str, any]:
        """
        Procesa una URL específica.

        Args:
            crawler: Instancia del crawler asíncrono.
            url (str): URL a procesar.

        Returns:
            Dict[str, any]: Diccionario con el resultado del procesamiento de la URL.
        """
        if url in self.urls_visitadas:
            return {
                "url": url,
                "status": "omitido",
                "motivo": "URL ya visitada",
                "timestamp": datetime.now().isoformat(),
            }

        # Excluir dominios deprecated
        parsed_url = urlparse(url)
        if "cms.dm.uba.ar" in parsed_url.netloc:
            print(f"Excluyendo dominio deprecated: {url}")
            return {
                "url": url,
                "status": "omitido",
                "motivo": "Dominio deprecated",
                "timestamp": datetime.now().isoformat(),
            }
        
        # Verificar si la URL pertenece a dominios permitidos
        domain_allowed = any(domain in parsed_url.netloc for domain in DOMINIO)
        if not domain_allowed:
            return {
                "url": url,
                "status": "omitido",
                "motivo": "Dominio no permitido",
                "timestamp": datetime.now().isoformat(),
            }
            return None

        self.urls_visitadas.add(url)

        try:
            print(f"Analizando: {url}")
            result = await crawler.arun(url=url)

            if not result or not result.html:
                return {
                    "url": url,
                    "status": "error",
                    "error": "No se encontró contenido",
                    "timestamp": datetime.now().isoformat(),
                }

            # Analizar tecnología
            tecnologia = await self.detectar_tecnologia(result.html, url)

            # Analizar contenido
            contenido_info = self.analizar_contenido_materias(result.html, url)

            # Extraer links relevantes
            links_encontrados = self.extraer_links_relevantes(result.html, url)

            # Añadir nuevos links para procesar
            for link in links_encontrados:
                if link not in self.urls_visitadas:
                    self.urls_por_procesar.add(link)

            info_sitio = {
                "url": url,
                "titulo": (
                    BeautifulSoup(result.html, "html.parser").title.string
                    if BeautifulSoup(result.html, "html.parser").title
                    else ""
                ),
                "tecnologia": tecnologia,
                "contenido_materias": contenido_info,
                "links_encontrados": list(links_encontrados),
                "status": "exitoso",
                "timestamp": datetime.now().isoformat(),
            }

            return info_sitio

        except Exception as e:
            print(f"Error procesando {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def descubrir_sitios_completo(self, max_urls: int = 50):
        """Proceso completo de descubrimiento"""
        print("Iniciando descubrimiento de sitios...")

        # Inicializar con URLs base
        for url in URLS_BASE:
            self.urls_por_procesar.add(url)

        async with AsyncWebCrawler(verbose=False) as crawler:
            procesados = 0

            while self.urls_por_procesar and procesados < max_urls:
                url = self.urls_por_procesar.pop()

                info_sitio = await self.procesar_url(crawler, url)
                if info_sitio:
                    self.sitios_encontrados[url] = info_sitio

                procesados += 1

                # Mostrar progreso
                if procesados % 5 == 0:
                    print(
                        f"Procesados: {procesados}/{max_urls}, En cola: {len(self.urls_por_procesar)}"
                    )

        print(
            f"Descubrimiento completado: {len(self.sitios_encontrados)} sitios analizados"
        )

    def generar_reporte(self) -> Dict[str, any]:
        """Genera reporte de descubrimiento"""
        reporte = {
            "resumen": {
                "total_sitios": len(self.sitios_encontrados),
                "sitios_exitosos": len(
                    [
                        s
                        for s in self.sitios_encontrados.values()
                        if s["status"] == "exitoso"
                    ]
                ),
                "sitios_con_materias": len(
                    [
                        s
                        for s in self.sitios_encontrados.values()
                        if s.get("contenido_materias", {}).get("tiene_materias", False)
                    ]
                ),
                "timestamp": datetime.now().isoformat(),
            },
            "por_tecnologia": {},
            "por_tipo_contenido": {},
            "sitios_prioritarios": [],
            "sitios_detalle": self.sitios_encontrados,
        }

        # Agrupar por tecnología
        for sitio in self.sitios_encontrados.values():
            if sitio["status"] == "exitoso":
                cms = sitio["tecnologia"]["cms"]
                if cms not in reporte["por_tecnologia"]:
                    reporte["por_tecnologia"][cms] = []
                reporte["por_tecnologia"][cms].append(sitio["url"])
        
        # ordenar tecnologias urls alfabeticamente
        for tecnologia in reporte["por_tecnologia"]:
            reporte["por_tecnologia"][tecnologia].sort()

        # Identificar sitios prioritarios (MEJORADO con scoring LCD)
        for sitio in self.sitios_encontrados.values():
            if (
                sitio["status"] == "exitoso"
                and sitio["contenido_materias"]["tiene_materias"]
            ):
                # Score combinado: materias base + score LCD + actualidad
                score_base = sitio["contenido_materias"]["cantidad_materias_estimada"]
                score_lcd = sitio["contenido_materias"].get("score_lcd", 0)
                es_actual = sitio["contenido_materias"].get("es_actual", True)
                
                # Score final combinado
                score_final = score_base + score_lcd
                if es_actual:
                    score_final += 20  # Bonificación por ser actual
                
                # Solo incluir sitios con score mínimo
                if score_final > 15:
                    prioridad = {
                        "url": sitio["url"],
                        "titulo": sitio["titulo"],
                        "score": score_final,
                        "score_lcd": score_lcd,
                        "score_base": score_base,
                        "tipos_info": sitio["contenido_materias"]["tipos_informacion"],
                        "cms": sitio["tecnologia"]["cms"],
                        "es_actual": es_actual,
                        "ano_detectado": sitio["contenido_materias"].get("ano_detectado"),
                    }
                    reporte["sitios_prioritarios"].append(prioridad)

        # Ordenar por score
        reporte["sitios_prioritarios"].sort(key=lambda x: x["score"], reverse=True)

        return reporte

    def guardar_resultados(self, archivo: str = "inventario_sitios.json"):
        """Guarda los resultados del descubrimiento"""
        reporte = self.generar_reporte()

        # Crear directorio data si no existe y guardar ahí
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(data_dir, exist_ok=True)
        ruta_completa = os.path.join(data_dir, archivo)

        with open(ruta_completa, "w", encoding="utf-8") as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)

        print(f"Inventario guardado en: {ruta_completa}")

        # Mostrar resumen
        print("\nRESUMEN DEL DESCUBRIMIENTO:")
        print(f"   • Total sitios analizados: {reporte['resumen']['total_sitios']}")
        print(f"   • Sitios con materias: {reporte['resumen']['sitios_con_materias']}")
        print(f"   • Sitios prioritarios: {len(reporte['sitios_prioritarios'])}")

        print("\nTOP 10 SITIOS PRIORITARIOS (SCORING LCD):")
        for i, sitio in enumerate(reporte["sitios_prioritarios"][:10], 1):
            titulo_corto = sitio['titulo'][:50] + "..." if len(sitio['titulo']) > 50 else sitio['titulo']
            actualidad = "ACTUAL" if sitio.get('es_actual', True) else f"OLD {sitio.get('ano_detectado', '')}"
            
            print(f"   {i}. {titulo_corto}")
            print(f"      URL: {sitio['url']}")
            print(f"      Score: {sitio['score']} (Base:{sitio.get('score_base', 0)} + LCD:{sitio.get('score_lcd', 0)})")
            print(f"      CMS: {sitio['cms']} | {actualidad}")
            print(f"      Info: {', '.join(sitio['tipos_info'])}")
            print()


async def main():
    descubridor = DescubrirSitios()

    print("DESCUBRIMIENTO DE SITIOS RELACIONADOS CON EXACTAS UBA")
    print("=" * 60)

    await descubridor.descubrir_sitios_completo(max_urls=50)  # Reducido por problemas de encoding
    descubridor.guardar_resultados()

    print("\nProximos pasos REFINADOS:")
    print("   1. Revisar inventario_sitios.json (con scoring LCD mejorado)")
    print("   2. Priorizar sitios Depto. Computacion y Matematica")
    print("   3. Desarrollar scrapers especificos por CMS detectado")
    print("   4. Implementar scraping coordinado con nuevas URLs base")
    print("   5. Validar cobertura de materias core LCD")


if __name__ == "__main__":
    asyncio.run(main())
