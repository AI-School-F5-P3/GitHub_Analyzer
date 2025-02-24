import os
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import render
from reportlab.pdfgen import canvas
from dotenv import load_dotenv
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
from RAG_analyzer import GitHubRAGAnalyzer
from django.http import FileResponse
import logging
import shutil
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from Github_getter import GitHubAnalyzer  # Asegúrate de tener la ruta correcta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import Color
import json

load_dotenv()

def home(request):
    """Vista para renderizar la página principal"""
    return render(request, 'home.html')

def generate_pdf_report(analysis_results, briefing_name):
    """
    Genera un informe PDF detallado de los resultados del análisis
    Args:
        analysis_results: Resultados del análisis del repositorio
        briefing_name: Nombre del archivo briefing original
    Returns:
        str: Ruta al archivo PDF generado
    """
    try:
        # Preparación del nombre y ruta del archivo PDF
        clean_name = briefing_name.lower().replace('.pdf', '')
        pdf_name = f"Informe_Analisis_{clean_name}.pdf"
        pdf_path = os.path.join("static/reports", pdf_name)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # Configuración del documento
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )

        # Estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            spaceBefore=30,
            textColor=Color(0.2, 0.2, 0.2)
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            textColor=Color(0.3, 0.3, 0.3)
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            leftIndent=20,
            spaceAfter=10
        )

        # Contenido del documento
        story = []
        
        # Título del informe
        story.append(Paragraph("Informe de Análisis por Niveles", title_style))
        
        # Tipo de proyecto
        project_type_map = {
            'ml': 'Machine Learning',
            'nlp': 'Procesamiento de Lenguaje Natural',
            'genai': 'IA Generativa'
        }
        story.append(Paragraph(
            f"Tipo de Proyecto: {project_type_map.get(analysis_results['project_type'], 'N/A')}", 
            heading_style
        ))
        
        # Estadísticas del repositorio
        repo_stats = analysis_results['repository_stats']
        story.append(Paragraph("1. Estadísticas del Repositorio", heading_style))
        story.append(Paragraph(
            f"Total Commits: {repo_stats['commit_count']}", 
            normal_style
        ))
        story.append(Paragraph(
            f"Lenguajes: {', '.join([f'{l['name']} ({l['percentage']}%)' for l in repo_stats['languages']])}", 
            normal_style
        ))
        
        # Análisis por niveles
        story.append(Paragraph("2. Análisis por Niveles", heading_style))
        tier_analysis = analysis_results['tier_analysis']
        
        for nivel in ['nivel_esencial', 'nivel_medio', 'nivel_avanzado', 'nivel_experto']:
            nivel_data = tier_analysis['analisis_por_nivel'][nivel]
            story.append(Paragraph(nivel.replace('_', ' ').title(), heading_style))
            story.append(Paragraph(
                f"Completitud: {nivel_data['porcentaje_completitud']}%", 
                normal_style
            ))
            
            if nivel_data['requisitos_cumplidos']:
                story.append(Paragraph("Requisitos Cumplidos:", normal_style))
                for req in nivel_data['requisitos_cumplidos']:
                    story.append(Paragraph(f"• {req}", bullet_style))
            
            if nivel_data['requisitos_faltantes']:
                story.append(Paragraph("Requisitos Faltantes:", normal_style))
                for req in nivel_data['requisitos_faltantes']:
                    story.append(Paragraph(f"• {req}", bullet_style))
            
            story.append(Spacer(1, 12))

        # Análisis técnico
        story.append(Paragraph("3. Análisis Técnico", heading_style))
        tech_analysis = tier_analysis['analisis_tecnico']
        for key, value in tech_analysis.items():
            story.append(Paragraph(
                f"{key.replace('_', ' ').title()}: {value}", 
                normal_style
            ))
        
        # Recomendaciones
        story.append(Paragraph("4. Recomendaciones", heading_style))
        for rec in tier_analysis['recomendaciones']:
            story.append(Paragraph(f"• {rec}", bullet_style))
        
        # Puntuación final
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            f"Puntuación de Madurez: {tier_analysis['puntuacion_madurez']}/100",
            heading_style
        ))

        # Construir el documento
        doc.build(story)
        return pdf_path
        
    except Exception as e:
        logging.error(f"Error generating PDF report: {e}")
        return None

def analysis(request):
    """
    Maneja la solicitud de análisis del repositorio
    Procesa el formulario, realiza el análisis y genera el informe
    """
    if request.method == "POST":
        repo_url = request.POST.get("repo_url")
        briefing_file = request.FILES.get("briefing")
        temp_files = []

        # Validación de entrada
        if not repo_url:
            messages.error(request, "Por favor, proporciona una URL del repositorio")
            return render(request, "analysis.html")

        try:
            analyzer = GitHubRAGAnalyzer()
            
            if briefing_file:
                try:
                    # Guardar archivo de briefing
                    briefing_filename = default_storage.save(
                        f"briefings/{briefing_file.name}", 
                        ContentFile(briefing_file.read())
                    )
                    briefing_path = default_storage.path(briefing_filename)
                    temp_files.append(briefing_path)
                    
                    # Realizar análisis completo
                    analysis_results = analyzer.analyze_requirements_completion(
                        repo_url=repo_url,
                        briefing_path=briefing_path
                    )
                    
                    if not analysis_results:
                        raise ValueError("No se obtuvieron resultados del análisis")
                    
                    if "error" in analysis_results:
                        raise ValueError(analysis_results["error"])
                    
                    if "tier_analysis" not in analysis_results:
                        raise ValueError("Análisis por niveles no disponible en los resultados")

                    # Generar informe PDF
                    clean_name = briefing_file.name.lower().replace('.pdf', '')
                    pdf_name = f"Informe_Analisis_{clean_name}.pdf"

                    if request.POST.get('download_pdf'):
                        pdf_path = generate_pdf_report(
                            analysis_results=analysis_results,
                            briefing_name=briefing_file.name
                        )
                    
                        if pdf_path:
                            if os.path.exists(pdf_path):
                                try:
                                    return FileResponse(
                                        open(pdf_path, 'rb'),
                                        content_type='application/pdf',
                                        as_attachment=True,
                                        filename=os.path.basename(pdf_path)
                                    )
                                except Exception as e:
                                    messages.error(request, f"Error downloading PDF: {str(e)}")
                            else:
                                messages.error(request, "PDF file not found")

                    # Añadir repo clonado a la lista de limpieza
                    cloned_repo_path = os.path.join(root_dir, "cloned_repo")
                    if os.path.exists(cloned_repo_path):
                        temp_files.append(cloned_repo_path)

                    return render(request, "analysis.html", {
                        "project_type": analysis_results["project_type"],
                        "repo_data": analysis_results["repository_stats"],
                        "tier_analysis": analysis_results["tier_analysis"],
                        "analysis_date": analysis_results["analysis_date"],
                        "analysis_available": bool(analysis_results.get("tier_analysis")),
                        "commit_analysis": analysis_results["repository_stats"].get("commit_analysis", []),
                        "pdf_filename": pdf_name  # Add this line for dynamic PDF filename
                    })

                except json.JSONDecodeError as je:
                    logging.error(f"Error al parsear JSON de la API: {str(je)}")
                    messages.error(request, "Error en el procesamiento de la respuesta de la API")
                except ValueError as ve:
                    logging.error(f"Error de validación: {str(ve)}")
                    messages.error(request, str(ve))
                except Exception as e:
                    logging.error(f"Error inesperado: {str(e)}")
                    messages.error(request, "Ha ocurrido un error inesperado durante el análisis")
                finally:
                    # Limpieza de archivos temporales
                    for file_path in temp_files:
                        try:
                            if os.path.isdir(file_path):
                                shutil.rmtree(file_path, ignore_errors=True)
                            elif os.path.isfile(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            logging.error(f"Error al limpiar archivo temporal {file_path}: {str(e)}")
            else:
                messages.error(request, "Por favor, proporciona un archivo briefing")
                
        except Exception as e:
            logging.error(f"Error en el análisis del repositorio: {str(e)}")
            messages.error(request, f"Error al analizar el repositorio: {str(e)}")

    return render(request, "analysis.html", {"analysis_available": False})

def quick_analysis(request):
    if request.method == 'POST':
        repo_url = request.POST.get('repo_url')
        
        if not repo_url:
            messages.error(request, 'Por favor, proporciona una URL válida')
            return render(request, 'quick_analysis.html')
            
        try:
            # Inicialización del analizador de GitHub
            analyzer = GitHubAnalyzer()
            repo = analyzer.github.get_repo(analyzer._extract_repo_name(repo_url))
            
            # Obtención de commits y autores de todas las ramas
            branches = repo.get_branches()
            all_commits = []
            commit_authors = []

            # Análisis de commits por rama
            for branch in branches:
                branch_commits = repo.get_commits(sha=branch.name)
                for commit in branch_commits:
                    if commit.sha not in [c.sha for c in all_commits]:
                        all_commits.append(commit)
                        author = None
                        if commit.author:
                            author = commit.author.login
                        elif commit.commit.author.email:
                            author = commit.commit.author.email
                        else:
                            author = commit.commit.author.name
                        commit_authors.append(author)

            # Verificación de commits encontrados
            if not all_commits:
                messages.warning(request, 'No se encontraron commits en este repositorio')
                return render(request, 'quick_analysis.html')
            
            # Generación de visualizaciones
            commit_data = pd.DataFrame({
                'fecha': [c.commit.author.date.date() for c in all_commits],
                'autor': commit_authors,
                'hora': [c.commit.author.date.hour for c in all_commits],
                'cantidad': 1
            })

            # Gráfica de actividad
            fig_activity = go.Figure()
            colors = px.colors.qualitative.Set1

            for idx, autor in enumerate(commit_data['autor'].unique()):
                df_autor = commit_data[commit_data['autor'] == autor]
                df_daily = df_autor.groupby('fecha')['cantidad'].sum().reset_index()
                
                fig_activity.add_trace(
                    go.Scatter(
                        x=df_daily['fecha'],
                        y=df_daily['cantidad'],
                        name=autor,
                        mode='lines+markers'
                    )
                )

            # Gráfica de distribución de autores
            df_authors = pd.DataFrame(commit_authors, columns=['autor'])
            author_counts = df_authors['autor'].value_counts()
            
            fig_authors = px.pie(
                values=author_counts.values,
                names=author_counts.index,
                title='Distribución de Commits por Desarrollador'
            )

            # Análisis de lenguajes y estadísticas
            repo_stats = analyzer.get_repo_stats(repo_url)
            languages_data = []
            
            if repo_stats and "languages" in repo_stats:
                languages_data = repo_stats['languages']

            context = {
                'graphs': {
                    'commits_activity': fig_activity.to_html(full_html=False),
                    'developer_distribution': fig_authors.to_html(full_html=False)
                },
                'languages': languages_data,
                'libraries': repo_stats.get('libraries', [])
            }

            return render(request, 'quick_analysis.html', context)
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'quick_analysis.html')
    
    return render(request, 'quick_analysis.html')