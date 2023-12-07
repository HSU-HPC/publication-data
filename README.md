# Replication Packages
Use a seperate orphan branch for each replication package:
```bash
git init
git remote add origin https://github.com/HSU-HPC/replication-packages.git
git checkout --orphan <NAME>
```
In the readme of your replication package, include instructions on how to download only the relevant branch:
```bash
git clone -b <NAME> --single-branch https://github.com/HSU-HPC/replication-packages.git
```
