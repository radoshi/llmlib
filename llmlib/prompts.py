import string
from pathlib import Path
from typing import Union

from pydantic import BaseModel


class Template(BaseModel):
    content: str
    name: str = ""
    role: str = "user"

    def message(self, inputs: dict = {}) -> dict[str, str]:
        """Return a dictionary that is ready to fed into OpenAI ChatCompletion."""
        content = self.content.format(**inputs)
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


class TemplateLibrary(BaseModel):
    _templates: dict[str, Template] = {}

    def __getitem__(self, name: str) -> Template:
        return self._templates[name]

    def __setitem__(self, name: str, template: Template) -> None:
        self._templates[name] = template

    def __delitem__(self, name: str) -> None:
        del self._templates[name]

    @classmethod
    def from_file_or_dir(cls, filename_or_dir: Union[str, Path]) -> "TemplateLibrary":
        """Load templates from a file or directory."""
        path = Path(filename_or_dir)
        library = cls()
        if path.is_dir():
            for filename in path.glob("*.json"):
                template = Template.parse_file(filename)
                library[template.name] = template
            else:
                return library
        else:
            template = Template.parse_file(path)
            library[template.name] = template
        return library
        return library
