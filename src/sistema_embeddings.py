import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from typing import List, Dict, Any, Tuple
import os


class SistemaEmbeddings:
    def __init__(
        self,
        modelo_nombre: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        """
        Inicializa el sistema de embeddings

        Args:
            modelo_nombre: Nombre del modelo de sentence transformers para español
        """
        print(f"🤖 Cargando modelo de embeddings: {modelo_nombre}")
        self.modelo = SentenceTransformer(modelo_nombre)
        self.dimension = self.modelo.get_sentence_embedding_dimension()
        self.index = None
        self.documentos = []

    def crear_embeddings(self, documentos: List[Dict[str, Any]]) -> np.ndarray:
        """Crea embeddings para una lista de documentos"""
        print(f"🔄 Generando embeddings para {len(documentos)} documentos...")

        textos = []
        for doc in documentos:
            # Combinar nombre de materia con contenido para mejor contexto
            texto_completo = f"{doc['metadatos']['materia_nombre']}: {doc['contenido']}"
            textos.append(texto_completo)

        # Generar embeddings en lotes para eficiencia
        embeddings = self.modelo.encode(
            textos, batch_size=32, show_progress_bar=True, convert_to_numpy=True
        )

        return embeddings

    def crear_indice_faiss(self, embeddings: np.ndarray):
        """Crea un índice FAISS para búsqueda rápida"""
        print(
            f"🗃️ Creando índice FAISS con {len(embeddings)} vectores de dimensión {self.dimension}"
        )

        # Usar IndexFlatIP para similitud coseno (Inner Product tras normalización)
        self.index = faiss.IndexFlatIP(self.dimension)

        # Normalizar embeddings para usar producto interno como similitud coseno
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Agregar al índice
        self.index.add(embeddings_norm.astype(np.float32))

        print(f"✅ Índice creado con {self.index.ntotal} vectores")

    def procesar_documentos(
        self, archivo_documentos: str = "documentos_rag_final.json"
    ):
        """Procesa documentos completos: embeddings + índice"""
        print("📚 Cargando documentos...")
        with open(archivo_documentos, "r", encoding="utf-8") as f:
            self.documentos = json.load(f)

        # Crear embeddings
        embeddings = self.crear_embeddings(self.documentos)

        # Crear índice FAISS
        self.crear_indice_faiss(embeddings)

        return self

    def buscar_similares(
        self, consulta: str, k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Busca documentos similares a una consulta

        Args:
            consulta: Texto de la consulta
            k: Número de resultados a devolver

        Returns:
            Lista de tuplas (documento, score_similitud)
        """
        if self.index is None:
            raise ValueError("Debe procesar documentos primero")

        # Generar embedding de la consulta
        embedding_consulta = self.modelo.encode([consulta], convert_to_numpy=True)
        embedding_consulta = embedding_consulta / np.linalg.norm(
            embedding_consulta, axis=1, keepdims=True
        )

        # Buscar en el índice
        scores, indices = self.index.search(embedding_consulta.astype(np.float32), k)

        # Devolver documentos con scores
        resultados = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documentos):  # Verificar índice válido
                documento = self.documentos[idx]
                resultados.append((documento, float(score)))

        return resultados

    def guardar_sistema(self, directorio: str = "rag_sistema"):
        """Guarda el sistema completo (índice + documentos + modelo)"""
        os.makedirs(directorio, exist_ok=True)

        # Guardar índice FAISS
        faiss.write_index(self.index, os.path.join(directorio, "indice.faiss"))

        # Guardar documentos
        with open(
            os.path.join(directorio, "documentos.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.documentos, f, ensure_ascii=False, indent=2)

        # Guardar metadatos del sistema
        metadatos = {
            "modelo_nombre": (
                self.modelo.model_name
                if hasattr(self.modelo, "model_name")
                else "unknown"
            ),
            "dimension": self.dimension,
            "total_documentos": len(self.documentos),
            "total_vectores": self.index.ntotal if self.index else 0,
        }

        with open(
            os.path.join(directorio, "metadatos.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(metadatos, f, ensure_ascii=False, indent=2)

        print(f"💾 Sistema RAG guardado en: {directorio}")

    def cargar_sistema(self, directorio: str = "rag_sistema"):
        """Carga un sistema RAG previamente guardado"""
        print(f"📂 Cargando sistema RAG desde: {directorio}")

        # Cargar índice FAISS
        self.index = faiss.read_index(os.path.join(directorio, "indice.faiss"))

        # Cargar documentos
        with open(
            os.path.join(directorio, "documentos.json"), "r", encoding="utf-8"
        ) as f:
            self.documentos = json.load(f)

        # Cargar metadatos
        with open(
            os.path.join(directorio, "metadatos.json"), "r", encoding="utf-8"
        ) as f:
            metadatos = json.load(f)

        print(
            f"✅ Sistema cargado: {metadatos['total_documentos']} documentos, {metadatos['total_vectores']} vectores"
        )
        return self


def test_sistema():
    """Función de prueba del sistema"""
    print("🧪 Probando sistema de embeddings...")

    sistema = SistemaEmbeddings()
    sistema.procesar_documentos()

    # Pruebas de búsqueda
    consultas_test = [
        "horarios de clases",
        "correlativas de análisis matemático",
        "programa de la materia",
        "carrera de computación",
        "requisitos para cursar",
    ]

    print("\n🔍 Probando búsquedas:")
    for consulta in consultas_test:
        print(f"\n❓ Consulta: '{consulta}'")
        resultados = sistema.buscar_similares(consulta, k=3)

        for i, (doc, score) in enumerate(resultados[:2], 1):
            print(f"   {i}. [{score:.3f}] {doc['metadatos']['materia_nombre']}")
            print(f"      {doc['contenido'][:100]}...")

    # Guardar sistema
    sistema.guardar_sistema()

    return sistema


def main():
    """Función principal para crear el sistema RAG"""
    # Crear sistema de embeddings
    sistema = SistemaEmbeddings()

    # Procesar documentos
    sistema.procesar_documentos()

    # Guardar sistema
    sistema.guardar_sistema()

    # Hacer pruebas básicas
    print("\n" + "=" * 50)
    print("🧪 REALIZANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)

    consultas_test = [
        "¿Cuáles son los horarios de análisis matemático?",
        "¿Qué correlativas tiene la materia de algoritmos?",
        "¿Cómo es el programa de bases de datos?",
    ]

    for consulta in consultas_test:
        print(f"\n❓ {consulta}")
        resultados = sistema.buscar_similares(consulta, k=2)

        for i, (doc, score) in enumerate(resultados, 1):
            print(f"   {i}. [{score:.3f}] {doc['metadatos']['materia_nombre']}")
            print(f"      📄 {doc['contenido'][:150]}...")


if __name__ == "__main__":
    main()
