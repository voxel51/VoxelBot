import logging

from github import Auth, Github, GithubException
from github.Issue import Issue
from github.Organization import Organization
from github.PaginatedList import PaginatedList
from hata import Client, ClientWrapper, InteractionEvent
from hata.ext.slash import abort

from ..constants import GITHUB_TOKEN

ALL = ClientWrapper()

GITHUB = Github(auth=Auth.Token(GITHUB_TOKEN))
ORG: Organization = GITHUB.get_organization("voxel51")
VOXEL51_REPOS: list[str] = [r.full_name for r in ORG.get_repos(type="public")]


@ALL.interactions(is_global=True, wait_for_acknowledgement=True)
async def ref_issue(
    client: Client,
    event: InteractionEvent,
    query: ("str", "Topic to search"),  # type: ignore # noqa: F722
    repo: ("str", "Repo to search."),  # type: ignore # noqa: F722
):
    """
    Returns a list of top-five related issues from a specified Voxel51 repository based on the
    user's query.

    Args:
        client (Client): The client instance to use for sending messages.
        event (InteractionEvent): The interaction event that triggered this function.
        query (str): The topic to search for in the issues.
        repo (str): The repository to search within.

    Raises:
        GithubException: If there is an error with the GitHub API request.
    """
    if repo not in VOXEL51_REPOS:
        abort("Must be Voxel51 repo.")

    try:
        issues: PaginatedList[Issue] = GITHUB.search_issues(
            f"{query} repo:{repo} in:title,body is:issue"
        )

        if issues.totalCount == 0:
            return await client.message_create(event.channel, "No relevant issues found.")

        issue_links: str = "\n".join(f"{issue.title}: {issue.html_url}" for issue in issues[:5])
        await client.message_create(event.channel, f"Top relevant issues:\n{issue_links}")

    except GithubException as e:
        logging.error(f"GitHub API error: {e}")
        await client.message_create(
            event.channel, "An error occurred while searching for issues. Please try again later."
        )


@ref_issue.autocomplete("repo")
async def repo_autocomplete(value) -> list[str]:
    """
    Provides autocomplete suggestions for repository names.

    This function is triggered by the `ref_issue.autocomplete` decorator with the
    argument "repo". It returns a list of repository names that match the given
    input value. If no value is provided, it returns the full list of repositories.

    Args:
        value (str): The input value to match against repository names.

    Returns:
        list[str]: A list of repository names that start with the input value.
    """
    if not value:
        return VOXEL51_REPOS
    value_lower: str = value.lower()
    return [repo for repo in VOXEL51_REPOS if repo.startswith(value_lower)]
