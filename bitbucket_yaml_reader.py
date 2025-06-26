#!/usr/bin/env python3
"""
Bitbucket YAML File Reader and Parser

This script authenticates with Bitbucket using an access token and reads YAML files
from a specified repository, then parses them using PyYAML.
"""

import requests
import yaml
import json
import os
from typing import Dict, Any, List
from urllib.parse import urljoin


class BitbucketYAMLReader:
    def __init__(self, access_token: str, workspace: str, repository: str):
        """
        Initialize the Bitbucket YAML reader.

        Args:
            access_token (str): Bitbucket access token
            workspace (str): Bitbucket workspace name
            repository (str): Repository name
        """
        self.access_token = access_token
        self.workspace = workspace
        self.repository = repository
        self.base_url = "https://api.bitbucket.org/2.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get_file_content(self, file_path: str) -> str:
        """
        Get the content of a file from Bitbucket.

        Args:
            file_path (str): Path to the file in the repository

        Returns:
            str: File content
        """
        url = f"{self.base_url}/repositories/{self.workspace}/{self.repository}/src/main/{file_path}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching file {file_path}: {e}")
            return None

    def list_yaml_files(self) -> List[str]:
        """
        List all YAML files in the repository.

        Returns:
            List[str]: List of YAML file paths
        """
        url = (
            f"{self.base_url}/repositories/{self.workspace}/{self.repository}/src/main/"
        )

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            yaml_files = []
            for item in data.get("values", []):
                if item["type"] == "commit_file" and item["path"].endswith(
                    (".yml", ".yaml")
                ):
                    yaml_files.append(item["path"])

            return yaml_files
        except requests.exceptions.RequestException as e:
            print(f"Error listing files: {e}")
            return []

    def parse_yaml_content(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML content using PyYAML.

        Args:
            content (str): YAML content as string

        Returns:
            Dict[str, Any]: Parsed YAML data
        """
        try:
            # Try to parse as single document first
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            # If single document fails, try multi-document
            try:
                documents = list(yaml.safe_load_all(content))
                if len(documents) == 1:
                    return documents[0]
                else:
                    # Return a dictionary with numbered documents
                    return {f"document_{i+1}": doc for i, doc in enumerate(documents)}
            except yaml.YAMLError as e2:
                print(f"Error parsing YAML (both single and multi-document): {e2}")
                return None

    def read_and_parse_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a YAML file from the repository.

        Args:
            file_path (str): Path to the YAML file

        Returns:
            Dict[str, Any]: Parsed YAML data
        """
        content = self.get_file_content(file_path)
        if content:
            return self.parse_yaml_content(content)
        return None

    def print_parsed_info(self, data: Dict[str, Any], indent: int = 0):
        """
        Print parsed YAML data in a readable format.

        Args:
            data: Parsed YAML data
            indent: Indentation level
        """
        if data is None:
            print("No data to print")
            return

        indent_str = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{indent_str}{key}:")
                    self.print_parsed_info(value, indent + 1)
                else:
                    print(f"{indent_str}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                print(f"{indent_str}[{i}]:")
                self.print_parsed_info(item, indent + 1)
        else:
            print(f"{indent_str}{data}")
