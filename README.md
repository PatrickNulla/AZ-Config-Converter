# AZ-Config-Converter [Python]
The Converter is a Python script that processes Local Azure Function App Configuration to Azure DevOps Release Pipeline Configuration and Azure Function App Configuration

## Prerequisites
- Python 3.x

## Usage
1. Place the `converter.py` file and the configuration file (`converter.json`) in the same directory.

2. Open the `converter.json` file and update the configuration to match your specific requirements. The configuration consists of two sections:
   - `config-path`: Contains environment mappings and file paths.
   - `variables`: Defines the value per configuration keys for specific environments.

   Replace the placeholder values with your actual configuration paths, environment, and configuration keys.

   Example `converter.json` file:
   ```json
   {
       "config-path": {
           "env": [
               {
                   "names":[
                       "list of your",
                       "environments"
                   ],
                   "path":[
                       ["Path to your local config (e.g. local.settings.json)", "File name that it will use upon generation"],
                       ["Path to your local config (e.g. local.settings.json)", "e.g. FunctionApp1"],
                       ["E:/Sample/Path/To/Your/local.settings.json", "FileNameItWillUse"]
                   ]
               }
           ]
       },
       "variables":{
           "one_of_your":{
               "VariableInYour":"sample-value-1"
           },
           "environments":{
               "Configuration":"sample-value-2"
           },
           "in_the_names_list":{
               "ThatHasAUniqueValuePerEnvironment":"#$one_of_your$#"
           }
       }
   }
   ```

3. Open a terminal or command prompt and navigate to the directory containing the `converter.py` and `converter.json` files.

4. Run the script by executing the following command:
   ```
   python converter.py
   ```

5. The script will process the configurations and generate the formatted code and converted JSON files based on the specified paths and environment mappings.

6. The generated output will be placed in separate folders for each environment, as specified in the configuration.

## Customization
You can customize the behavior of the Converter script by modifying the configuration in the `converter.json` file according to your specific needs.

## Sample
- Todo: Add Sample Use Case