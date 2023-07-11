import os
import json
import time
from enum import Enum

class Converter:
    class _WriteMode(Enum):
        Overwrite = 1
        CreateNew = 2

    def __init__(self):
        with open("converter.json") as config_file:
            self.config_data = json.load(config_file)
        self.folder_name = self.config_data["folderName"]
        self.pipeline_folder_name = self.config_data["pipelineFolderName"]
        self.function_app_folder_name = self.config_data["functionAppFolderName"]
        self.write_mode = self.config_data["writeMode"]
        self.is_sorted = self.config_data.get("isSorted", False)
        self.reversed_sort = self.config_data.get("reversedSort", False)
        self.env_mappings = self.config_data["configPath"]["env"]
        self.variables = self.config_data["variables"]
        self.ignore_variables = self.config_data["ignoreVariables"]

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

    def __get_output_folder_path_local_to_pipeline(self, environment):
        if self._WriteMode[self.write_mode] == self._WriteMode.CreateNew:
            timestamp = str(int(time.time()))
            return f"{self.folder_name}_{timestamp}/{environment}_environment/{self.pipeline_folder_name}"
        else:
            return f"{self.folder_name}/{environment}_environment/{self.pipeline_folder_name}"

    def __get_output_folder_path_pipeline_to_azure_fa(self, environment):
        if self._WriteMode[self.write_mode] == self._WriteMode.CreateNew:
            timestamp = str(int(time.time()))
            return f"{self.folder_name}_{timestamp}/{environment}_environment/{self.function_app_folder_name}"
        else:
            return f"{self.folder_name}/{environment}_environment/{self.function_app_folder_name}"

    def __process_files(self, get_output_folder_path_func, file_extension, convert_func):
        for env_mapping in self.env_mappings:
            environment_names = env_mapping["names"]
            path_mappings = env_mapping["path"]

            for environment in environment_names:
                output_folder = get_output_folder_path_func(environment)
                os.makedirs(output_folder, exist_ok=True)

                for path_filename in path_mappings:
                    path, filename = path_filename
                    with open(path) as file:
                        data = file.read()
                        converted_data = convert_func(data, environment)

                    output_file_name = os.path.join(output_folder, f"{environment}_{filename}{file_extension}")

                    with open(output_file_name, "w") as output_file:
                        output_file.write(converted_data)

    def __convert_local_to_pipeline(self, data, environment):
        parsed_data = json.loads(data)
        formatted_strings = []
        for key, value in self.__sorted_items(parsed_data["Values"]):
            if key not in self.ignore_variables:
                formatted_value = self.__replace_variables(key, value, environment, self.variables)
                formatted_strings.append(f'-{key} "{formatted_value}"')
        formatted_output = " ".join(formatted_strings)
        return formatted_output

    def __convert_pipeline_to_azure_fa_config(self, data, environment):
        json_data = json.loads(data)
        values = json_data["Values"]
        result = []
        for key, value in self.__sorted_items(values):
            if key not in self.ignore_variables:
                formatted_value = self.__replace_variables(key, value, environment, self.variables)
                result.append({"name": key, "value": formatted_value, "slotSetting": False})
        converted_data = json.dumps(result, indent=2)
        return converted_data

    def __replace_variables(self, key, value, environment, variables):
        if environment in variables and key in variables[environment]:
            value = variables[environment][key]
            if value.startswith("#$") and value.endswith("$#"):
                extracted_value = value[2:-2]
                value = variables[extracted_value][key]
            return value
        else:
            return value

    def __sorted_items(self, dictionary):
        if self.is_sorted:
            items = sorted(dictionary.items())
            if self.reversed_sort:
                items = reversed(items)
            return items
        else:
            return dictionary.items()

    @staticmethod
    def __create_config_meta_data(file_path, metadata):
        pass


def main():
    converter = Converter()
    converter.local_to_pipeline()
    converter.pipeline_to_azure_fa_config()


if __name__ == "__main__":
    main()
