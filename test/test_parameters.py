from obsidian_scripts.parameters import get_parameters


def test_get_parameters():
    params = get_parameters()
    assert params["paths"]["notes"] == "/Users/jyesselman2/Dropbox/notes"
