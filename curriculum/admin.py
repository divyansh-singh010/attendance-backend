from django.contrib import admin
from curriculum.models import (
    Course,
    Semester,
    CourseClassDates
)


# Register your models here.
    
class CourseAdmin(admin.ModelAdmin):
    list_display = ('courseCode', 'courseName', 'semester', 'courseInstructor')
    search_fields = ('courseCode', 'courseName', 'semester', 'courseInstructor')
    list_filter = ('semester', 'courseInstructor')
    
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('academicYear', 'semesterNumber', 'startDate', 'endDate')
    search_fields = ('academicYear', 'semesterNumber', 'startDate', 'endDate')
    list_filter = ('academicYear', 'semesterNumber')
    
class CourseClassDatesAdmin(admin.ModelAdmin):
    list_display = ('course', 'classDate')
    search_fields = ('course', 'classDate')
    list_filter = ('course', 'classDate')
    

admin.site.register(Course, CourseAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(CourseClassDates, CourseClassDatesAdmin)