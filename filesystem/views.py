from django.shortcuts import render
import json

from authentication.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .main_service import MainService
from authorization.authorization_service import AuthorizationService
from .default_directory_service import DefaultDirectoryService
from .directory_builder_service import DirectoryBuilderService

main_service = MainService()

@csrf_exempt
@require_POST
def build_directory_structure(request):
    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    service = DirectoryBuilderService()
    structure = service.build_directory_structure(username=username)

    return JsonResponse({
        "username": username,
        "structure": structure
    })

@csrf_exempt
@require_POST
def create_default_directories(request):
    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=404
        )

    service = DefaultDirectoryService(user)
    results = service.create_default_directories()

    return JsonResponse({
        "username": username,
        "results": results
    })

@csrf_exempt
def create_folder(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)
        
        name = data.get("name")
        if not name:
            return JsonResponse(
                {"error": "name is required"},
                status=400
            )
            
        path = data.get("path", "")

        result = main_service.create_folder(
            username,
            name,
            path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to create folder"},
            status=500
        )

@csrf_exempt
def rename_folder(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_name = data.get("newName")
        if not new_name:
            return JsonResponse(
                {"error": "newName is required"},
                status=400
            )

        result = main_service.rename_folder(
            username,
            path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to rename folder"},
            status=500
        )

@csrf_exempt
def delete_folder(request):
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        result = main_service.delete_folder(
            username,
            path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to delete folder"},
            status=500
        )

@csrf_exempt
def move_folder(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_path = data.get("newPath")
        if not new_path:
            return JsonResponse(
                {"error": "newPath is required"},
                status=400
            )

        new_name = data.get("newName", "")

        result = main_service.move_folder(
            username,
            path,
            new_path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to move folder"},
            status=500
        )

@csrf_exempt
def copy_folder(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_path = data.get("newPath")
        if not new_path:
            return JsonResponse(
                {"error": "newPath is required"},
                status=400
            )

        new_name = data.get("newName", "")

        result = main_service.copy_folder(
            username,
            path,
            new_path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to copy folder"},
            status=500
        )

@csrf_exempt
def create_file(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        name = data.get("name")
        if not name:
            return JsonResponse(
                {"error": "name is required"},
                status=400
            )

        path = data.get("path", "")

        result = main_service.create_file(
            username,
            name,
            path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to create file"},
            status=500
        )

@csrf_exempt
def rename_file(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_name = data.get("newName")
        if not new_name:
            return JsonResponse(
                {"error": "newName is required"},
                status=400
            )

        result = main_service.rename_file(
            username,
            path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to rename file"},
            status=500
        )

@csrf_exempt
def delete_file(request):
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        result = main_service.delete_file(
            username,
            path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to delete file"},
            status=500
        )

@csrf_exempt
def save_file(request):
    if request.method != "PUT":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        content = data.get("content", "")

        result = main_service.save_file(
            username,
            path,
            content
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to save file"},
            status=500
        )

@csrf_exempt
def save_as(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_path = data.get("newPath")
        if not new_path:
            return JsonResponse(
                {"error": "newPath is required"},
                status=400
            )

        new_name = data.get("newName", "")

        result = main_service.save_as(
            username,
            path,
            new_path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to save file as"},
            status=500
        )

@csrf_exempt
def move_file(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_path = data.get("newPath")
        if not new_path:
            return JsonResponse(
                {"error": "newPath is required"},
                status=400
            )

        result = main_service.move_file(
            username,
            path,
            new_path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to move file"},
            status=500
        )

@csrf_exempt
def copy_file(request):
    if request.method != "PATCH":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        data = json.loads(request.body)

        path = data.get("path")
        if not path:
            return JsonResponse(
                {"error": "path is required"},
                status=400
            )

        new_path = data.get("newPath")
        if not new_path:
            return JsonResponse(
                {"error": "newPath is required"},
                status=400
            )

        new_name = data.get("newName", "")

        result = main_service.copy_file(
            username,
            path,
            new_path,
            new_name
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to copy file"},
            status=500
        )

@csrf_exempt
def read_directory(request):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        name = request.GET.get("name")
        if not name:
            return JsonResponse(
                {"error": "name is required"},
                status=400
            )

        path = request.GET.get("path", "")

        result = main_service.read_directory(
            username,
            name,
            path
        )

        return JsonResponse(
            result,
            safe=False
        )

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to read directory"},
            status=500
        )

@csrf_exempt
def read_file(request):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    result = AuthorizationService.authorize(request)

    if not result["authenticated"]:
        return JsonResponse(
            {"error": "Authentication required"},
            status=401
        )

    user = result["user"]
    username = user.username

    try:
        path = request.GET.get("path")
        if not path:
            return JsonResponse(
                {"error": "File path is required"},
                status=400
            )

        result = main_service.read_file(
            username,
            path
        )

        return JsonResponse(result)

    except Exception as error:
        print(error)
        return JsonResponse(
            {"error": "Failed to read file"},
            status=500
        )