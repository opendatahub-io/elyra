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
"""
Lightweight unit tests for URL decode and path validation fixes.
"""

import os
import tempfile
from unittest.mock import Mock, patch
from urllib.parse import quote

import pytest

from elyra.airflow import bootstrapper as airflow_bootstrapper
from elyra.kfp import bootstrapper as kfp_bootstrapper


class TestValidatePath:
    """Test the validate_path security method"""

    def test_kfp_validate_safe_relative_paths(self):
        """Test that safe relative paths pass validation"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: kfp_bootstrapper.FileOpBase.has_wildcard(mock_instance, filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                safe_paths = ["model/output.txt", "data/results.csv", "subdir/file.bin"]

                for path in safe_paths:
                    result = kfp_bootstrapper.FileOpBase.validate_path(mock_instance, path)
                    assert result == path
            finally:
                os.chdir(original_cwd)

    def test_kfp_validate_safe_wildcard_paths(self):
        """Test that wildcard paths pass validation"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: kfp_bootstrapper.FileOpBase.has_wildcard(mock_instance, filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                os.makedirs("model", exist_ok=True)
                wildcard_paths = ["model/*", "data/*.txt", "output/**/*.csv"]

                for path in wildcard_paths:
                    result = kfp_bootstrapper.FileOpBase.validate_path(mock_instance, path)
                    assert result == path
            finally:
                os.chdir(original_cwd)

    def test_kfp_validate_blocks_parent_traversal(self):
        """Test that parent directory traversal is blocked"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: kfp_bootstrapper.FileOpBase.has_wildcard(mock_instance, filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                malicious_paths = ["../../../etc/passwd", "../../secret.txt", "../config.yml"]

                for path in malicious_paths:
                    with pytest.raises(ValueError, match="Path traversal"):
                        kfp_bootstrapper.FileOpBase.validate_path(mock_instance, path)
            finally:
                os.chdir(original_cwd)

    def test_kfp_validate_blocks_mixed_traversal(self):
        """Test that mixed path traversal is blocked"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: kfp_bootstrapper.FileOpBase.has_wildcard(mock_instance, filename)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                mixed_paths = ["output/../../etc/passwd", "data/../../../secret.txt"]

                for path in mixed_paths:
                    with pytest.raises(ValueError, match="Path traversal"):
                        kfp_bootstrapper.FileOpBase.validate_path(mock_instance, path)
            finally:
                os.chdir(original_cwd)

    def test_airflow_validate_safe_paths(self):
        """Test that Airflow validate_path works identically"""
        mock_instance = Mock(spec=airflow_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: airflow_bootstrapper.FileOpBase.has_wildcard(
            mock_instance, filename
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                result = airflow_bootstrapper.FileOpBase.validate_path(mock_instance, "model/output.txt")
                assert result == "model/output.txt"
            finally:
                os.chdir(original_cwd)

    def test_airflow_validate_blocks_traversal(self):
        """Test that Airflow validate_path blocks traversal"""
        mock_instance = Mock(spec=airflow_bootstrapper.FileOpBase)
        mock_instance.has_wildcard = lambda filename: airflow_bootstrapper.FileOpBase.has_wildcard(
            mock_instance, filename
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with pytest.raises(ValueError, match="Path traversal"):
                    airflow_bootstrapper.FileOpBase.validate_path(mock_instance, "../../../etc/passwd")
            finally:
                os.chdir(original_cwd)


class TestURLDecodeInputs:
    """Test URL decoding in process_dependencies for input files"""

    def test_kfp_process_dependencies_decodes_single_input(self):
        """Test that a single URL-encoded input is decoded"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.input_params = {
            "cos-dependencies-archive": "archive.tgz",
            "inputs": f"model/{quote('*')}.bin",
        }
        mock_instance.get_file_from_object_storage = Mock()

        with patch("subprocess.call"):
            kfp_bootstrapper.FileOpBase.process_dependencies(mock_instance)

        calls = [call[0][0] for call in mock_instance.get_file_from_object_storage.call_args_list]
        assert calls[0] == "archive.tgz"
        assert calls[1] == "model/*.bin"

    def test_kfp_process_dependencies_decodes_multiple_inputs(self):
        """Test that multiple URL-encoded inputs are decoded"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.input_params = {
            "cos-dependencies-archive": "archive.tgz",
            "inputs": f"input/{quote('*')}.txt;data/{quote('?')}.csv;normal.file",
        }
        mock_instance.get_file_from_object_storage = Mock()

        with patch("subprocess.call"):
            kfp_bootstrapper.FileOpBase.process_dependencies(mock_instance)

        calls = [call[0][0] for call in mock_instance.get_file_from_object_storage.call_args_list]
        assert calls[0] == "archive.tgz"
        assert calls[1] == "input/*.txt"
        assert calls[2] == "data/?.csv"
        assert calls[3] == "normal.file"

    def test_kfp_process_dependencies_handles_no_inputs(self):
        """Test that process_dependencies works with no inputs"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)
        mock_instance.input_params = {
            "cos-dependencies-archive": "archive.tgz",
            "inputs": None,
        }
        mock_instance.get_file_from_object_storage = Mock()

        with patch("subprocess.call"):
            kfp_bootstrapper.FileOpBase.process_dependencies(mock_instance)

        # Should only fetch the archive
        calls = [call[0][0] for call in mock_instance.get_file_from_object_storage.call_args_list]
        assert calls == ["archive.tgz"]

    def test_airflow_process_dependencies_decodes_inputs(self):
        """Test that Airflow process_dependencies decodes inputs"""
        mock_instance = Mock(spec=airflow_bootstrapper.FileOpBase)
        mock_instance.input_params = {
            "cos-dependencies-archive": "archive.tgz",
            "inputs": f"openvino/{quote('*')}.xml;openvino/{quote('*')}.bin",
        }
        mock_instance.get_file_from_object_storage = Mock()

        with patch("subprocess.call"):
            airflow_bootstrapper.FileOpBase.process_dependencies(mock_instance)

        calls = [call[0][0] for call in mock_instance.get_file_from_object_storage.call_args_list]
        assert calls[0] == "archive.tgz"
        assert calls[1] == "openvino/*.xml"
        assert calls[2] == "openvino/*.bin"


class TestURLDecodeOutputs:
    """Test URL decoding in process_outputs"""

    def test_kfp_process_outputs_decodes_and_validates(self):
        """Test that process_outputs decodes and validates output paths"""
        mock_instance = Mock(spec=kfp_bootstrapper.FileOpBase)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                os.makedirs("model", exist_ok=True)

                mock_instance.input_params = {"outputs": f"model/{quote('*')};data/{quote('?')}.csv"}
                mock_instance.process_output_file = Mock()

                # Use real validate_path
                def real_validate(path):
                    return kfp_bootstrapper.FileOpBase.validate_path(mock_instance, path)

                mock_instance.validate_path = Mock(side_effect=real_validate)

                kfp_bootstrapper.FileOpBase.process_outputs(mock_instance)

                # Verify validate_path was called with decoded paths
                validate_calls = [call[0][0] for call in mock_instance.validate_path.call_args_list]
                assert validate_calls == ["model/*", "data/?.csv"]

                # Verify process_output_file was called with validated paths
                output_calls = [call[0][0] for call in mock_instance.process_output_file.call_args_list]
                assert output_calls == ["model/*", "data/?.csv"]
            finally:
                os.chdir(original_cwd)

    def test_airflow_process_outputs_decodes_and_validates(self):
        """Test that Airflow process_outputs decodes and validates"""
        mock_instance = Mock(spec=airflow_bootstrapper.FileOpBase)

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                os.makedirs("output", exist_ok=True)

                mock_instance.input_params = {"outputs": f"output/{quote('**')}/{quote('*')}.txt"}
                mock_instance.process_output_file = Mock()

                def real_validate(path):
                    return airflow_bootstrapper.FileOpBase.validate_path(mock_instance, path)

                mock_instance.validate_path = Mock(side_effect=real_validate)

                airflow_bootstrapper.FileOpBase.process_outputs(mock_instance)

                validate_calls = [call[0][0] for call in mock_instance.validate_path.call_args_list]
                assert validate_calls == ["output/**/*.txt"]

                output_calls = [call[0][0] for call in mock_instance.process_output_file.call_args_list]
                assert output_calls == ["output/**/*.txt"]
            finally:
                os.chdir(original_cwd)
