from django.contrib import admin

from .models import Subject, QuestionBank, Report, Department


class ReportAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create', 'total_percentage')
    readonly_fields = ('created_at', 'total_percentage')
    list_filter = ('created_at', 'subject_code')

admin.site.register(Report, ReportAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('semester', 'subject_code', 'subject_name', 'department')
    list_filter = ('subject_code', 'semester', 'department')

admin.site.register(Subject, SubjectAdmin)

class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'question', 'cognitive_level', 'exam_type', 'batch_id')
    list_filer = ('department_code', 'subject_code', 'semester')

admin.site.register(QuestionBank, QuestionBankAdmin)

admin.site.register(Department)