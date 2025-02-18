import logging

from github import Auth, Github, GithubException
from hata import Client, ClientWrapper
from hata.ext.slash import abort

from ..constants import GITHUB_TOKEN

ALL = ClientWrapper()

GITHUB = Github(auth=Auth.Token(GITHUB_TOKEN))
ORG = GITHUB.get_organization("voxel51")
VOXEL51_REPOS = [r.full_name for r in ORG.get_repos(type="public")]


@ALL.interactions(is_global=True, wait_for_acknowledgement=True)
async ref_issue(client: Client, event: InteractionEvent, query: ("str", "Topic to search"), repo: ("str", "Repo to search.")):  # type: ignore # noqa: F722
    """Returns list of top-five related issues from Voxel51 repository based on user query."""
    if repo is not None and repo not in VOXEL51_REPOS:
        abort("Must be Voxel51 repo.")
    elif repo is None:
        repo = "voxel51/fiftyone"  # default
    
    try:
        issues = GITHUB.search_issues(f"{query} repo:{repo} in:title,body is:issue")
        
        if issues.totalCount == 0:
            return await client.message_create(event.channel, "No relevant issues found.")
        
        issue_links = "\n".join(f"{issue.title}: {issue.html_url}" for issue in issues[:5])
        await client.message_create(event.channel, f"Top relevant issues:\n{issue_links}")
    
    except GithubException as e:
        logging.error(f"GitHub API error: {e}")
        await client.message_create(event.channel, "An error occurred while searching for issues. Please try again later.")


@ref_issue.autocomplete("repo")
async def repo_autocomplete(value):
    if not value:
        return VOXEL51_REPOS
    value_lower = value.lower()
    return [repo for repo in VOXEL51_REPOS if repo.startswith(value_lower)]
