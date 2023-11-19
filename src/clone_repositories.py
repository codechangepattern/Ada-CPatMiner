from itertools import islice
import json
import os.path
import settings
from git import Repo

def clone():
    with open('./src/conf/repositories.json') as f:
        repositories = json.load(f)
    top_50 = list(islice(repositories, 50))
    for repository in top_50:
        if not os.path.exists(os.path.join(settings.get('git_repositories_dir'), repositories[repository]['name'])):
            Repo.clone_from(f'https://github.com/{repository}.git', os.path.join(settings.get('git_repositories_dir'), repositories[repository]['name']))

if __name__ == '__main__':
    clone()