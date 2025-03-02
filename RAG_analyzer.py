from datetime import datetime
import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.globals import set_debug
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage
import requests.exceptions
from dotenv import load_dotenv
from github_getter import GitHubAnalyzer
from Briefing_analyzer import ComplianceAnalyzer
from RAG_process import RepoRAGProcessor

class LLMClient:
    def __init__(
        self, 
        groq_api_key: Optional[str] = None,
        groq_model: str = "mixtral-8x7b-32768",
        ollama_model: str = "mistral:latest",
        logger: Optional[logging.Logger] = None,
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model
        self.ollama_model = ollama_model
        self.logger = logger or logging.getLogger(__name__)
        self.using_ollama = False

        set_debug(True)
        self._initialize_llm()
        
    def _initialize_llm(self):
        try:
            if not self.groq_api_key:
                raise ValueError("No Groq API key provided")
                
            self.llm = ChatGroq(
                api_key=self.groq_api_key,
                model_name=self.groq_model,
                max_retries=0
            )
            self.using_ollama = False
            self.logger.info(f"Successfully initialized Groq model: {self.groq_model}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Groq: {e}. Falling back to Ollama")
            self._switch_to_ollama()
    
    def _switch_to_ollama(self) -> bool:
        try:
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
            self.llm = Ollama(
                model=self.ollama_model,
                callback_manager=callback_manager
            )
            self.using_ollama = True
            self.logger.info(f"Switched to Ollama model: {self.ollama_model}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {e}")
            return False
    
    def invoke(self, messages: List) -> str:
        try:
            response = self.llm.invoke(messages)
            
            # Extract text content from response
            if self.using_ollama:
                return str(response).strip()
            else:
                if hasattr(response, 'content'):
                    return response.content.strip()
                elif isinstance(response, dict) and 'content' in response:
                    return response['content'].strip()
                elif isinstance(response, str):
                    return response.strip()
                else:
                    raise ValueError(f"Unexpected response format: {type(response)}")
                    
        except requests.exceptions.HTTPError as http_err:
            if hasattr(http_err.response, 'status_code') and http_err.response.status_code in [413, 429]:
                self.logger.warning(f"Groq API error {http_err.response.status_code}, switching to Ollama")
                if self._switch_to_ollama():
                    return self.invoke(messages)
            raise
        except Exception as e:
            self.logger.error(f"Error invoking LLM: {e}")
            if not self.using_ollama and self._switch_to_ollama():
                return self.invoke(messages)
            raise

class GitHubRAGAnalyzer:
    def __init__(
        self,
        model_name: str = "mixtral-8x7b-32768",
        api_key: str = None,
        ollama_model: str = 'mistral:latest',
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        load_dotenv()
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.llm_client = LLMClient(
            groq_api_key=api_key,
            groq_model=model_name,
            ollama_model=ollama_model,
            logger=self.logger
        )
        self.github_analyzer = GitHubAnalyzer()
        self.compliance_analyzer = ComplianceAnalyzer()
        self.rag_processor = RepoRAGProcessor(embedding_model_name=embedding_model)

    def analyze_requirements_completion(self, repo_url: str, briefing_path: str) -> Dict[str, Any]:
        try:
            # Get repository content
            self.logger.info(f"Starting analysis for repository: {repo_url}")
            repo_path = self.github_analyzer.clone_repo(repo_url)
            if not repo_path:
                raise ValueError("Failed to clone repository")
            self.logger.info(f"Repository cloned to: {repo_path}")
            
            # Process repository to RAG
            self.logger.info("Starting repository processing...")
            repo_success = self.rag_processor.process_repository(repo_path)
            if not repo_success:
                self.logger.error("Repository processing failed")
                raise ValueError("Failed to process repository content")
            self.logger.info("Repository processing completed successfully")
            
            # Process briefing into RAG
            self.logger.info(f"Processing briefing document: {briefing_path}")
            if not os.path.exists(briefing_path):
                self.logger.error(f"Briefing file not found: {briefing_path}")
                raise ValueError(f"Briefing file not found: {briefing_path}")
                
            briefing_success = self.rag_processor.process_briefing(briefing_path)
            if not briefing_success:
                self.logger.error("Briefing processing failed")
                raise ValueError("Failed to process briefing document")
            self.logger.info("Briefing processing completed successfully")
            
            # Get repository statistics
            repo_stats = self.github_analyzer.get_repo_stats(repo_url)
            detected_technologies = self.rag_processor.technologies if hasattr(self.rag_processor, 'technologies') else {}

            # Get briefing content
            analysis_queries = [
                "¿Qué requisitos técnicos establece el briefing?",
                "¿Qué componentes y funcionalidades tiene este repositorio?",
                "¿Cómo se estructura y organiza el código en este repositorio?",
                "¿Qué arquitectura y tecnologías se utilizan en este proyecto?",
                "¿Qué frameworks, librerías y herramientas están configuradas en el proyecto?",
                "¿Qué archivos de configuración de dependencias existen en el repositorio?"
            ]

            context_parts = []
            for query in analysis_queries:
                retrieved_context = self.rag_processor.get_formatted_context(query, k=5)
                context_parts.append(f"Consulta: {query}\n{retrieved_context}")
            
            rag_context = "\n\n".join(context_parts)
            
            prompt = f"""
            You are an AI/ML Technical Analyst with expertise in code quality assessment, AI-generated code detection, and technical debt evaluation. Your task is to critically analyze a GitHub repository from bootcamp students, considering multi-level objectives from the briefing (up to 4 levels: essential/medium/advanced/expert) and highlighting key elements for teacher review.

            **Input Data:**
            1. RAG CONTEXT (Briefing with possible multi-level objectives):
            {rag_context}

            2. DETECTED TECHNOLOGIES (JSON):
            {json.dumps(detected_technologies, indent=2, ensure_ascii=False)}

            3. REPOSITORY STATISTICS (JSON):
            {json.dumps(repo_stats, indent=2, ensure_ascii=False)}

            **Analysis Instructions:**
            1. Multi-Level Objective Mapping:
            - Identify which briefing levels (essential/medium/advanced/expert) are present
            - Evaluate differentiated compliance by level with concrete evidence
            - Highlight attempts to reach higher objectives not required (critical positive)

            2. Deep Technical Analysis:
            - Compare actual architecture vs. expected by complexity level
            - Evaluate suspicious code patterns (over-engineering or risky simplifications)
            - Analyze key metrics: coupling, cohesion, cyclomatic complexity

            3. AI Detection with Educational Context:
            - Look for atypical patterns for students (advanced syntax without conceptual foundation)
            - Analyze correlation between commit complexity and technical leaps
            - Calculate probability of AI-generated code with pedagogical indicators

            4. Learning-Oriented Recommendations:
            - Prioritize improvements that close gaps between achieved vs. expected levels
            - Point out "technical patches" that demonstrate conceptual misunderstandings
            - Suggest refactors that strengthen MLOps fundamentals

            **Output Requirements (in Spanish):**
            Generate the response translated to Spanish, using markdown with this structure as reference on how to output the analysis:

            1. **Multi-Level Technical Analysis**  
            - Implemented Architecture vs. Expected by Level
            - Key Technologies and Objective Compliance
            - Critical Points of Educational Technical Debt

            2. **Levels of Objectives Achieved**  
            - ✅❌ Essential: Analysis with specific evidence
            - ➕/− Medium: Detected partial implementations
            - ⚠️ Advanced/Expert: Meritorious attempts or conceptual errors

            3. **AI Use and Pedagogical Warning Signs**  
            - Estimated Probability (%) and Key Patterns
            - Suspicious Sections (e.g., Complex model without basic data pipeline)
            - Inconsistencies between Code Complexity and Versioning Practices

            4. **Prioritized Improvements for Technical Maturity**  
            - Actions to Consolidate Current Level
            - Preparation for Higher Objectives
            - Conceptual Errors to Review Urgently

            5. **Elements for Teacher Review**  
            - Code with High Risk of "Smart Copying"
            - Implementations that Mask Misunderstanding
            - Anomalous Metrics (e.g., High test coverage with untestable logic)

            **Critical Approach:**  
            - Directly relate technical findings to learning stages  
            - Highlight discrepancies between technical ambition and fundamentals  
            - Point out both exceptional progress and dangerous shortcuts  
            - Use concrete examples from the code for each observation  
            """

            # Get analysis from LLM
            messages = [
                SystemMessage(content="Eres un analista técnico que evalúa proyectos de IA en español."),
                HumanMessage(content=prompt)
            ]
            
            try:
                analysis = self.llm_client.invoke(messages)
                
                # Clean and encode the response
                cleaned_analysis = analysis.encode('utf-8', errors='ignore').decode('utf-8').strip()

                required_sections = [
                {
                    "number": "1", 
                    "keywords": [
                        # Spanish keywords
                        "análisis", "técnico", "multinivel", "analisis",
                        # English keywords  
                        "analysis", "technical", "multilevel", "multi-level"
                    ]
                },
                {
                    "number": "2", 
                    "keywords": [
                        # Spanish keywords
                        "niveles", "objetivos", "alcanzados", "logrados",
                        # English keywords
                        "levels", "objectives", "achieved", "goals", "reached"
                    ]
                },
                {
                    "number": "3", 
                    "keywords": [
                        # Spanish keywords
                        "uso", "ia", "señales", "alerta", "pedagógica", "pedagogica", "ai", 
                        # English keywords
                        "use", "ai", "signs", "warning", "pedagogical", "educational"
                    ]
                },
                {
                    "number": "4", 
                    "keywords": [
                        # Spanish keywords
                        "mejoras", "priorizadas", "madurez", "técnica", "tecnica", 
                        # English keywords
                        "improvements", "prioritized", "maturity", "technical"
                    ]
                },
                {
                    "number": "5", 
                    "keywords": [
                        # Spanish keywords
                        "elementos", "revisión", "revision", "docente", 
                        # English keywords
                        "elements", "review", "teacher", "instructor"
                    ]
                }
            ]

                missing_sections = []
                for section in required_sections:
                    # Try multiple formats: "1. Title", "## 1. Title", "1, Title", etc.
                    section_patterns = [
                    rf"{section['number']}\.?\s+.*{keyword}" for keyword in section['keywords']
                ] + [
                    rf"#+\s*{section['number']}\.?\s+.*{keyword}" for keyword in section['keywords']
                ]
                                    
                    # Check if any pattern matches
                    found = False
                    for pattern in section_patterns:
                        import re
                        if re.search(pattern.lower(), cleaned_analysis.lower()):
                            found = True
                            break
                    
                    if not found:
                        # Store the missing section for later addition
                        missing_sections.append(section)
                        self.logger.warning(f"Missing section {section['number']} in analysis")
                
                # Add missing sections if needed
                standard_section_titles = [
                    "1. Análisis Técnico Multinivel",
                    "2. Niveles de Objetivos Alcanzados",
                    "3. Uso de IA y Señales de Alerta Pedagógica",
                    "4. Mejoras Priorizadas para Madurez Técnica",
                    "5. Elementos para Revisión Docente"
                ]
                
                for missing in missing_sections:
                    section_index = int(missing['number']) - 1
                    cleaned_analysis += f"\n\n## {standard_section_titles[section_index]}\nContenido no generado por el modelo"

                
                if not cleaned_analysis:
                    raise ValueError("Empty response after cleaning")
                    
                self.logger.info("Successfully generated analysis")
                
                # Return the response in the format expected by views.py
                return {
                    "project_type": "ml",  # Default to ML if not detected
                    "repository_stats": repo_stats,
                    "tier_analysis": {
                        "evaluacion_general": cleaned_analysis,
                        "analisis_por_nivel": {
                            "nivel_esencial": {
                                "requisitos_cumplidos": [],
                                "requisitos_faltantes": [],
                                "porcentaje_completitud": 0
                            }
                        },
                        "puntuacion_madurez": 0
                    },
                    "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "success"
                }
                
            except Exception as llm_error:
                self.logger.error(f"LLM analysis error: {llm_error}")
                raise ValueError(f"Error during LLM analysis: {str(llm_error)}")

        except Exception as e:
            self.logger.error(f"Error analyzing repository: {e}")
            return {
                "error": str(e),
                "repository": repo_url,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error"
            }