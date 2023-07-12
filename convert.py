import os
import json
import time
from enum import Enum


class Converter:
    class _WriteMode(Enum):
        Overwrite = 1
        CreateNew = 2

    class _ConverterType(Enum):
        Generic = 0
        Local_Settings_FunctionApp = 1
        Azure_DevOps_Release_Pipeline_FunctionApp = 2
        Azure_FunctionApp = 3

    def __init__(self):
        with open("converter.json") as config_file:
            self.config_data = json.load(config_file)
        self.folder_name = self.config_data["folderName"]
        self.write_mode = self.config_data["writeMode"]
        self.is_sorted = self.config_data.get("isSorted", False)
        self.reversed_sort = self.config_data.get("reversedSort", False)
        self.env_mappings = self.config_data["configPath"]["env"]
        self.variables = self.config_data["variables"]
        self.ignore_variables = self.config_data["ignoreVariables"]

    def convert_configs(self):
        for env_mapping in self.env_mappings:
            convert_from = env_mapping.get("convertFrom", self._ConverterType.Generic.name)
            convert_to = env_mapping.get("convertTo", self._ConverterType.Generic.name)
            names = env_mapping["names"]
            path_mappings = env_mapping["path"]

            for environment in names:
                output_folder = self.__get_output_folder_path(environment, convert_to)
                os.makedirs(output_folder, exist_ok=True)

                for path_filename in path_mappings:
                    path, filename = path_filename
                    with open(path) as file:
                        data = file.read()
                        converted_data = self.__convert(data, environment, convert_from, convert_to)

                    output_file_name = os.path.join(output_folder, f"{environment}_{filename}.{convert_to}")

                    with open(output_file_name, "w") as output_file:
                        output_file.write(str(converted_data))  # Convert to string explicitly

    def __get_output_folder_path(self, environment, convert_to):
        if self._WriteMode[self.write_mode] == self._WriteMode.CreateNew:
            timestamp = str(int(time.time()))
            return f"{self.folder_name}_{timestamp}/{environment}_environment/{convert_to}"
        else:
            return f"{self.folder_name}/{environment}_environment/{convert_to}"

    def __convert(self, data, environment, convert_from, convert_to):
        if convert_from == self._ConverterType.Local_Settings_FunctionApp.name and convert_to == self._ConverterType.Azure_DevOps_Release_Pipeline_FunctionApp.name:
            return self.__convert_local_to_pipeline(data, environment)
        elif convert_from == self._ConverterType.Azure_DevOps_Release_Pipeline_FunctionApp.name and convert_to == self._ConverterType.Azure_FunctionApp.name:
            return self.__convert_pipeline_to_azure_fa_config(data, environment)
        # Add more converters here for other conversion types
        elif convert_from == self._ConverterType.Generic.name:
            return self.__convert_generic(data, environment)
        else:
            raise ValueError("Unsupported conversion types specified")

    def __convert_generic(self, data, environment):
        # Placeholder for the generic conversion logic
        pass

    def __convert_local_to_pipeline(self, data, environment):
        parsed_data = json.loads(data)
        formatted_strings = []
        for key, value in self.__sorted_items(parsed_data["Values"]):
            if key not in self.ignore_variables:
                formatted_value = self.__replace_variables(key, value, environment)
                formatted_strings.append(f'-{key} "{formatted_value}"')
        formatted_output = " ".join(formatted_strings)
        return formatted_output

    def __convert_pipeline_to_azure_fa_config(self, data, environment):
        json_data = json.loads(data)
        values = json_data["Values"]
        result = []
        for key, value in self.__sorted_items(values):
            if key not in self.ignore_variables:
                formatted_value = self.__replace_variables(key, value, environment)
                result.append({"name": key, "value": formatted_value, "slotSetting": False})
        converted_data = json.dumps(result, indent=2)
        return converted_data

    def __replace_variables(self, key, value, environment):
        if environment in self.variables and key in self.variables[environment]:
            value = self.variables[environment][key]
            if value.startswith("#$") and value.endswith("$#"):
                extracted_value = value[2:-2]
                value = self.variables[extracted_value][key]
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
    converter.convert_configs()


if __name__ == "__main__":
    main()
