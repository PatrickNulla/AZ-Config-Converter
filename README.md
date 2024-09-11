# Local Function App Settings Converter [Python]

Version 2.0

A Python script used to convert Local Azure Function App Configuration to Azure DevOps Release Pipeline Configuration and Azure Function App Configuration.

[For the C# version with executable release click here. (OUTDATED)](https://github.com/PatrickNulla/CSharp-LocalAzureFAConfig-Converter)

## Prerequisites
- Python 3.x

## Usage
1. Place the `convert.py` file in your project directory.

2. Run the script for the first time to generate a template configuration file:
   ```
   python convert.py
   ```
   This will create a `template-converter.json` file in the same directory.

3. Rename `template-converter.json` to `gen-converter.json` and edit it to match your specific requirements. The configuration consists of the following sections:
   - `folderName`: The base folder name for output (will be prepended with "gen-").
   - `pipelineFolderName`: Folder name for the release pipeline generated config.
   - `functionAppFolderName`: Folder name for the Azure Function App generated config.
   - `searchPattern`: Pattern to search for configuration files (e.g., "C:\\Path\\To\\Your\\Project\\FunctionApps.*\\{files}").
   - `writeMode`: Generation mode for the config, either Overwrite or CreateNew. Overwrite mode replaces the whole base folder. CreateNew mode generates a new folder with the Unix time appended to prevent replacing the previously generated configurations.
   - `isSorted`: Sorts the generated configurations alphabetically. (true | false)
   - `reversedSort`: Reverses the order of the keys in the generated configurations. (true | false)
   - `configPath`: Contains environment mappings and file names.
   - `variables`: Defines the value per configuration keys for specific environments (You could use the environment name to reuse the previously set value for that variable e.g. #$Environment_Name$#).
   - `ignoreVariables`: List of variables to be ignored in the generated configurations (Instead of removing the variable in the 'variables' key, list out the unnecessary variables for documentation).

   Replace the placeholder values with your actual configuration paths, environments, and configuration keys.

   Example `gen-converter.json` file:
   ```json
    {
        "folderName": "OutputFolder",
        "pipelineFolderName": "PipelineConfig",
        "functionAppFolderName": "FunctionAppConfig",
        "searchPattern": "C:\\Path\\To\\Your\\Project\\FunctionApps.*\\{files}",
        "writeMode": "Overwrite",
        "isSorted": true,
        "reversedSort": false,
        "configPath": {
            "env": [
                {
                    "names": [
                        "dev",
                        "staging",
                        "production"
                    ],
                    "files": [
                        "local.settings.json"
                    ]
                }
            ]
        },
        "variables": {
            "dev": {
                "EXAMPLE_VAR": "dev_value"
            },
            "staging": {
                "EXAMPLE_VAR": "staging_value"
            },
            "production": {
                "EXAMPLE_VAR": "prod_value"
            }
        },
        "ignoreVariables": [
            "WEBSITE_RUN_FROM_PACKAGE"
        ]
    }
   ```

4. Run the script again to process the configurations:
   ```
   python convert.py
   ```

5. The script will process the configurations and generate the formatted code and converted JSON files based on the specified search pattern and environment mappings.

6. The generated output will be placed in separate folders for each environment, as specified in the configuration, all within a "gen-" prefixed base folder.

## Command-line Arguments
The script supports the following command-line arguments:
- `--config`: Specify a custom path to the configuration file (default is "gen-converter.json").
- `--LocalToPipeline`: Convert local config to pipeline config only.
- `--PipelineToAzure`: Convert pipeline config to Azure Function App config only.
- `--AZtoLocal`: Convert Azure Function App config to local config (requires `--file` argument).
- `--file`: Specify the input file path for AZtoLocal conversion.

Example:
```
python convert.py --config my-config.json --LocalToPipeline
```

## Customization
You can customize the behavior of the Converter script by modifying the configuration in the `gen-converter.json` file according to your specific needs.

### Sample
[Check out the actual sample files here.](https://github.com/PatrickNulla/Azure-FunctionApp-Configuration-Converter/tree/main/Sample)

For this example, let's base the configuration on the following scenario:
- You have 3 environments: `dev`, `staging`, and `production`.
- In production, you have 2 different payment methods: `Paypal` and `Stripe`.
- You have 2 Azure Function Apps: `Account` and `Payment` Function Apps.
- You have 3 different connection strings for each environment: `dev-connectionstring`, `staging-connectionstring`, and `production-connectionstring`.
- You have 2 different API keys for each payment method: `PaypalAPIKey` and `StripeAPIKey`.

For our scenario, the local.settings.json for the Payment Function App looks like this:
```json
{
  "IsEncrypted": false,
  "Values": {
    "DBConnectionString": "someValue",
    "Version": "someValue",
    "PaymentAPIKey": "someValue"
  }
}
```

For example, you have this converter configuration:
```json
    {
        "folderName": "Sample/Generated Configs",
        "pipelineFolderName": "Pipeline Configs",
        "functionAppFolderName": "Azure Function App Configs",
        "searchPattern": "D:\\Sample\\Local Settings\\*\\local.settings.json",
        "writeMode": "Overwrite",
        "isSorted": true,
        "reversedSort": false,   
        "configPath": {
            "env": [
                {
                    "names": [
                        "dev",
                        "staging"
                    ],
                    "files": ["local.settings.json"]
                },
                {
                    "names": [
                        "production-account"
                    ],
                    "files": ["local.settings.json"]
                },
                {
                    "names": [
                        "production-paypal",
                        "production-stripe"
                    ],
                    "files": ["local.settings.json"]
                }
            ]
        },
        "variables": {
            "dev": {
                "DBConnectionString": "dev-connectionstring"
            },
            "staging": {
                "DBConnectionString": "staging-connectionstring"
            },
            "production-account": {
                "DBConnectionString": "production-connectionstring"
            },
            "production-paypal": {
                "DBConnectionString": "#$production-account$#",
                "Version": "1.0.0",
                "PaymentAPIKey": "PaypalAPIKey"
            },
            "production-stripe": {
                "DBConnectionString": "#$production-account$#",
                "Version": "1.0.1",
                "PaymentAPIKey": "StripeAPIKey"
            }
        },
        "ignoreVariables": [
            "Version"
        ]
    }
```
The output folder structure would be as follows:
```
gen-Sample\Generated Configs
|
|---dev_environment
|   |
|   |---Pipeline Configs
|   |  |
|   |  |---dev-AccountFA.txt
|   |  |---dev-PaymentFA.txt
|   |
|   |---Azure Function App Configs
|      |
|      |---dev-AccountFA.json
|      |---dev-PaymentFA.json
|    
|---staging_environment
|   |
|   |---Pipeline Configs
|   |  |
|   |  |---staging-AccountFA.txt
|   |  |---staging-PaymentFA.txt
|   |
|   |---Azure Function App Configs
|      |
|      |---staging-AccountFA.json
|      |---staging-PaymentFA.json
|
|---production-account_environment
|   |
|   |---Pipeline Configs
|   |  |
|   |  |---production-account-AccountFA.txt
|   |
|   |---Azure Function App Configs
|      |
|      |---production-account-AccountFA.json
|
|---production-paypal_environment
|   |
|   |---Pipeline Configs
|   |  |
|   |  |---production-paypal-PaymentFA.txt
|   |
|   |---Azure Function App Configs
|      |
|      |---production-paypal-PaymentFA.json
|
|---production-stripe_environment
|   |
|   |---Pipeline Configs
|   |  |
|   |  |---production-stripe-PaymentFA.txt
|   |
|   |---Azure Function App Configs
|      |
|      |---production-stripe-PaymentFA.json
|
|---variable-list.json
```

**Sample Release Pipeline config output**
#### dev-PaymentFA.txt (Azure DevOps Release Pipeline Configuration)

`-DBConnectionString "dev-connectionstring" -PaymentAPIKey "DevTestAPIKey"`

**Sample Azure Function App config output**
#### dev-PaymentFA.json (Azure Function App Configuration)
```json
[
    {
        "name": "DBConnectionString",
        "value": "dev-connectionstring",
        "slotSetting": false
    },
    {
        "name": "PaymentAPIKey",
        "value": "DevTestAPIKey",
        "slotSetting": false
    }
]
```

## Output
The script generates the following outputs:
1. Converted configuration files for each environment and function app.
2. A `variable-list.json` file in the base output folder, containing a sorted list of all unique variables found during the conversion process.

## Note on Security
The script prepends "gen-" to the output folder name. It's recommended to add "gen-*" to your .gitignore file to avoid accidentally pushing sensitive data to version control.

## Error Handling
The script includes basic error handling and will print error messages if issues occur during the conversion process.

# Todo
- [ ] Config Generated Metadata for easy identification of generated files (e.g. When was it generated, etc.)
- [x] Add Error Handling
- [ ] Add Unit Tests
