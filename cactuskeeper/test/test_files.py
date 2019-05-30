from cactuskeeper.files import read_config_file

EMPTY_CONFIG = {"tagged-files": [], "ignore_issues": []}


def test_read_empty_config(tmpdir):
    p = tmpdir.join("setup.cfg")
    assert EMPTY_CONFIG == read_config_file(str(tmpdir))

    p.write("[some_other_tool]\na = 12\nb=13\n")

    assert EMPTY_CONFIG == read_config_file(str(tmpdir))


def test_read_config_file(tmpdir):

    content = """
    [cactuskeeper]
    tagged-files =
        version_info.json
        some_other_file.py
    ignore_issues = #1,#134
    """

    p = tmpdir.join("setup.cfg")
    p.write(content)

    config = read_config_file(str(tmpdir))
    assert set(["tagged-files", "ignore_issues"]) == config.keys()

    assert ["version_info.json", "some_other_file.py"] == config["tagged-files"]

    assert ["#1", "#134"] == config["ignore_issues"]
