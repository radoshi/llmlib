import string
from pathlib import Path
from typing import Union

import tomli
from pydantic import BaseModel


class Template(BaseModel):
    content: str
    name: str = ""
    role: str = "user"

    def message(self, **kwargs) -> dict[str, str]:
        """Return a dictionary that is ready to fed into OpenAI ChatCompletion."""
        content = self.content.format(**kwargs)
        return {"content": content, "role": self.role}

    def save(self, filename: Union[str, Path] = "") -> None:
        """Save the template to a file."""
        if not filename and not self.name:
            raise ValueError("Name must be provided to save the template.")
        filename = Path(filename or f"{self.name}.json")
        with open(filename, "w") as f:
            f.write(self.json())

    def inputs(self) -> list[str]:
        """Return a list of field names in the contents."""
        formatter = string.Formatter()
        field_names = []
        for _, field_name, _, _ in formatter.parse(self.content):
            if field_name is not None:
                field_names.append(field_name)
        return sorted(list(set(field_names)))

    @classmethod
    def parse_toml(cls, filename: Union[Path, str]) -> "Template":
        """Parse a TOML file and return a Template object."""
        with open(filename, "rb") as f:
            toml_dict = tomli.load(f)
            return cls.parse_obj(toml_dict)


class TemplateLibrary(BaseModel):
    _templates: dict[str, Template] = {}

    def __getitem__(self, name: str) -> Template:
        return self._templates[name]

    def __setitem__(self, name: str, template: Template) -> None:
        self._templates[name] = template

    def __delitem__(self, name: str) -> None:
        del self._templates[name]

    def add(self, template: Template) -> None:
        """Add a template to the library."""
        if not template.name:
            raise ValueError("Template must have a name.")
        self._templates[template.name] = template

    @classmethod
    def from_file_or_directory(
        cls, filename_or_dir: Union[str, Path]
    ) -> "TemplateLibrary":
        """Load templates from a file or directory."""
        path = Path(filename_or_dir)
        library = cls()
        if path.is_dir():
            for filename in path.glob("*.json"):
                library.add(Template.parse_file(filename))
            for filename in path.glob("*.toml"):
                library.add(Template.parse_toml(filename))
        else:
            if path.suffix == ".toml":
                library.add(Template.parse_toml(path))
            else:
                library.add(Template.parse_file(path))
        return library
