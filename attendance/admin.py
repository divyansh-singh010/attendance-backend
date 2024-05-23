from django.contrib import admin
from attendance.models import (
    Attendance,
    CourseAttendanceKey
)

# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'time')
    search_fields = ('student', 'course', 'date')
    list_filter = ('student', 'course', 'date')
    
class CourseAttendanceKeyAdmin(admin.ModelAdmin):
    list_display = ('course', 'timestamp', 'privateKey', 'publicKey')
    search_fields = ('course', 'privateKey', 'publicKey')
    
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(CourseAttendanceKey, CourseAttendanceKeyAdmin)