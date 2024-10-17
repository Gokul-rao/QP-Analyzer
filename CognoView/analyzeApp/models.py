from typing import Iterable
from django.db import models


class Semester(models.IntegerChoices):
    SEMESTER_I = 1, 'Semester I'
    SEMESTER_II = 2, 'Semester II'
    SEMESTER_III = 3, 'Semester III'
    SEMESTER_IV = 4, 'Semester IV'
    SEMESTER_V = 5, 'Semester V'
    SEMESTER_VI = 6, 'Semester VI'


class CognitiveLevels(models.TextChoices):
    REMEMBER = 'REMEMBER', 'Remember'
    UNDERSTAND = 'UNDERSTAND', 'Understand'
    APPLY = 'APPLY', 'Apply'
    ANALYZE = 'ANALYZE', 'Analyze'
    EVALUATE = 'EVALUATE', 'Evaluate'
    CREATE = 'CREATE', 'Create'


class ExamType(models.TextChoices):
    CA = 'CA', 'Continuous Assessment'
    ESE = 'ESE', 'End Semester Examination'


class CourseType(models.TextChoices):
    UG = 'UG', "Undergraduate"
    PG = 'PG', "Postgraduate"
    DIPLOMA = 'DIPLOMA', "Diploma"
    PG_DIPLOMA = 'PGDIPLOMA', "PG Diploma"
    AICTE = 'AICTE', "AICTE"



class Department(models.Model):
    department_code = models.CharField(max_length=100)
    department_name = models.CharField(max_length=100)
    course_type = models.CharField(max_length=100, choices=CourseType.choices)
    
    def __str__(self) -> str:
        return f"{self.department_name} [{self.course_type}]"
    

class Subject(models.Model):
    subject_code = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=100)
    semester = models.IntegerField(choices=Semester.choices)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.subject_code}"
    

class QuestionBank(models.Model):
    batch_id = models.CharField(max_length=100, blank=True, null=True)
    department_code = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.IntegerField(default=None, choices=Semester.choices)
    subject_code = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question = models.TextField()
    cognitive_level = models.CharField(max_length=20, choices=CognitiveLevels.choices)
    exam_type = models.CharField(default=None, max_length=20, choices=ExamType.choices)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.semester} - {self.subject_code} - {self.exam_type}"
    

class Report(models.Model):
    batch_id = models.CharField(max_length=100, blank=True, null=True)
    subject_code = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    remember = models.DecimalField(max_digits=5, decimal_places=2)
    understand = models.DecimalField(max_digits=5, decimal_places=2)
    apply = models.DecimalField(max_digits=5, decimal_places=2)
    analyze = models.DecimalField(max_digits=5, decimal_places=2)
    evaluate = models.DecimalField(max_digits=5, decimal_places=2)
    create = models.DecimalField(max_digits=5, decimal_places=2)
    total_percentage = models.DecimalField(editable=False, max_digits=5, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_percentage = sum([self.remember, self.understand, self.apply, self.analyze, self.evaluate, self.create])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.subject_code} - {self.created_at}"
    