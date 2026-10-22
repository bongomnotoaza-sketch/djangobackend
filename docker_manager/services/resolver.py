class ContainerResolverService:

    @staticmethod
    def ubuntu_container(user):
        return f"{user.username}-ubuntu"

    @staticmethod
    def filesystem_container(user):
        return f"{user.username}-files"

    @staticmethod
    def filesystem_volume(user):
        return f"{user.username}-filesystem"

    @staticmethod
    def network():
        return "logictree"