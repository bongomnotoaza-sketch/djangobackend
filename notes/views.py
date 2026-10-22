from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CreateCourseSerializer,
    CreateLessonBodySerializer,
    CourseSerializer,
    CreateModuleSerializer,
    ModuleSerializer,
    CreateLessonSerializer,
    LessonSerializer,
    CreateTaskSerializer,
    TaskSerializer,
    CreateTaskQuestionSerializer,
    TaskQuestionSerializer,
    CreateTaskAnswerSerializer,
    TaskAnswerSerializer,
    CreateUploadAnswerSerializer,
    UploadAnswerSerializer,
    CreateTaskCodeAnswerSerializer,
    TaskCodeAnswerSerializer,
    CreateAssignmentSerializer,
    AssignmentSerializer,
    CreateAssignmentQuestionSerializer,
    AssignmentQuestionSerializer,
    CreateAssignmentAnswerSerializer,
    AssignmentAnswerSerializer,
    CreateAssignmentUploadAnswerSerializer,
    AssignmentUploadAnswerSerializer,
    CreateAssignmentCodeAnswerSerializer,
    AssignmentCodeAnswerSerializer,
    GetLessonBodySerializer,
)
from .models import (
    Course,
    Module,
    Lesson,
    LessonBody,
    Task,
    TaskQuestion,
    TaskAnswer,
    UploadAnswer,
    TaskCodeAnswer,
    Assignment,
    AssignmentQuestion,
    AssignmentAnswer,
    AssignmentUploadAnswer,
    AssignmentCodeAnswer,
)



class CreateCourseView(APIView):

    def post(self, request):
        serializer = CreateCourseSerializer(data=request.data)

        if serializer.is_valid():
            course = serializer.save()

            return Response(
                {
                    "id": course.id,
                    "message": "Course created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class CourseView(APIView):

    def get(self, request):
        courses = Course.objects.select_related("userid").all()

        serializer = CourseSerializer(
            courses,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
class CreateModuleView(APIView):

    def post(self, request):
        serializer = CreateModuleSerializer(data=request.data)

        if serializer.is_valid():
            module = serializer.save()

            return Response(
                {
                    "id": module.id,
                    "message": "Module created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
        
class ModuleView(APIView):

    def get(self, request):
        course_id = request.query_params.get("course_id")

        modules = Module.objects.filter(parentid_id=course_id)

        serializer = ModuleSerializer(
            modules,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
class LessonBodyView(APIView):

    def get(self, request):
        lesson_id = request.query_params.get("lesson_id")

        lesson_body = LessonBody.objects.filter(
            lessonid_id=lesson_id
        ).order_by("index")

        serializer = GetLessonBodySerializer(
            lesson_body,
            many=True
        )

        return Response(serializer.data)
        
class CreateLessonView(APIView):

    def post(self, request):
        serializer = CreateLessonSerializer(data=request.data)

        if serializer.is_valid():
            lesson = serializer.save()

            return Response(
                {
                    "id": lesson.id,
                    "message": "Lesson created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class CreateLessonBodyView(APIView):

    def post(self, request):
        serializer = CreateLessonBodySerializer(data=request.data)

        if serializer.is_valid():
            lesson_body = serializer.save()

            return Response(
                {
                    "id": lesson_body.id,
                    "message": "Lesson body created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class LessonView(APIView):

    def get(self, request):
        module_id = request.query_params.get("module_id")

        lessons = Lesson.objects.filter(moduleid_id=module_id)

        serializer = LessonSerializer(
            lessons,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )     

class CreateTaskView(APIView):

    def post(self, request):
        serializer = CreateTaskSerializer(data=request.data)

        if serializer.is_valid():
            task = serializer.save()

            return Response(
                {
                    "id": task.id,
                    "message": "Task created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskView(APIView):

    def get(self, request):
        lesson_id = request.query_params.get("lesson_id")

        tasks = Task.objects.filter(lessonid_id=lesson_id)

        serializer = TaskSerializer(
            tasks,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
class CreateTaskQuestionView(APIView):
    def post(self, request):
        serializer = CreateTaskQuestionSerializer(data=request.data)

        if serializer.is_valid():
            task_question = serializer.save()

            return Response(
                {
                    "id": task_question.id,
                    "message": "Task question created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskQuestionView(APIView):
    def get(self, request):
        task_id = request.query_params.get("task_id")

        task_questions = TaskQuestion.objects.filter(taskid_id=task_id)

        serializer = TaskQuestionSerializer(
            task_questions,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateTaskAnswerView(APIView):
    def post(self, request):
        serializer = CreateTaskAnswerSerializer(data=request.data)

        if serializer.is_valid():
            task_answer = serializer.save()

            return Response(
                {
                    "id": task_answer.id,
                    "message": "Task answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskAnswerView(APIView):
    def get(self, request):
        task_question_id = request.query_params.get("task_question_id")

        task_answers = TaskAnswer.objects.filter(taskquestionid_id=task_question_id)

        serializer = TaskAnswerSerializer(
            task_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateUploadAnswerView(APIView):
    def post(self, request):
        serializer = CreateUploadAnswerSerializer(data=request.data)

        if serializer.is_valid():
            upload_answer = serializer.save()

            return Response(
                {
                    "id": upload_answer.id,
                    "message": "Upload answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class UploadAnswerView(APIView):
    def get(self, request):
        question_id = request.query_params.get("question_id")

        upload_answers = UploadAnswer.objects.filter(questionid_id=question_id)

        serializer = UploadAnswerSerializer(
            upload_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateTaskCodeAnswerView(APIView):
    def post(self, request):
        serializer = CreateTaskCodeAnswerSerializer(data=request.data)

        if serializer.is_valid():
            task_code_answer = serializer.save()

            return Response(
                {
                    "id": task_code_answer.id,
                    "message": "Task code answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class TaskCodeAnswerView(APIView):
    def get(self, request):
        question_id = request.query_params.get("question_id")

        task_code_answers = TaskCodeAnswer.objects.filter(questionid_id=question_id)

        serializer = TaskCodeAnswerSerializer(
            task_code_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateAssignmentView(APIView):
    def post(self, request):
        serializer = CreateAssignmentSerializer(data=request.data)

        if serializer.is_valid():
            assignment = serializer.save()

            return Response(
                {
                    "id": assignment.id,
                    "message": "Assignment created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssignmentView(APIView):
    def get(self, request):
        module_id = request.query_params.get("module_id")

        assignments = Assignment.objects.filter(moduleid_id=module_id)

        serializer = AssignmentSerializer(
            assignments,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateAssignmentQuestionView(APIView):
    def post(self, request):
        serializer = CreateAssignmentQuestionSerializer(data=request.data)

        if serializer.is_valid():
            assignment_question = serializer.save()

            return Response(
                {
                    "id": assignment_question.id,
                    "message": "Assignment question created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssignmentQuestionView(APIView):
    def get(self, request):
        assignment_id = request.query_params.get("assignment_id")

        assignment_questions = AssignmentQuestion.objects.filter(assignmentid_id=assignment_id)

        serializer = AssignmentQuestionSerializer(
            assignment_questions,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateAssignmentAnswerView(APIView):
    def post(self, request):
        serializer = CreateAssignmentAnswerSerializer(data=request.data)

        if serializer.is_valid():
            assignment_answer = serializer.save()

            return Response(
                {
                    "id": assignment_answer.id,
                    "message": "Assignment answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssignmentAnswerView(APIView):
    def get(self, request):
        assignment_question_id = request.query_params.get("assignment_question_id")

        assignment_answers = AssignmentAnswer.objects.filter(assignmentquestionid_id=assignment_question_id)

        serializer = AssignmentAnswerSerializer(
            assignment_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateAssignmentUploadAnswerView(APIView):
    def post(self, request):
        serializer = CreateAssignmentUploadAnswerSerializer(data=request.data)

        if serializer.is_valid():
            assignment_upload_answer = serializer.save()

            return Response(
                {
                    "id": assignment_upload_answer.id,
                    "message": "Assignment upload answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssignmentUploadAnswerView(APIView):
    def get(self, request):
        assignment_question_id = request.query_params.get("assignment_question_id")

        assignment_upload_answers = AssignmentUploadAnswer.objects.filter(assignmentquestionid_id=assignment_question_id)

        serializer = AssignmentUploadAnswerSerializer(
            assignment_upload_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreateAssignmentCodeAnswerView(APIView):
    def post(self, request):
        serializer = CreateAssignmentCodeAnswerSerializer(data=request.data)

        if serializer.is_valid():
            assignment_code_answer = serializer.save()

            return Response(
                {
                    "id": assignment_code_answer.id,
                    "message": "Assignment code answer created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AssignmentCodeAnswerView(APIView):
    def get(self, request):
        assignment_question_id = request.query_params.get("assignment_question_id")

        assignment_code_answers = AssignmentCodeAnswer.objects.filter(assignmentquestionid_id=assignment_question_id)

        serializer = AssignmentCodeAnswerSerializer(
            assignment_code_answers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )