import os
import json
import time
from enum import Enum
from typing import Dict, List, Tuple
import datetime
import argparse
import glob

class Converter:
    VERSION = "2.0"

    class _WriteMode(Enum):
        Overwrite = 1
        CreateNew = 2

    def __init__(self, config_file="converter.json"):
        with open(config_file) as config_file:
            self.config_data = json.load(config_file)
            self.unique_variables = set()
        self.folder_name = self.config_data["folderName"]
        self.pipeline_folder_name = self.config_data["pipelineFolderName"]
        self.function_app_folder_name = self.config_data["functionAppFolderName"]
        self.search_pattern = self.config_data["searchPattern"]
        self.write_mode = self._WriteMode[self.config_data["writeMode"]]
        self.is_sorted = self.config_data.get("isSorted", False)
        self.reversed_sort = self.config_data.get("reversedSort", False)
        self.env_mappings = self.config_data["configPath"]["env"]
        self.variables = self.config_data["variables"]
        self.ignore_variables = self.config_data["ignoreVariables"]
        self.generated_files = []
        self.config_files = self.__find_config_files()

    def __find_config_files(self):
        config_files = []
        base_pattern, file_placeholder = self.search_pattern.split("{")
        base_pattern = base_pattern.rstrip('\\') 

        function_dirs = glob.glob(base_pattern)
        
        for function_dir in function_dirs:
            for env_mapping in self.env_mappings:
                for file_name in env_mapping.get("files", []):
                    file_path = os.path.join(function_dir, file_name)
                    if os.path.exists(file_path):
                        config_files.append(file_path)

        print(f"Found config files: {config_files}")
        return config_files

    def process_configurations(self):
        try:
            self.local_to_pipeline()
            self.pipeline_to_azure_fa_config()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def local_to_pipeline(self):
        self.__process_files(
            self.__get_output_folder_path_local_to_pipeline,
            ".txt",
            self.__convert_local_to_pipeline,
        )

    def pipeline_to_azure_fa_config(self):
        self.__process_files(
            self.__get_output_folder_path_pipeline_to_azure_fa,
            ".json",
            self.__convert_pipeline_to_azure_fa_config,
        )

    def __get_output_folder_path(self, environment: str, subfolder: str) -> str:
        base_path = self.folder_name
        if self.write_mode == self._WriteMode.CreateNew:
            timestamp = str(int(time.time()))
            base_path = f"{self.folder_name}_{timestamp}"
        return os.path.join(base_path, f"{environment}_environment", subfolder)

    def __get_output_folder_path_local_to_pipeline(self, environment: str) -> str:
        return self.__get_output_folder_path(environment, self.pipeline_folder_name)

    def __get_output_folder_path_pipeline_to_azure_fa(self, environment: str) -> str:
        return self.__get_output_folder_path(environment, self.function_app_folder_name)

    def __process_files(self, get_output_folder_path_func, file_extension: str, convert_func):
        for env_mapping in self.env_mappings:
            for environment in env_mapping["names"]:
                output_folder = get_output_folder_path_func(environment)
                os.makedirs(output_folder, exist_ok=True)

                for file_path in self.config_files:
                    try:
                        with open(file_path) as file:
                            data = file.read()
                            converted_data, variables = convert_func(data, environment)

                        self.unique_variables.update(variables)  # Add variables to the set

                        wildcard_value = os.path.basename(os.path.dirname(file_path))

                        output_file_name = os.path.join(output_folder, f"{environment}-{wildcard_value}{file_extension}")

                        self.__write_output_file(output_file_name, converted_data)
                        self.generated_files.append(output_file_name)
                        print(f"Converted file: {output_file_name}")
                    except json.JSONDecodeError:
                        print(f"Warning: Unable to parse file: {file_path}. Skipping.")
                    except Exception as e:
                        print(f"Error processing file {file_path}: {str(e)}")

        # After processing all files, create the variable-list.json
        self.__create_variable_list()

    def __write_output_file(self, file_name: str, content: str):
        with open(file_name, "w") as output_file:
            output_file.write(content)

    def __convert_local_to_pipeline(self, data: str, environment: str) -> Tuple[str, List[str]]:
        parsed_data = json.loads(data)
        variables = list(parsed_data["Values"].keys())
        formatted_strings = [
            f'-{key} "{self.__replace_variables(key, value, environment, self.variables)}"'
            for key, value in self.__sorted_items(parsed_data["Values"])
            if key not in self.ignore_variables
        ]
        return " ".join(formatted_strings), variables

    def __convert_pipeline_to_azure_fa_config(self, data: str, environment: str) -> Tuple[str, List[str]]:
        json_data = json.loads(data)
        variables = list(json_data["Values"].keys())
        result = [
            {"name": key, "value": str(self.__replace_variables(key, value, environment, self.variables)), "slotSetting": False}
            for key, value in self.__sorted_items(json_data["Values"])
            if key not in self.ignore_variables
        ]
        return json.dumps(result, indent=2), variables

    def __replace_variables(self, key: str, value: str, environment: str, variables: Dict) -> str:
        if environment in variables and key in variables[environment]:
            value = variables[environment][key]
            if isinstance(value, str) and value.startswith("#$") and value.endswith("$#"):
                extracted_value = value[2:-2]
                value = variables[extracted_value][key]
        return value

    def __sorted_items(self, dictionary: Dict) -> List[Tuple[str, str]]:
        items = dictionary.items()
        if self.is_sorted:
            items = sorted(items, reverse=self.reversed_sort)
        return items

    def azure_to_local(self, input_file_path):
        try:
            output_folder = os.path.join(self.folder_name, "AZtoLocal")
            os.makedirs(output_folder, exist_ok=True)

            with open(input_file_path, 'r') as file:
                data = file.read()
                converted_data, variables = self.__convert_azure_to_local(data, "")

            self.unique_variables.update(variables)

            output_file_name = os.path.join(output_folder, f"local.settings.json")
            self.__write_output_file(output_file_name, converted_data)
            self.generated_files.append(output_file_name)
            print(f"Conversion complete. Output file: {output_file_name}")

            # Create variable-list.json after processing
            self.__create_variable_list()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def __convert_azure_to_local(self, data: str, environment: str) -> Tuple[str, List[str]]:
        azure_config = json.loads(data)
        local_config = {
            "IsEncrypted": False,
            "Values": {}
        }
        
        variables = []
        for item in azure_config:
            local_config["Values"][item["name"]] = item["value"]
            variables.append(item["name"])

        return json.dumps(local_config, indent=2), variables

    def __create_variable_list(self):
        variable_list = {
            "variables": sorted(list(self.unique_variables))
        }
        output_file_name = os.path.join(self.folder_name, "variable-list.json")
        with open(output_file_name, "w") as output_file:
            json.dump(variable_list, output_file, indent=2)
        print(f"Created variable list: {output_file_name}")

def main():
    parser = argparse.ArgumentParser(description="Azure Function App Configuration Converter")
    parser.add_argument("--LocalToPipeline", action="store_true", help="Convert local config to pipeline config")
    parser.add_argument("--PipelineToAzure", action="store_true", help="Convert pipeline config to Azure Function App config")
    parser.add_argument("--AZtoLocal", action="store_true", help="Convert Azure Function App config to local config")
    parser.add_argument("--file", type=str, help="Path of the file to convert (required for AZtoLocal)")
    args = parser.parse_args()

    converter = Converter()

    if args.LocalToPipeline:
        converter.local_to_pipeline()
    elif args.PipelineToAzure:
        converter.pipeline_to_azure_fa_config()
    elif args.AZtoLocal:
        if not args.file:
            print("Error: --file is required when using --AZtoLocal")
            return
        converter.azure_to_local(args.file)
    else:
        converter.process_configurations()

if __name__ == "__main__":
    main()