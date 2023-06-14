"""This module contains shared fixtures, steps, and hooks.
"""
import pytest
from main.core.api.http_methods_enum import HttpMethods
from main.pivotal_tracker.utils.pivotal_tracker_constants \
    import PayloadsRoute
from main.pivotal_tracker.utils.api_utils import ApiUtils
from main.core.utils.string_utils import StringUtils
from main.core.utils.json_reader import JsonReader
from main.core.api.request_manager import RequestManager

config_file = JsonReader.get_json('./configuration.json')
env_selected = config_file.get("environment", "develop")


def pytest_bdd_before_scenario(request, scenario):
    """ pytest bdd before scenario

    Parameters
    ----------
        request (object): request object of fixture
        feature (object): feature object of pytest bdd
        scenario (object): scenario object of pytest bdd
    """
    request.context = {
        "members_endpoint": False
    }
    request.tags = []
    request.body = {}
    request.response = {}
    scenario_tags = ApiUtils.sort_tags_by_features(request, scenario)

    for tag in scenario_tags:
        if "fixture_create" in tag:
            module_name = tag.split('_')[-1].rstrip('0123456789')

            payload = JsonReader.get_json(
                f".{PayloadsRoute.ROUTE.value}"
                f"payload_{module_name}_creation.json")
            payload = ApiUtils.\
                replace_empty_payload_values(payload,
                                             request, tag.split('_')[-1])
            payload = StringUtils.change_name(payload, tag.split('_')[-1])
            if module_name == "workspace":
                path_endpoint = f"/my/{module_name}s"
            elif module_name == "epic":
                project_id = request.context["project"]["id"]
                path_endpoint = f"/projects/{project_id}/{module_name}s"
            elif module_name == "label":
                project_id = request.context["project"]["id"]
                path_endpoint = f"/projects/{project_id}/{module_name}s"
            elif module_name == "story":
                project_id = request.context["project"]["id"]
                path_endpoint = f"/projects/{project_id}/stories"
            else:
                path_endpoint = f"/{module_name}s"
            response, _ = RequestManager.get_instance().send_request(
                HttpMethods.POST.value,
                path_endpoint,
                payload
            )
            request.context[f"{tag.split('_')[-1]}"] = response
        elif "fake_create" in tag:
            module_name = tag.split('_')[-1].rstrip('0123456789')
            payload = JsonReader.get_json(
                f".{PayloadsRoute.ROUTE.value}"
                f"payload_{module_name}_creation_fake.json")
            request.context[f"{tag.split('_')[-1]}"] = payload


def pytest_bdd_step_error(scenario, exception):
    """ pytest bdd step error

    Args:
        multiple args related with pytest bdd
    """
    print(f"On {scenario}, exception: ", exception)


def pytest_bdd_after_scenario(request):
    """ pytest bdd after scenario

    Args:
        request (object): request object of fixture
        feature (object): feature object of pytest bdd
        scenario (object): scenario object of pytest bdd
    """
    scenario_tags = request.tags
    scenario_report = request.node.__scenario_report__.serialize()
    status = any(bool(scenario_report['steps'][step]['failed'])
                 for step in range(len(scenario_report['steps'])))
    status = 'FAILED' if status else 'SUCCESS'

    for tag in scenario_tags:
        if "fixture_delete" in tag:
            module_name = tag.split('_')[-1].rstrip('0123456789')
            element_id = request.context[f"{module_name}"]["id"]
            if module_name == "workspace":
                path_endpoint = f"/my/{module_name}s/{element_id}"
            else:
                path_endpoint = f"/{module_name}s/{element_id}"

            RequestManager.get_instance().send_request(
                HttpMethods.DELETE.value,
                path_endpoint)


@pytest.fixture()
def datatable():
    """fixture to support implementation of datatables

    Returns:
        DataTable
    """
    return DataTable()


class DataTable:
    """Datatable Class to manage table elements
    """
    def __init__(self):
        pass

    def __str__(self):
        dt_str = ''
        for field, value in self.__dict__.items():
            dt_str = f'{dt_str}\n{field} = {value}'
        return dt_str

    def __repr__(self) -> str:
        """
        __repr__
        :return:
        """
        return self.__str__()
