#!/usr/bin/python3

import requests
import sys
import os
import subprocess
from requests.auth import HTTPBasicAuth
'''
argv[1] => github_user
argv[2] => github_user_token
argv[3] => github_org
'''
if len(sys.argv) < 4:
    raise Exception("To few arguments")
if len(sys.argv) > 4:
    raise Exception("To many arguments")

response = requests.get("https://api.github.com/orgs/" +
                        sys.argv[3]+"/repos?type=forked", auth=HTTPBasicAuth(sys.argv[1], sys.argv[2]), headers={"accept": "application/vnd.github.v3+json"})

repos = {}
for repo in response.json():
    try:
        repo_info = requests.get("https://api.github.com/repos/"+sys.argv[3]+"/"+repo["name"], auth=HTTPBasicAuth(sys.argv[1], sys.argv[2]),  headers={
            "accept": "application/vnd.github.v3+json"}).json()

        repos[repo["name"]] = {"owner": repo_info["parent"]["owner"]
                               ["login"], "url": repo_info["parent"]["html_url"], "branch": repo_info["parent"]["default_branch"]}
        current_repo = repos[repo["name"]]

        if not os.path.exists('./'+repo["name"]):
            subprocess.call(["git", "clone", "https://"+sys.argv[1].replace('@', '%40')+":" +
                            sys.argv[2]+"@github.com/" + sys.argv[3] + "/" + repo["name"]], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        os.chdir('./'+repo["name"])
        subprocess.call(["git", "pull", "https://"+sys.argv[1].replace('@', '%40') +
                        ":"+sys.argv[2]+"@"+current_repo["url"].replace("https://", ""), current_repo["branch"]], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.call(["git", "push", "https://" + sys.argv[1].replace('@', '%40') +
                        ":"+sys.argv[2]+"@github.com/"+sys.argv[3]+"/" + repo["name"]], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        os.chdir('..')
        print("\U00002705 "+sys.argv[3]+"/"+repo["name"] + " has been updated with upstream " +
              current_repo["url"], end="\n")

    except(Exception):
        print("\U0000274C "+sys.argv[3]+"/"+repo["name"] + " has not been updated with upstream " +
              current_repo["url"], end="\n")
