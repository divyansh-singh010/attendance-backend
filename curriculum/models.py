from django.db import models
from kerberos_profiles.models import Profile

# Create your models here.
  
class Semester(models.Model):
    academicYear = models.CharField(max_length=10)
    semesterNumber = models.IntegerField(default=0)
    startDate = models.DateField(default=None)
    endDate = models.DateField(default=None)

class Course(models.Model):
    courseCode = models.CharField(max_length=10, primary_key=True)
    courseName = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    courseInstructor = models.ForeignKey(Profile, on_delete=models.CASCADE)
    numberOfClasses = models.IntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['courseCode', 'semester'], name='unique_course'),
        ]
    

    def __str__(self):
        return self.courseCode + ' | ' + self.courseName
    
class CourseClassDates(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classDate = models.DateField(default=None)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'classDate'], name='unique_class_date'),
        ]
    
    def __str__(self):
        return str(self.course) + ' | ' + str(self.classDate) + ' | ' + str(self.classTime)