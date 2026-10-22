from rest_framework import serializers
from .models import Course,Module,Lesson,LessonBody,Task,TaskAnswer,TaskCodeAnswer,TaskQuestion,UploadAnswer,Assignment,AssignmentAnswer,AssignmentCodeAnswer,AssignmentQuestion,AssignmentUploadAnswer
from authentication.services import EncryptionService

class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "userid",
            "course_name",
            "imageurl",
        ]
        
class CourseSerializer(serializers.ModelSerializer):
    educator_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "course_name",
            "imageurl",
            "educator_name",
        ]

    def get_educator_name(self, obj):
        return "Alikho"
    
class CreateModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            "parentid",
            "module_name",
            "imageurl",
        ]
        
        
class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            "id",
            "module_name",
            "imageurl",
        ]
        


class CreateLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["moduleid", "lesson_name", "lesson_time"]

    def create(self, validated_data):
        module = validated_data["moduleid"]
        last = Lesson.objects.filter(moduleid=module).order_by("-lesson_index").first()
        next_index = (last.lesson_index + 1) if last else 1

        return Lesson.objects.create(
            moduleid=module,
            lesson_name=validated_data["lesson_name"],
            lesson_time=validated_data["lesson_time"],
            lesson_index=next_index,
        )

class GetLessonBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBody
        fields = [
            "id",
            "type",
            "content",
            "index",
        ]
       
class CreateLessonBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBody
        fields = [
            "lessonid",
            "type",
            "content",
            "index"
        ]
  
        
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "lesson_index",
            "lesson_name",
        ]
        
class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "lessonid",
            "task_name",
        ]

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "task_name",
        ]
        
class CreateTaskQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskQuestion
        fields = [
            "taskid",
            "index",
            "content",
        ]


class TaskQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskQuestion
        fields = [
            "id",
            "index",
            "content",
        ]


class CreateTaskAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAnswer
        fields = [
            "taskquestionid",
            "index",
            "answer_content",
        ]


class TaskAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAnswer
        fields = [
            "id",
            "index",
            "answer_content",
        ]


class CreateUploadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadAnswer
        fields = [
            "questionid",
        ]


class UploadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadAnswer
        fields = [
            "id",
            "type",
        ]


class CreateTaskCodeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCodeAnswer
        fields = [
            "questionid",
        ]


class TaskCodeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCodeAnswer
        fields = [
            "id",
            "type",
        ]
        
class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "moduleid",
            "assignment_name",
        ]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "id",
            "assignment_name",
        ]


class CreateAssignmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentQuestion
        fields = [
            "assignmentid",
            "index",
            "content",
        ]


class AssignmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentQuestion
        fields = [
            "id",
            "index",
            "content",
        ]


class CreateAssignmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentAnswer
        fields = [
            "assignmentquestionid",
            "index",
            "answer_content",
        ]


class AssignmentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentAnswer
        fields = [
            "id",
            "index",
            "answer_content",
        ]


class CreateAssignmentUploadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentUploadAnswer
        fields = [
            "assignmentquestionid",
        ]


class AssignmentUploadAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentUploadAnswer
        fields = [
            "id",
            "type",
        ]


class CreateAssignmentCodeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentCodeAnswer
        fields = [
            "assignmentquestionid",
        ]


class AssignmentCodeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentCodeAnswer
        fields = [
            "id",
            "type",
        ]