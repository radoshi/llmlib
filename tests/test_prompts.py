import pytest

from llmlib.prompts import Template, TemplateLibrary


# Test function for the `message` method
def test_message():
    template = Template(content="Hello, World!", name="greeting", role="system")
    expected_message = {"content": "Hello, World!", "role": "system"}
    assert template.message() == expected_message


# Test function for the `save` method when a filename is provided
def test_save_with_filename(tmp_path):
    template = Template(content="Hello, World!", name="greeting", role="system")
    filename = tmp_path / "greeting.json"
    template.save(filename)
    assert filename.exists()
    with open(filename) as f:
        assert f.read() == template.json()


# Test function for the `save` method when a filename is not provided but
# the name attribute is set
def test_save_without_filename(tmp_path):
    template = Template(content="Hello, World!", name="greeting", role="system")
    filename = tmp_path / "greeting.json"
    template.save(filename=filename)
    assert filename.exists()
    with open(filename) as f:
        assert f.read() == template.json()


# Test function for the `save` method when neither filename nor name attribute is
# provided
def test_save_without_filename_and_name():
    template = Template(content="Hello, World!", role="system")
    with pytest.raises(ValueError, match="Name must be provided to save the template."):
        template.save()


# Test function for the `save` method when an empty name attribute is provided
def test_save_with_empty_name():
    template = Template(content="Hello, World!", name="", role="system")
    with pytest.raises(ValueError, match="Name must be provided to save the template."):
        template.save()
        template.save()


# Unit test for extract_format_inputs
def test_extract_format_inputs():
    # Test case 1: Format string with two field names
    template = Template(content="{hello} {world}")
    inputs1 = template.inputs()
    assert inputs1 == ["hello", "world"]

    # Test case 2: Format string with no field names
    template = Template(content="Hello, World!")
    inputs2 = template.inputs()
    assert inputs2 == []

    # Test case 4: Format string with repeated field names
    template = Template(content="{greeting}, {name}. My name is also {name}.")
    inputs3 = template.inputs()
    assert inputs3 == ["greeting", "name"]


def test_getitem_setitem():
    library = TemplateLibrary()
    template = Template(content="Hello, World!", name="greeting", role="system")
    library["greeting"] = template  # Calls __setitem__
    assert library["greeting"] == template  # Calls __getitem__


def test_del_item():
    library = TemplateLibrary()
    template = Template(content="Hello, World!", name="greeting", role="system")
    library["greeting"] = template
    del library["greeting"]  # Calls __del_item__
    with pytest.raises(KeyError):
        _ = library["greeting"]


def test_from_file(tmp_path):
    template = Template(content="Hello, World!", name="greeting", role="system")
    filename = tmp_path / "greeting.json"
    template.save(filename)
    library = TemplateLibrary.from_file_or_dir(filename)
    assert library["greeting"] == template


def test_from_directory(tmp_path):
    template1 = Template(content="Hello, World!", name="greeting", role="system")
    template2 = Template(content="Goodbye, World!", name="farewell", role="user")
    filename1 = tmp_path / "greeting.json"
    filename2 = tmp_path / "farewell.json"
    template1.save(filename1)
    template2.save(filename2)
    library = TemplateLibrary.from_file_or_dir(tmp_path)
    assert library["greeting"] == template1
    assert library["farewell"] == template2


def test_from_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        _ = TemplateLibrary.from_file_or_dir("nonexistent.json")


def test_from_nonexistent_directory():
    with pytest.raises(FileNotFoundError):
        _ = TemplateLibrary.from_file_or_dir("nonexistent_dir")
