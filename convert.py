import os
import json

class Converter:
    @staticmethod
    def LocalToPipeline():
        with open('converter.json') as config_file:
            config_data = json.load(config_file)

        env_mappings = config_data['config-path']['env']
        variables = config_data['variables']

        for env_mapping in env_mappings:
            environment_names = env_mapping['names']
            path_mappings = env_mapping['path']

            for path, filename in path_mappings:
                for environment in environment_names:
                    output_folder = f'{environment}_environment\\Azure-DevOps-ReleasePipeline-Config'
                    os.makedirs(output_folder, exist_ok=True)

                    with open(path) as file:
                        data = file.read()
                        parsed_data = json.loads(data)

                        formatted_strings = []
                        for key, value in parsed_data['Values'].items():
                            formatted_value = Converter.replace_variables(key, value, environment, variables)
                            formatted_strings.append(f"-{key} \"{formatted_value}\"")

                        formatted_output = ' '.join(formatted_strings)

                    output_file_name = os.path.join(output_folder, f"{environment}_{filename}.txt")

                    with open(output_file_name, 'w') as output_file:
                        output_file.write(formatted_output)

    @staticmethod
    def PipelineToAzureFAConfig():
        with open('converter.json') as config_file:
            config_data = json.load(config_file)

        env_mappings = config_data['config-path']['env']
        variables = config_data['variables']

        for env_mapping in env_mappings:
            environment_names = env_mapping['names']
            path_mappings = env_mapping['path']

            for path, filename in path_mappings:
                for environment in environment_names:
                    output_folder = f'{environment}_environment\\Azure-FunctionApp-Config'
                    os.makedirs(output_folder, exist_ok=True)

                    with open(path) as file:
                        data = file.read()
                        json_data = json.loads(data)
                        values = json_data["Values"]

                        result = []
                        for key, value in values.items():
                            formatted_value = Converter.replace_variables(key, value, environment, variables)
                            result.append({
                                "name": key,
                                "value": formatted_value,
                                "slotSetting": False
                            })

                        converted_data = json.dumps(result, indent=2)

                    output_file_name = os.path.join(output_folder, f"{environment}-{filename}.json")

                    with open(output_file_name, 'w') as output_file:
                        output_file.write(converted_data)

    @staticmethod
    def replace_variables(key, value, environment, variables):
        if environment in variables and key in variables[environment]:
            value = variables[environment][key]
            if value.startswith('#$') and value.endswith('$#'):
                extracted_value = value[2:-2]
                value = variables[extracted_value][key]
            return value
        else:
            return value

def main():
    Converter.LocalToPipeline()
    Converter.PipelineToAzureFAConfig()

if __name__ == "__main__":
    main()
    