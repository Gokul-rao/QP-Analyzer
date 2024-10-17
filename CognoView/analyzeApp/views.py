from datetime import datetime
import json
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone  
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .shared.question_extractor import QuestionExtractor

from .models import Department, QuestionBank, Report, Subject, Semester, ExamType

import os


@login_required(login_url='login')
def home(request):
    return render(request, "qpanalyze/home.html")

def analyze(request):
    return render(request, "qpanalyze/analyze.html")

def abt(request):
    departments = Department.objects.all()
    semesters = list(Semester.choices)
    exam_type = list(ExamType.choices)

    subjects = []
    subject_count = 0

    # Check if the department code is present in the GET parameters
    if 'department_code' in request.GET:
        department_code = request.GET['department_code']
        sem = request.GET['semester']
        subjects = get_subject_by_department(department_code, sem)
        subject_count = len(subjects)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(subjects, safe=False)
    
    if request.method == 'POST':
        subject_count = int(request.POST.get('subject_count', 0))
        department_code = request.POST.get('department', '')
        semester = request.POST.get('semester', '')
        exam_type = request.POST.get('exam_type', '')
        subject_code = request.POST.get('subject')
        question_text = request.POST.get('question', '')

        # Get department and semester objects
        department = Department.objects.get(department_code=department_code)
        batch_identifier = str(uuid.uuid4())
        
        subject = Subject.objects.get(subject_code=subject_code)

        qp_path = os.path.dirname('media/')
        question_extractor = QuestionExtractor(qp_path)

        # Split the input into a list of questions
        questions_list = [question.strip() for question in question_text.splitlines() if question.strip()]
        
        for question in questions_list:
            cognitive_level = question_extractor.predict_cognitive_level(question)
            
            QuestionBank.objects.create(
                department_code=department,
                semester=semester,
                subject_code=subject,
                question=question,
                cognitive_level=cognitive_level.upper(),
                exam_type=exam_type,
                is_verified=True,
                batch_id=batch_identifier
            )
        return redirect('fetch_questions', batch_identifier=batch_identifier)

    context = {
        'departments': departments,
        'subjects': subjects,
        'subjects_count': subject_count,
        'semesters': semesters,
        'exam_type': exam_type
    }

    return render(request, "qpanalyze/abt.html", context=context)


def abf(request):

    departments = Department.objects.all()
    semesters = list(Semester.choices)
    exam_type = list(ExamType.choices)

    subjects = []
    subject_count = 0

    # Check if the department code is present in the GET parameters
    if 'department_code' in request.GET:
        department_code = request.GET['department_code']
        sem = request.GET['semester']
        subjects = get_subject_by_department(department_code, sem)
        subject_count = len(subjects)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(subjects, safe=False)

    context = {
        'departments': departments,
        'subjects': subjects,
        'subjects_count': subject_count,
        'semesters': semesters,
        'exam_type': exam_type
    }

    return render(request, "qpanalyze/abf.html", context=context)


def get_subject_by_department(department_no, semester):
    subjects = Subject.objects.filter(department__department_code=department_no, semester=semester)
    subject_list = [subject for subject in subjects.values('subject_code', 'subject_name')]

    return subject_list


def get_added_questions(request):
    if request.method == 'POST':
        subject_count = int(request.POST.get('subject_count', 0))
        department_code = request.POST.get('department', '')
        semester = request.POST.get('semester', '')
        exam_type = request.POST.get('exam_type', '')

        # Get department and semester objects
        department = Department.objects.get(department_code=department_code)
        batch_identifier = str(uuid.uuid4())

        for i in range(1, subject_count + 1):
            subject_code = request.POST.get(f'subject_{i}')
            file_obj = request.FILES.get(f'file_{i}')

            if subject_code and file_obj:
                file_path = handle_uploaded_file(file_obj, subject_code)

                # Get the Subject object
                subject = Subject.objects.get(subject_code=subject_code)
                
                qp_path = os.path.dirname(file_path)
                question_extractor = QuestionExtractor(qp_path)

                question_text = question_extractor.extract_text_from_pdf(file_obj.name)
                if question_text:
                    questions = question_extractor.get_only_questions(question_text)
                    
                    for question in questions:
                        cognitive_level = question_extractor.predict_cognitive_level(question)
                        
                        QuestionBank.objects.create(
                            department_code=department,
                            semester=semester,
                            subject_code=subject,
                            question=question,
                            cognitive_level=cognitive_level.upper(),
                            exam_type=exam_type,
                            is_verified=True,
                            batch_id=batch_identifier
                        )
        return redirect('fetch_questions', batch_identifier=batch_identifier)

    return HttpResponse("Invalid request method", status=405)


def fetch_questions(request, batch_identifier):
    questions = QuestionBank.objects.filter(batch_id=batch_identifier)

    context = {
        'questions': questions,
        'batch_id': batch_identifier
    }

    return render(request, "qpanalyze/display_questions.html", context=context)


def handle_uploaded_file(file, subject_code):
    upload_dir = f'media/uploads/{subject_code}'
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return file_path


def generate_report(request, batch_id):
    if request.method == 'POST':
        questions = QuestionBank.objects.filter(batch_id=batch_id).select_related('subject_code')

        # Prepare data for report generation
        report_data = {}
        
        for question in questions:
            subject_code = question.subject_code
            cognitive_level = question.cognitive_level
            
            if subject_code not in report_data:
                report_data[subject_code] = {
                    'total_questions': 0,
                    'remember': 0,
                    'understand': 0,
                    'apply': 0,
                    'analyze': 0,
                    'evaluate': 0,
                    'create': 0,
                }
            
            report_data[subject_code]['total_questions'] += 1
            report_data[subject_code][cognitive_level.lower()] += 1  # Increment the count based on cognitive level

        # Create reports
        for subject_code, levels in report_data.items():
            print(levels)
            remember_percent = (levels['remember'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0
            understand_percent = (levels['understand'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0
            apply_percent = (levels['apply'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0
            analyze_percent = (levels['analyze'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0
            evaluate_percent = (levels['evaluate'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0
            create_percent = (levels['create'] / levels['total_questions'] * 100) if levels['total_questions'] > 0 else 0.0

            report = Report(
                batch_id=batch_id,
                subject_code=subject_code,
                remember=remember_percent,
                understand=understand_percent,
                apply=apply_percent,
                analyze=analyze_percent,
                evaluate=evaluate_percent,
                create=create_percent
            )
            report.save()  # Save the report to the database

        # Redirect to the report detail page or render a success template
        return redirect('report_detail', batch_id=batch_id) 


def report_detail(request, batch_id):
    # Fetch the report based on the report_id
    reports = Report.objects.filter(batch_id=batch_id)
    
    totals = {
        'remember': 0,
        'understand': 0,
        'apply': 0,
        'analyze': 0,
        'evaluate': 0,
        'create': 0,
        'total_percentage': 0
    }
    
    report_count = reports.count()

    for report in reports:
        totals['remember'] += report.remember
        totals['understand'] += report.understand
        totals['apply'] += report.apply
        totals['analyze'] += report.analyze
        totals['evaluate'] += report.evaluate
        totals['create'] += report.create
        totals['total_percentage'] += report.total_percentage
    
    averages = {
        key: (float(value) / report_count) if report_count > 0 else 0 for key, value in totals.items()
    }

    # Chart
    labels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    datasets = [
        {
            'label': "Average Cogntive Levels",
            'data': [
                float(averages['remember']),
                float(averages['understand']),
                float(averages['apply']),    
                float(averages['analyze']),  
                float(averages['evaluate']), 
                float(averages['create'])
            ],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.2)',  # Remember
                'rgba(54, 162, 235, 0.2)',  # Understand
                'rgba(255, 206, 86, 0.2)',   # Apply
                'rgba(75, 192, 192, 0.2)',   # Analyze
                'rgba(153, 102, 255, 0.2)',  # Evaluate
                'rgba(255, 159, 64, 0.2)',    # Create
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
            ],
            'borderWidth': 1
        }
    ]

    chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    context = {
        'chart_data': json.dumps(chart_data),
        'reports': reports,
        'batch_id': batch_id,
        'totals': totals,
        'averages': averages
    }

    if 'download_pdf' in request.GET:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{batch_id}.pdf"'

        # Create a SimpleDocTemplate for the PDF document
        pdf_buffer = SimpleDocTemplate(response, pagesize=A4)

        # List to hold the elements of the PDF
        elements = []

        # Add a Title to the PDF
        styles = getSampleStyleSheet()
        title = Paragraph(f"Cognitive Levels Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch)) 

        # Add a general introduction paragraph
        intro_text = Paragraph(
            f"This report provides an analysis of cognitive levels for this batch {batch_id}. \nBelow is the breakdown for each subject.",
            styles['BodyText']
        )
        elements.append(intro_text)
        elements.append(Spacer(1, 0.2 * inch))

        # Add a table with cognitive levels data
        table_data = [['Subject Code', 'R (%)', 'U (%)', 'AY (%)', 'AZ (%)', 'E (%)', 'C (%)', 'Total (%)']]

        for report in reports:
            table_data.append([
                report.subject_code,
                f"{float(report.remember):.2f}",
                f"{float(report.understand):.2f}",
                f"{float(report.apply):.2f}",
                f"{float(report.analyze):.2f}",
                f"{float(report.evaluate):.2f}",
                f"{float(report.create):.2f}",
                f"{float(report.total_percentage):.2f}"
            ])

            table_data.append([
                f"Total",
                f"{float(totals['remember']):.2f}",
                f"{float(totals['understand']):.2f}",
                f"{float(totals['apply']):.2f}",
                f"{float(totals['analyze']):.2f}",
                f"{float(totals['evaluate']):.2f}",
                f"{float(totals['create']):.2f}",
                f"{float(totals['total_percentage']):.2f}"
            ])

            table_data.append([
                f"Average",
                f"{float(averages['remember']):.2f}",
                f"{float(averages['understand']):.2f}",
                f"{float(averages['apply']):.2f}",    
                f"{float(averages['analyze']):.2f}",  
                f"{float(averages['evaluate']):.2f}", 
                f"{float(averages['create']):.2f}",
                f"{float(averages['total_percentage']):.2f}"
            ])

        # Create a Table and style it
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

         # Add the table to the PDF elements
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))

        # Add a summary paragraph
        summary_text = Paragraph(f"The cognitive level distribution across all subjects is as follows.", styles['BodyText'])
        elements.append(summary_text)
        elements.append(Spacer(1, 0.2 * inch))

        add_bar_chart_to_report(elements, averages)

        # Finalize and build the PDF
        pdf_buffer.build(elements)

        return response

    return render(request, "qpanalyze/report_detail.html", context=context)


def add_bar_chart_to_report(elements, report_data):
    drawing = Drawing(400, 200)  # Create a drawing canvas
    
    # Create the bar chart
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 50
    bar_chart.height = 150
    bar_chart.width = 300

    # Set data and labels for the bar chart
    bar_chart.data = [  # List of values for each category
        [
            report_data['remember'], 
            report_data['understand'], 
            report_data['apply'], 
            report_data['analyze'], 
            report_data['evaluate'], 
            report_data['create']
        ]
    ]
    
    bar_chart.categoryAxis.categoryNames = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    
    # Customize the appearance
    bar_chart.bars[0].fillColor = colors.blue
    bar_chart.bars[1].fillColor = colors.green

    # Add the chart to the drawing
    drawing.add(bar_chart)

    # Add the drawing (chart) to the PDF elements
    elements.append(drawing)
    return elements
