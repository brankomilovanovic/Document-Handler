from plugin_framework.author import Author
from plugin_framework.dependency import Dependency


class PluginSpecification:
    def __init__(self, _id, name, authors, version, core_version, category, licence, description, web_page, dependencies=[]):
        self.id = _id
        self.name = name
        self.authors = authors
        self.version = version
        self.core_version = core_version
        self.category = category
        self.licence = licence
        self.description = description
        self.web_page = web_page
        self.dependencies = dependencies

    @staticmethod
    def from_dict(specification_dict):
        # check for required data
        required = ["id", "name", "authors", "version", "core_version",
                    "category", "licence", "description", "web_page"]
        fulfilled = True
        for key in required:
            if key not in specification_dict:
                fulfilled = False
                break
        if not fulfilled:
            raise ValueError("Missing required data for plugin specification!")

        # get required data
        _id = specification_dict["id"]
        name = specification_dict["name"]
        authors = specification_dict["authors"]  # lista recnika
        required_author = ["first_name", "last_name", "email", "web_page"]
        authors_2 = []
        fulfilled_author = True
        for author in authors:  # author : dict
            for key in required_author:
                if key not in author:
                    fulfilled_author = False
                    break
            if not fulfilled_author:
                raise ValueError(
                    "Missing required data for author specification!")
            first_name = author["first_name"]
            last_name = author["last_name"]
            email = author["email"]
            web_page = author["web_page"]
            authors_2.append(Author(first_name, last_name, email, web_page))

        version = specification_dict["version"]
        core_version = specification_dict["core_version"]
        category = specification_dict["category"]
        licence = specification_dict["licence"]
        description = specification_dict["description"]
        web_page = specification_dict["web_page"]

        # get optional data
        # FIXME: kreirati dependency # lista recnika
        dependencies = specification_dict.get("dependencies", [])
        dependencies_2 = []
        required_dependency = ["id", "version"]
        fulfilled_dependency = True
        for dependency in dependencies:
            for key in required_dependency:
                if key not in dependency:
                    fulfilled_dependency = False
                    break
            if not fulfilled_dependency:
                raise ValueError(
                    "Missing required data for dependency specification!")
            id_dependency = dependency["id"]
            version_dependency = dependency["version"]
            dependencies_2.append(Dependency(
                id_dependency, version_dependency))

        return PluginSpecification(_id, name, authors_2, version, core_version, category, licence, description, web_page, dependencies_2)
