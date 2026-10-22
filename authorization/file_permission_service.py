from django.core.exceptions import PermissionDenied

from filesystem.models.file import Files


class FilePermissionsService:

    def can_create(
        self,
        user,
        parent_id,
    ):
        """
        Check whether the user can create a filesystem
        item inside the specified parent directory.
        """

        if not user.is_authenticated:

            raise PermissionDenied(
                "Authentication required."
            )

        # -----------------------------------------
        # Check parent directory ownership
        # -----------------------------------------

        try:

            Files.objects.get(
                id=parent_id,
                user=user,
                type="folder",
            )

        except Files.DoesNotExist:

            raise PermissionDenied(
                "You do not have permission to create "
                "items in this directory."
            )

        return True

    def can_access(
        self,
        user,
        item_id,
    ):
        """
        Check whether the user owns the specified
        filesystem item.
        """

        if not user.is_authenticated:

            raise PermissionDenied(
                "Authentication required."
            )

        # -----------------------------------------
        # Check item ownership
        # -----------------------------------------

        try:

            Files.objects.get(
                id=item_id,
                user=user,
            )

        except Files.DoesNotExist:

            raise PermissionDenied(
                "You do not have permission to access this item."
            )

        return True

    def can_move(
        self,
        user,
        item_id,
        new_parent_id,
    ):
        """
        Check whether the user can move an item into
        another directory.

        Both the item and destination directory must
        belong to the authenticated user.
        """

        if not user.is_authenticated:

            raise PermissionDenied(
                "Authentication required."
            )

        # -----------------------------------------
        # 1. Check item ownership
        # -----------------------------------------

        try:

            Files.objects.get(
                id=item_id,
                user=user,
            )

        except Files.DoesNotExist:

            raise PermissionDenied(
                "You do not have permission to move this item."
            )

        # -----------------------------------------
        # 2. Check destination ownership
        # -----------------------------------------

        try:

            Files.objects.get(
                id=new_parent_id,
                user=user,
                type="folder",
            )

        except Files.DoesNotExist:

            raise PermissionDenied(
                "You do not have permission to move "
                "items into this directory."
            )

        return True

    def can_delete(
        self,
        user,
        item_id,
    ):
        """
        Check whether the user can delete the specified
        filesystem item.
        """

        if not user.is_authenticated:

            raise PermissionDenied(
                "Authentication required."
            )

        # -----------------------------------------
        # Check item ownership
        # -----------------------------------------

        try:

            Files.objects.get(
                id=item_id,
                user=user,
            )

        except Files.DoesNotExist:

            raise PermissionDenied(
                "You do not have permission to delete this item."
            )

        return True