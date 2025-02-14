import logging

from github import Auth, Github
from hata import Client, ClientWrapper
from hata.ext.slash import abort

from ..constants import GITHUB_TOKEN

ALL = ClientWrapper()

GITHUB = Github(auth=Auth.Token(GITHUB_TOKEN))
VOXEL51_REPOS = [r.name for r in GITHUB.get_repos(type="public")]


@ALL.interactions(is_global=True, wait_for_acknowledgement=True)
async def ref_issue(client, event, query: ("str", "Topic to search"), repo: ("str", "Repo to search.")):  # type: ignore # noqa: F722
    """Provides specific metric(s) for the voxel51/fiftyone repository."""
    if repo not in (VOXEL51_REPOS):
        abort("Must be Voxel51 repo.")
    
    GITHUB.get_repo(repo)
    issues = repo.search_issues(f'{query} in:title,body')
    
    if issues.totalCount == 0:
            return await client.message_create(message.channel, "No relevant issues found.")
    
    issue_links = "\n".join(f"{issue.title}: {issue.html_url}" for issue in issues[:5])
    await client.message_create(event.channel, f"Top relevant issues:\n{issue_links}")
    
    except GithubException as e:
        logging.error(f"GitHub API error: {e}")
        await client.message_create(event.channel, "An error occurred while searching for issues. Please try again later.")


@repo_metrics.autocomplete("repo")
async def repo_autocomplete(value):
    if not value:
        return VOXEL51_REPOS
    value_lower = value.lower()
    return [repo for repo in VOXEL51_REPOS if repo.startswith(value_lower)]
