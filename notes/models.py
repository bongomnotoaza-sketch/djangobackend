from django.conf import settings
from django.db import models


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    userid = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    course_name = models.CharField(max_length=255)
    imageurl = models.URLField(max_length=2048)

    def __str__(self):
        return self.course_name

class Module(models.Model):
    id = models.BigAutoField(primary_key=True)
    parentid = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )
    module_name = models.CharField(max_length=255)
    imageurl = models.URLField(max_length=2048)

    def __str__(self):
        return self.module_name

class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    moduleid = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    lesson_index = models.PositiveIntegerField()
    lesson_name = models.CharField(max_length=255)
    lesson_time = models.PositiveIntegerField()

    def __str__(self):
        return self.lesson_name

class LessonBody(models.Model):
    id = models.BigAutoField(primary_key=True)
    lessonid = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="body",
    )
    type = models.CharField(max_length=50)
    content = models.TextField()
    index = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.lessonid.lesson_name} - {self.type} - {self.index}"

class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    lessonid = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    task_name = models.CharField(max_length=255)

    def __str__(self):
        return self.task_namexite

class TaskQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    taskid = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    index = models.PositiveIntegerField()
    content = models.TextField()

    def __str__(self):
        return f"{self.taskid.task_name} - Question {self.index}"

class TaskAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    taskquestionid = models.ForeignKey(
        TaskQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    index = models.PositiveIntegerField()
    answer_content = models.TextField()

    def __str__(self):
        return f"{self.taskquestionid} - Answer {self.index}"

class UploadAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    questionid = models.ForeignKey(
        TaskQuestion,
        on_delete=models.CASCADE,
        related_name="upload_answers",
    )
    type = models.CharField(max_length=20, default="upload")

    def __str__(self):
        return f"{self.questionid} - Upload Answer"

class TaskCodeAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    questionid = models.ForeignKey(
        TaskQuestion,
        on_delete=models.CASCADE,
        related_name="code_answers",
    )
    type = models.CharField(max_length=20, default="code")

    def __str__(self):
        return f"{self.questionid} - Code Answer"

class Assignment(models.Model):
    id = models.BigAutoField(primary_key=True)
    moduleid = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    assignment_name = models.CharField(max_length=255)

    def __str__(self):
        return self.assignment_name

class AssignmentQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignmentid = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    index = models.PositiveIntegerField()
    content = models.TextField()

    def __str__(self):
        return f"{self.assignmentid.assignment_name} - Question {self.index}"

class AssignmentAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignmentquestionid = models.ForeignKey(
        AssignmentQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    index = models.PositiveIntegerField()
    answer_content = models.TextField()

    def __str__(self):
        return f"{self.assignmentquestionid} - Answer {self.index}"


class AssignmentUploadAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignmentquestionid = models.ForeignKey(
        AssignmentQuestion,
        on_delete=models.CASCADE,
        related_name="upload_answers",
    )
    type = models.CharField(max_length=20, default="upload")

    def __str__(self):
        return f"{self.assignmentquestionid} - Upload Answer"


class AssignmentCodeAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignmentquestionid = models.ForeignKey(
        AssignmentQuestion,
        on_delete=models.CASCADE,
        related_name="code_answers",
    )
    type = models.CharField(max_length=20, default="code")

    def __str__(self):
        return f"{self.assignmentquestionid} - Code Answer"


