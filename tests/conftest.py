import pytest
import warnings


def pytest_collection_modifyitems(items):
    for item in items:
        test_type = item.originalname.split("_")[-1]
        if test_type == "unittest":
            item.add_marker(pytest.mark.unittest)
        elif test_type == "integration":
            item.add_marker(pytest.mark.integration)
        else:
            warnings.warn(
                UserWarning(
                    f"Naming Convention: '{item.nodeid}' must end with "
                    "'_unittest' or '_integration' for marker assignment."
                )
            )
