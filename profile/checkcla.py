import os
import re
import requests
from github import Github

CLA_FILE = "CLA.md"
CLA_LABEL_NAME = "cla-signed"
CHECKCLA_COMMENT = "checkcla"  # The text of the comment that triggers the CLA check.

def get_contributors(repo):
    """Return a list of contributors to the repo."""
    contributors = set()
    for contributor in repo.get_contributors():
        contributors.add(contributor.login)
    return contributors

def get_cla_text(repo):
    """Return the text of the CLA file."""
    contents = repo.get_contents(CLA_FILE)
    return contents.decoded_content.decode()

def get_signed_contributors(repo):
    """Return a set of contributors who have signed the CLA."""
    signed_contributors = set()
    for issue in repo.get_issues(state="all", labels=[CLA_LABEL_NAME]):
        # Check that the issue is the CLA issue and not a duplicate.
        if issue.number == CLA_ISSUE_NUMBER:
            for comment in issue.get_comments():
                signed_contributors.add(comment.user.login)
    return signed_contributors

def check_cla(repo):
    """Check that all contributors have signed the CLA."""
    contributors = get_contributors(repo)
    signed_contributors = get_signed_contributors(repo)
    cla_text = get_cla_text(repo)
    for contributor in contributors - signed_contributors:
        if contributor == os.environ["GITHUB_ACTOR"]:
            print(f"Error: {contributor} has not signed the CLA.")
            print(f"Please sign the CLA in {CLA_FILE} and comment on issue #{CLA_ISSUE_NUMBER}.")
            exit(1)
    print("All contributors have signed the CLA.")

if __name__ == "__main__":
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])
    event_type = os.environ["GITHUB_EVENT_NAME"]
    
    if event_type == "issue_comment":
        comment_text = os.environ["GITHUB_COMMENT_BODY"]
        if comment_text.strip().lower() == CHECKCLA_COMMENT.lower():
            check_cla(repo)
