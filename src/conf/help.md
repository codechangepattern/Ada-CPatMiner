# Settings configuration

In order to run the _Ada Change Pattern Miner_, you need to configure the `settings.json` file in this directory.
Here are detailed explanations of the settings:

### Settings for the _collect-cgs_ mode:

| Name                               | Description                                                                                                                 |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **git_repositories_dir**           | Path to the directory with Git repositories.                                                                                |                                   
| **traverse_file_max_line_count**   | The maximum number of lines in the analyzed files (processing larger files may sometimes cause memory issues).              |               
| **traverse_async**                 | **true** for the asynchronous processing of repositories (**recommended**).                                                 |                    
| **traverse_min_date**              | **(optional)** the date in the **%d.%m%.Y** format, no changes older than this date will be processed.                      |                      
| **change_graphs_storage_dir**      | Path to the output dir for change patterns.                                                                                 |
| **change_graphs_storage_interval** | Batch size of the number of change graphs to be saved in a single pickle file (to prevent the files from becoming too big). |
| **traverse_max_commits**           | Maximum number of commits to traverse for each Git repository.                                                              |

### Settings for the _patterns_ mode:

| Name                        | Description                                                           |
|-----------------------------|-----------------------------------------------------------------------|
| **patterns_output_dir**     | Path to the output directory                                          |
| **patterns_output_details** | **true** for saving a JSON for each pattern instance with its details |

### Additional settings:

| Name | Description |
|------|-------------|
|      |             |