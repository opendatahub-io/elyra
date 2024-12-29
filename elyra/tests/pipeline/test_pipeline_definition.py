#
# Copyright 2018-2025 Elyra Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from unittest import mock

import pytest

from elyra.pipeline.pipeline_constants import ENV_VARIABLES
from elyra.pipeline.pipeline_constants import KUBERNETES_SECRETS
from elyra.pipeline.pipeline_definition import Node
from elyra.pipeline.pipeline_definition import PipelineDefinition
from elyra.pipeline.properties import ElyraProperty
from elyra.pipeline.properties import ElyraPropertyList
from elyra.pipeline.properties import KubernetesSecret
from elyra.tests.pipeline.util import _read_pipeline_resource


@pytest.fixture
def mock_pipeline_property_propagation(monkeypatch):
    # Mock propagate_pipeline_default_properties to skip propagation
    monkeypatch.setattr(PipelineDefinition, "propagate_pipeline_default_properties", lambda x: True)


def test_valid_pipeline():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    assert pipeline_definition.is_valid()


def test_validation_flags_missing_schema_version(mock_pipeline_property_propagation):
    _check_missing_pipeline_field("version", "Pipeline schema version field is missing.")


def test_validation_flags_schema_version_has_wrong_type(mock_pipeline_property_propagation):
    _check_pipeline_field_type("version", 3.0, "Pipeline schema version field should be a string.")


def test_validation_flags_missing_pipelines_field(mock_pipeline_property_propagation):
    _check_missing_pipeline_field("pipelines", "Pipeline is missing 'pipelines' field.")


def test_validation_flags_pipelines_has_wrong_type(mock_pipeline_property_propagation):
    _check_pipeline_field_type("pipelines", "", "Field 'pipelines' should be a list.")


def test_validation_flags_pipelines_is_empty(mock_pipeline_property_propagation):
    _check_pipeline_field_type("pipelines", list(), "Pipeline has zero length 'pipelines' field.")


def test_validation_flags_missing_primary_pipeline_field(mock_pipeline_property_propagation):
    _check_missing_pipeline_field("primary_pipeline", "Could not determine the primary pipeline.")


def test_validation_flags_missing_primary_pipeline_nodes_field(mock_pipeline_property_propagation):
    _check_missing_primary_pipeline_field("nodes", "At least one node must exist in the primary pipeline.")


def test_validation_flags_missing_app_data_field(mock_pipeline_property_propagation):
    _check_missing_primary_pipeline_field("app_data", "Primary pipeline is missing the 'app_data' field.")


def test_validation_flags_missing_version_field():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")
    pipeline_json["pipelines"][0]["app_data"].pop("version")

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    assert pipeline_definition.is_valid() is False
    assert "Primary pipeline is missing the 'version' field." in pipeline_definition.validate()


def test_updates_to_primary_pipeline_updates_pipeline_definition():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)
    pipeline_definition.primary_pipeline.set("version", 3)

    assert pipeline_definition.primary_pipeline.version == 3
    assert pipeline_definition.to_dict()["pipelines"][0]["app_data"]["version"] == 3


def test_updates_to_nodes_updates_pipeline_definition():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)
    for node in pipeline_definition.primary_pipeline.nodes:
        node.set_component_parameter("filename", "foo")

    for node in pipeline_definition.to_dict()["pipelines"][0]["nodes"]:
        assert node["app_data"]["component_parameters"]["filename"] == "foo"


def test_envs_to_dict():
    env_variables = [
        {"env_var": "TEST", "value": " one"},
        {"env_var": "TEST_TWO", "value": "two"},
        {"env_var": "TEST_THREE", "value": ""},
        {"env_var": "TEST_FOUR", "value": "1"},
        {"env_var": "TEST_TWO"},
    ]
    converted_list = ElyraProperty.create_instance("env_vars", env_variables)
    test_dict_correct = {"TEST": "one", "TEST_TWO": "two", "TEST_FOUR": "1"}
    assert converted_list.to_dict() == test_dict_correct


def test_elyra_property_list_difference():
    env_variables = [
        {"env_var": "TEST", "value": "one"},
        {"env_var": "TEST_TWO", "value": "two"},
        {"env_var": "TEST_FOUR", "value": "1"},
    ]
    converted_list = ElyraProperty.create_instance("env_vars", env_variables)
    empty_list = ElyraPropertyList.difference(converted_list, converted_list)
    assert empty_list == []


def test_remove_env_vars_with_matching_secrets(monkeypatch):
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid_with_pipeline_default.json")

    # Mock set_elyra_properties_to_skip() so that a ComponentCache instance is not created unnecessarily
    monkeypatch.setattr(Node, "set_elyra_owned_properties", mock.Mock(return_value=None))
    monkeypatch.setattr(Node, "elyra_owned_properties", {KUBERNETES_SECRETS, ENV_VARIABLES})

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)
    node = None
    for node in pipeline_definition.pipeline_nodes:
        if node.op == "execute-notebook-node":  # assign the generic node to the node variable
            break

    # Set kubernetes_secret property to have all the same keys as those in the env_vars property
    kubernetes_secrets = ElyraPropertyList(
        [
            KubernetesSecret(env_var="var1", name="name1", key="key1"),
            KubernetesSecret(env_var="var2", name="name2", key="key2"),
            KubernetesSecret(env_var="var3", name="name3", key="key3"),
        ]
    )
    node.set_component_parameter(KUBERNETES_SECRETS, kubernetes_secrets)
    node.remove_env_vars_with_matching_secrets()
    assert node.get_component_parameter(ENV_VARIABLES) == []


def _check_pipeline_correct_pipeline_name():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")
    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    primary_pipeline = pipeline_definition.primary_pipeline

    assert primary_pipeline.name == "{{name}}"


def _check_pipeline_correct_pipeline_alternative_name():
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid_alternative_name.json")
    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    primary_pipeline = pipeline_definition.primary_pipeline

    assert primary_pipeline.name == "{{alternative_name}}"


#####################
# Utility functions #
#####################
def _check_missing_pipeline_field(field: str, error_msg: str):
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")
    pipeline_json.pop(field)

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    assert pipeline_definition.is_valid() is False
    assert error_msg in pipeline_definition.validate()


def _check_pipeline_field_type(field: str, wrong_type_value: any, error_msg: str):
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")
    pipeline_json.pop(field)
    pipeline_json[field] = wrong_type_value

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    assert pipeline_definition.is_valid() is False
    assert error_msg in pipeline_definition.validate()


def _check_missing_primary_pipeline_field(field: str, error_msg: str):
    pipeline_json = _read_pipeline_resource("resources/sample_pipelines/pipeline_valid.json")
    pipeline_json["pipelines"][0].pop(field)

    pipeline_definition = PipelineDefinition(pipeline_definition=pipeline_json)

    assert pipeline_definition.is_valid() is False
    assert error_msg in pipeline_definition.validate()
