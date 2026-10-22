from django.urls import path

from .views import (
    
    CreateCourseView,
    CourseView,
    
    CreateModuleView,
    ModuleView,
    
    CreateLessonView,
    LessonView,
    CreateLessonBodyView,
    LessonBodyView,

    CreateTaskView,
    TaskView,
    
    CreateTaskQuestionView,
    TaskQuestionView,
    
    CreateTaskAnswerView,
    TaskAnswerView,

    CreateUploadAnswerView,
    UploadAnswerView,

    CreateTaskCodeAnswerView,
    TaskCodeAnswerView,
    CreateAssignmentView,
    AssignmentView,
    
    CreateAssignmentQuestionView,
    AssignmentQuestionView,
    
    CreateAssignmentAnswerView,
    AssignmentAnswerView,
   
    CreateAssignmentUploadAnswerView,
    AssignmentUploadAnswerView,
    
    CreateAssignmentCodeAnswerView,
    AssignmentCodeAnswerView,
)

urlpatterns = [
    # Course endpoints
    path('courses/create/', CreateCourseView.as_view(), name='create-course'),
    path('courses/', CourseView.as_view(), name='courses'),

    # Module endpoints
    path('modules/create/', CreateModuleView.as_view(), name='create-module'),
    path('modules/', ModuleView.as_view(), name='modules'),

    # Lesson endpoints
    path('lessons/create/', CreateLessonView.as_view(), name='create-lesson'),
    path('lessons/', LessonView.as_view(), name='lessons'),
    path('lesson-bodies/create/', CreateLessonBodyView.as_view(), name='create-lesson-body'),
    path(
    "lesson-body/",
    LessonBodyView.as_view(),
    name="lesson-body",
    ),

    # Task endpoints
    path('tasks/create/', CreateTaskView.as_view(), name='create-task'),
    path('tasks/', TaskView.as_view(), name='tasks'),

    # TaskQuestion endpoints
    path('task-questions/create/', CreateTaskQuestionView.as_view(), name='create-task-question'),
    path('task-questions/', TaskQuestionView.as_view(), name='task-questions'),

    # TaskAnswer endpoints
    path('task-answers/create/', CreateTaskAnswerView.as_view(), name='create-task-answer'),
    path('task-answers/', TaskAnswerView.as_view(), name='task-answers'),

    # UploadAnswer endpoints
    path('upload-answers/create/', CreateUploadAnswerView.as_view(), name='create-upload-answer'),
    path('upload-answers/', UploadAnswerView.as_view(), name='upload-answers'),

    # TaskCodeAnswer endpoints
    path('task-code-answers/create/', CreateTaskCodeAnswerView.as_view(), name='create-task-code-answer'),
    path('task-code-answers/', TaskCodeAnswerView.as_view(), name='task-code-answers'),

    # Assignment endpoints
    path('assignments/create/', CreateAssignmentView.as_view(), name='create-assignment'),
    path('assignments/', AssignmentView.as_view(), name='assignments'),

    # AssignmentQuestion endpoints
    path('assignment-questions/create/', CreateAssignmentQuestionView.as_view(), name='create-assignment-question'),
    path('assignment-questions/', AssignmentQuestionView.as_view(), name='assignment-questions'),

    # AssignmentAnswer endpoints
    path('assignment-answers/create/', CreateAssignmentAnswerView.as_view(), name='create-assignment-answer'),
    path('assignment-answers/', AssignmentAnswerView.as_view(), name='assignment-answers'),

    # AssignmentUploadAnswer endpoints
    path('assignment-upload-answers/create/', CreateAssignmentUploadAnswerView.as_view(), name='create-assignment-upload-answer'),
    path('assignment-upload-answers/', AssignmentUploadAnswerView.as_view(), name='assignment-upload-answers'),

    # AssignmentCodeAnswer endpoints
    path('assignment-code-answers/create/', CreateAssignmentCodeAnswerView.as_view(), name='create-assignment-code-answer'),
    path('assignment-code-answers/', AssignmentCodeAnswerView.as_view(), name='assignment-code-answers'),
]