from django.urls import path

from . import views


urlpatterns = [
    path("folders/create/", views.create_folder),
    path("folders/rename/", views.rename_folder),
    path("folders/delete/", views.delete_folder),
    path("folders/move/", views.move_folder),
    path("folders/copy/", views.copy_folder),

    path("files/create/", views.create_file),
    path("files/rename/", views.rename_file),
    path("files/delete/", views.delete_file),
    path("files/save/", views.save_file),
    path("files/save-as/", views.save_as),
    path("files/move/", views.move_file),
    path("files/copy/", views.copy_file),

    path("folders/", views.read_directory),
    path("files/", views.read_file),
    path(
        "directory-builder/",
        views.build_directory_structure
    ),
    path("default-directories/", views.create_default_directories),
]