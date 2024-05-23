from django.db import models
from curriculum.models import Course
from kerberos_profiles.models import Profile


class CourseAttendanceKey(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    privateKey = models.TextField()
    publicKey = models.TextField()
    

# Create your models here.
class Attendance(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=None)
    time = models.TimeField(default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'course', 'date'], name='unique_attendance'),
        ]
    
    def __str__(self):
        return str(self.student_course.courseSlot.course.courseName) + ' | ' + str(self.date) + ' | ' + str(self.time)
    