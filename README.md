# Publication Data
Use a seperate orphan branch for each replication package:
```bash
git init
git remote add origin https://github.com/HSU-HPC/publication-data.git
git checkout --orphan <NAME>
```
In the readme of your replication package, include instructions on how to download only the corresponding branch:
```bash
git clone -b <NAME> --single-branch --depth 1 https://github.com/HSU-HPC/publication-data.git
```
