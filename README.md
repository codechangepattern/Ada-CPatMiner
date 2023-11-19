# Ada-CPatMiner


## Tool
### Getting started (Linux instructions)

0. The tool requires Python 3.9 or 3.10 to run. We have tested it only on Linux and Windows systems.
```
sudo apt install python3 python3-pip
```
1. Clone this repository
```shell script
git clone https://github.com/codechangepattern/Ada-CPatMiner.git && cd Ada-CPatMiner
```
2. Install the required dependencies:
    * Most dependencies of Ada-CPatMiner are easily installed by using the requirements.txt:
    ```shell script
    pip3 install -r requirements.txt
    ```
    * GraphViz is required to generate PDF files for flow and change graphs:
    ```
    sudo apt install graphviz
    ```
    * Libadalang (install using alire):
        * Install gnat and gprbuild
        ```
        sudo apt install gnat gprbuild
        ```
        * Installing [ALIRE](https://alire.ada.dev/)
           * Download [ALIRE](https://github.com/alire-project/alire/releases/download/v1.2.2/alr-1.2.2-bin-x86_64-linux.zip)
           * Extract alr-1.2.2-bin-x86_64-linux.zip
           * Copy alr to `/usr/local/bin`:
           ```
           sudo cp /alr-1.2.2-bin-x86_64-linux/bin/alr  /usr/local/bin/alr
           ```
        * Download, build, and install libadalang and its dependencies:
        ```shell script
        alr get libadalang
        ```
        ```shell script
        cd libadalang_23.0.0_f27a5d00
        ```
        Open the alire.toml file and add the following line below [[depends-on]]
        ```shell script
        gnat_native = "12.2.1"
        ```
        Build libadalang:
        ```shell script
        alr build
        ```
        Install the shared object libraries:
        ```shell script
        sudo find . -type f,l -name "*.so" -exec cp "{}" /usr/local/lib \;
        ```
        Add /usr/local/lib to your path environment:
        ```shell script
        sudo vim /etc/environment
        ```
        Configure dynamic linker run-time bindings:
        ```shell script
        sudo ldconfig
        ```
        ```
        cd python
        pip3 install .
        ```
        Now run test_libadalang_installation.py to verify that the libadalang installation has been successful:
        ```shell script
        python3 test_libadalang_installation.py
        ```
3. Configure the settings file

### Repositories

Ada-CPatMiner comes with a collection of 82 Ada repositories with over 1.000 commits each;
this collection is found in ```src/conf/repositories.json```. We also provide a list of 46 Ada repositories, each ranging between 500 and 1.000 commits;
this collection is found in ```src/conf/test_repositories.json```. We provide the ```src/clone_repositories.py``` script to automate the cloning process.
This script clones the top 50 repositories (based on stars) by default. To indicate where these projects should be cloned, configure the ```git_repositories_dir``` in the ```src/conf/settings.json``` file.
For example:

```json
{
   ...
   "git_repositories_dir": "/home/username/repos"
   ...
}
```

After configuring the repositories folder, run the following command to clone the top 50 repositories:

```shell script
python3 src/clone_repositories.py
```

### How to use
You can run any step of the pipeline by using the following command:
```
python3 src/main.py <mode> <args>
```
Ada-CPatMiner currently supports four operation modes:
1. `afg` — build a program dependence graph from the Ada source.
   Arguments
   * `-i` — path to the source file.
   * `-o` — path to the output file; two files are created, a DOT graph file and a graphviz-generated PDF file.
   * `--no-closure` — **(optional)** no closure will be built for the graph.
   * `--show-deps` — **(optional)** edges with type dep will be present in the graph, indicating the dependence of the vertices on each other.
   * `--hide-op-kinds` — **(optional)** hide operation types.
   * `--show-data-keys` — **(optional)** show variable IDs.
   Typical use:
   ```
   python3 src/main.py afg -i src/examples/example.adb -o images/afg.dot
   ```
2. `cg` — build a change graph from two source files (before and after changes).
   Arguments:
   * `-s` — path to the source file before changes.
   * `-d` — path to the source file after changes.
   * `-o` — path to the output file; two files are created, a DOT graph file and a graphviz-generated PDF file.
   Typical use:
   ```
   python3 src/main.py cg -s src/examples/0_old.adb -d src/examples/0_new.adb -o images/cg.dot
   ```
3. `collect-cgs` — mine change graphs from local repositories.
   All general settings for this mode are located in the configuration JSON file (see part 3 of **Getting started**.
   Use:
   ```
   python3 src/main.py collect-cgs
   ```
4. `patterns` — search for patterns in the generated change graphs.
   All general settings for this mode are located in the configuration JSON file (see part 3 of **Getting started**.
   
   Use:
   ```
   python3 src/main.py patterns
   ```

## Data

In the data folder, there are two files:
- "repositories.pdf" file contains the list of the 50 repositories analyzed in the paper. 
- "patterns-depth-corpus.tar.gz" file contains the discovered patterns. The generated PDF files have been removed to decrease the overall size, but they could be regenerated from the DOT files.
