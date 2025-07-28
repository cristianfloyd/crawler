#!/usr/bin/env python3
"""
Script para descubrir y mapear todos los sitios relacionados
con la Facultad de Ciencias Exactas UBA
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

# URLs base conocidas
URLS_BASE = [
    "https://lcd.exactas.uba.ar/",
]

DOMINIO = [
    "uba.ar",
]

# Patrones de URLs de interés
PATRONES_INTERES = [
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
]

PATRONES_DESINTERES = [
    r"concurso abierto"
],

# Departamentos conocidos
DEPARTAMENTOS_CONOCIDOS = [
    "matematica",
    "computacion",
    "fisica",
    "quimica",
    "ciencias-atmosfera",
    "geologicas",
    "biodiversidad",
    "ecologia",
    "instituto-calculo",
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
        """Extrae links relevantes del HTML"""
        soup = BeautifulSoup(html_content, "html.parser")
        links_relevantes = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            url_completa = urljoin(base_url, href)

            # Filtrar solo dominios de UBA
            if not ("uba.ar" in url_completa or "exactas" in url_completa):
                continue

            # Buscar patrones de interés
            for patron in PATRONES_INTERES:
                if re.search(patron, href.lower()) or re.search(
                    patron, link.get_text().lower()
                ):
                    links_relevantes.add(url_completa)
                    break

            # Buscar departamentos
            for depto in DEPARTAMENTOS_CONOCIDOS:
                if depto in href.lower():
                    links_relevantes.add(url_completa)
                    break

        return links_relevantes

    def analizar_contenido_materias(self, html_content: str) -> Dict[str, any]:
        """Analiza si la página contiene información de materias"""
        contenido_lower = html_content.lower()
        soup = BeautifulSoup(html_content, "html.parser")

        indicadores = {
            "tiene_materias": False,
            "tiene_horarios": False,
            "tiene_correlativas": False,
            "tiene_programas": False,
            "cantidad_materias_estimada": 0,
            "tipos_informacion": [],
        }

        # Buscar indicadores de materias
        palabras_clave_materias = ["materia", "asignatura", "cátedra", "curso"]
        for palabra in palabras_clave_materias:
            if contenido_lower.count(palabra) > 3:
                indicadores["tiene_materias"] = True
                indicadores["cantidad_materias_estimada"] = max(
                    indicadores["cantidad_materias_estimada"],
                    contenido_lower.count(palabra),
                )
                break

        # Buscar horarios
        if any(
            dia in contenido_lower
            for dia in ["lunes", "martes", "miércoles", "jueves", "viernes"]
        ):
            indicadores["tiene_horarios"] = True
            indicadores["tipos_informacion"].append("horarios")

        # Buscar correlativas
        if any(
            palabra in contenido_lower
            for palabra in ["correlativa", "prerrequisito", "requiere"]
        ):
            indicadores["tiene_correlativas"] = True
            indicadores["tipos_informacion"].append("correlativas")

        # Buscar programas
        if any(
            palabra in contenido_lower
            for palabra in ["programa", "contenido", "temario", "bibliografía"]
        ):
            indicadores["tiene_programas"] = True
            indicadores["tipos_informacion"].append("programas")

        return indicadores

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
            print(f"⚠️  Excluyendo dominio deprecated: {url}")
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
            print(f"🔍 Analizando: {url}")
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
            contenido_info = self.analizar_contenido_materias(result.html)

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
            print(f"❌ Error procesando {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def descubrir_sitios_completo(self, max_urls: int = 50):
        """Proceso completo de descubrimiento"""
        print("🚀 Iniciando descubrimiento de sitios...")

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
                        f"📊 Procesados: {procesados}/{max_urls}, En cola: {len(self.urls_por_procesar)}"
                    )

        print(
            f"✅ Descubrimiento completado: {len(self.sitios_encontrados)} sitios analizados"
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

        # Identificar sitios prioritarios
        for sitio in self.sitios_encontrados.values():
            if (
                sitio["status"] == "exitoso"
                and sitio["contenido_materias"]["tiene_materias"]
                and sitio["contenido_materias"]["cantidad_materias_estimada"] > 5
            ):
                prioridad = {
                    "url": sitio["url"],
                    "titulo": sitio["titulo"],
                    "score": sitio["contenido_materias"]["cantidad_materias_estimada"],
                    "tipos_info": sitio["contenido_materias"]["tipos_informacion"],
                    "cms": sitio["tecnologia"]["cms"],
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

        print(f"💾 Inventario guardado en: {ruta_completa}")

        # Mostrar resumen
        print("\n📊 RESUMEN DEL DESCUBRIMIENTO:")
        print(f"   • Total sitios analizados: {reporte['resumen']['total_sitios']}")
        print(f"   • Sitios con materias: {reporte['resumen']['sitios_con_materias']}")
        print(f"   • Sitios prioritarios: {len(reporte['sitios_prioritarios'])}")

        print("\n🎯 TOP 5 SITIOS PRIORITARIOS:")
        for i, sitio in enumerate(reporte["sitios_prioritarios"][:5], 1):
            print(f"   {i}. {sitio['titulo'][:50]}...")
            print(f"      URL: {sitio['url']}")
            print(f"      Score: {sitio['score']}, CMS: {sitio['cms']}")
            print(f"      Info: {', '.join(sitio['tipos_info'])}")
            print()


async def main():
    descubridor = DescubrirSitios()

    print("🔍 DESCUBRIMIENTO DE SITIOS RELACIONADOS CON EXACTAS UBA")
    print("=" * 60)

    await descubridor.descubrir_sitios_completo(max_urls=40)
    descubridor.guardar_resultados()

    print("\n💡 Próximos pasos:")
    print("   1. Revisar inventario_sitios.json")
    print("   2. Priorizar sitios según relevancia")
    print("   3. Desarrollar scrapers específicos")
    print("   4. Implementar scraping coordinado")


if __name__ == "__main__":
    asyncio.run(main())
