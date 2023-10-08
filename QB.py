import pytest

def validate_version(version):
    try:
        parts = version.split('.')
        for part in parts:
            int(part)
    except ValueError:
        return "Invalid version format: {}".format(version)
        
def compare_versions(version1, version2):
    error_message1 = validate_version(version1)
    error_message2 = validate_version(version2)

    if error_message1:
        return error_message1
    elif error_message2:
        return error_message2

    v1 = list(map(int, version1.split('.')))
    v2 = list(map(int, version2.split('.')))

    if v1 > v2:
        return "Version {} is greater than {}".format(version1, version2)
    elif v1 < v2:
        return "Version {} is less than {}".format(version1, version2)
    else:
        return "Version {} is equal to {}".format(version1, version2)

def test_equal_versions():
    assert compare_versions("1.0", "1.0") == "Version 1.0 is equal to 1.0"
    assert compare_versions("2.3.4", "2.3.4") == "Version 2.3.4 is equal to 2.3.4"

def test_greater_versions():
    assert compare_versions("2.0", "1.0") == "Version 2.0 is greater than 1.0"
    assert compare_versions("2.3.5", "2.3.4") == "Version 2.3.5 is greater than 2.3.4"
    assert compare_versions("2.4", "2.3.4") == "Version 2.4 is greater than 2.3.4"

def test_lesser_versions():
    assert compare_versions("1.0", "2.0") == "Version 1.0 is less than 2.0"
    assert compare_versions("2.3.4", "2.3.5") == "Version 2.3.4 is less than 2.3.5"
    assert compare_versions("2.3.4", "2.4") == "Version 2.3.4 is less than 2.4"

def test_mixed_versions():
    assert compare_versions("1.2.3", "1.2.4") == "Version 1.2.3 is less than 1.2.4"
    assert compare_versions("3.2.1", "2.3.4") == "Version 3.2.1 is greater than 2.3.4"

def test_invalid_versions():
    assert compare_versions("1.2", "1.a") == "Invalid version format: 1.a"
    assert compare_versions("1.2.3", "1..2.3") == "Invalid version format: 1..2.3"