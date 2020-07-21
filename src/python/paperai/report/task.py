"""
Config module
"""

import os

import yaml

class Task(object):
    """
    YAML task configuration loader
    """

    @staticmethod
    def load(task):
        """
        Loads a YAML configuration. Supports loading from a string or file path.

        Args:
            task: YAML string or file path to YAML configuration

        Returns:
            (name, queries, output directory)
        """

        if os.path.exists(task):
            # Load tasks yml file
            with open(task, "r") as f:
                # Read configuration
                config = yaml.safe_load(f)

                # Write output to same directory as input
                outdir = os.path.dirname(task)
        else:
            # Assume task is a yml string
            config = yaml.safe_load(task)
            outdir = "."

        # Extract queries
        queries = Task.queries(config)

        return config["name"], queries, outdir

    @staticmethod
    def queries(config):
        """
        Gets a list of queries from this configuration.

        Args:
            config: configuration object

        Returns:
            list of queries
        """

        queries = []

        for key, value in config.items():
            if key not in ["id", "name", "fields"]:
                # Flatten columns
                value["columns"] = Task.flatten(value["columns"])

                # Add query
                queries.append((key, value))

        return queries

    @staticmethod
    def flatten(columns):
        """
        Flattens nested lists into a single list.

        Args:
            columns: list of columns, possibly with nested lists

        Returns:
            flattened list of columns
        """

        output = []
        for column in columns:
            if isinstance(column, list):
                output.extend(column)
            else:
                output.append(column)

        return output
