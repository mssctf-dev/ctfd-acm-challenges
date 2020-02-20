import docker


class Judge():
    @staticmethod
    def execute(image_name, container_name, limits):
        client = docker.DockerClient()
        client.services.create(
            image=image_name,
            name=container_name,
            resources=docker.types.Resources(
                mem_limit=Judge.convert_readable_text(limits['mem_limit'])*2,
            ),
        )
        pass

    @staticmethod
    def compile(code):
        Judge.execute()
        pass


    @staticmethod
    def convert_readable_text(text):
        lower_text = text.lower()

        if lower_text.endswith("k"):
            return int(text[:-1]) * 1024

        if lower_text.endswith("m"):
            return int(text[:-1]) * 1024 * 1024

        if lower_text.endswith("g"):
            return int(text[:-1]) * 1024 * 1024 * 1024

        return 0
