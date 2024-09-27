import argparse
import sys
from datetime import datetime, timezone
import requests
from dateutil.relativedelta import relativedelta
import logging
from . import settings




logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
six_months_ago = current_time - relativedelta(months=6) # Set to whichever limit you would want.
three_months_ago = current_time - relativedelta(months=3) # Set to whichever limit you would want.


HEADERS = {
    'PRIVATE-TOKEN': settings.PRIVATE_TOKEN,
    "Accept": "application/json"
}
SST_DEV_EMAIL = '' # Some repositories have bump2version implemented and will have an automatic email set up to push changes in order to suffice on gitlab, remove this and wherever its used if not needed.


def get_gitlab_data(endpoint):
    response = requests.get(endpoint, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def filter_stale_branches(branches, ci_default_branch, **kwargs):
    stale_branches = []
    for branch in branches:
        commit_time = datetime.strptime(branch.get('commit').get('created_at'), '%Y-%m-%dT%H:%M:%S.%f%z')
        if (commit_time <= six_months_ago and
                branch['name'] != ci_default_branch and
                branch['commit'].get('committer_email') != SST_DEV_EMAIL):
            stale_branches.append({
                'name': branch['name'],
                'committer_email': branch['commit'].get('committer_email'),
                'project_url': branch.get('web_url'),
            })
    return stale_branches


def filter_stale_merge_requests(merge_requests, dry_run=False):
    stale_mrs = []
    for mr in merge_requests:
        updated_at = datetime.strptime(mr.get('updated_at'), '%Y-%m-%dT%H:%M:%S.%f%z')
        if updated_at <= three_months_ago and not mr.get('has_conflicts'):
            stale_mrs.append({
                'source_branch': mr.get('source_branch'),
                'username': mr.get('author').get('username'),
                'project_url': mr.get('web_url'),
            })
    if dry_run:
        return log_stale_items(stale_mrs, "Merge Request", dry_run)
    return stale_mrs


def send_awareness(branch_type, branch, user, project_url, dry_run):
    if dry_run:
        logger.debug(f'this is a dry run for  \n{user}, {branch_type}, {branch} {project_url} ')
        return "Dry run successful"
    url = f"<your_url_for_endpoint_here>/{user}" # Alter the endpoint however needed to reach your endpoint which sends an email/msg through your slack or chatting app.
    payload = (f"\n\n\n:mrclean: Hello, :wave: Mr Clean here!\n\n"
               f"- *{branch_type}*: {branch}\n"
               f"- *URL*: {project_url}\n"
               f"- *Reason*: Stale {branch_type}, needs immediate action! \n\n"
        "Please finish what you need to or remove the branch. In 7 days it will be removed unless you add a new commit."
    )

    try:
        requests.post(url, data=payload)
    except Exception:
        return "Request made to retrieve branch/mr's has been unsuccessful"


def log_stale_items(stale_items, branch_type, dry_run):
    if dry_run:
        if stale_items != []:
            logger.debug('')
            logger.debug('!=======!')
            logger.debug(f'Found {branch_type} to be terminated!')
            logger.debug('!=======!')
            logger.debug(
                f'The activity on {branch_type} below are stale. Owners have been alerted')

            for item in stale_items:
                get_branch = f"{branch_type} '{item.get('name' if branch_type == 'Branches' else 'source_branch')}'"
                get_user = f"{item.get('committer_email' if branch_type == 'Branches' else 'username')}"
                get_url = f"{item.get('project_url')}"
                logger.debug(
                    f"{get_branch} by "
                    f"{get_user}")
                send_awareness(get_branch, get_user, get_url, dry_run)
        else:
            logger.debug(f'No stale {branch_type}')
            logger.debug('**Sparkle** Theres no clean like MrClean **Sparkle**')

    if stale_items != []:
        logger.warning('')
        logger.warning('!=======!')
        logger.warning(f'Found {branch_type} to be terminated!')
        logger.warning('!=======!')
        logger.warning(
            f'The activity on {branch_type} below are stale. Owners have been alerted')

        for item in stale_items:
            get_branch_type = f"{branch_type}"
            get_branch = f"{item.get('name' if branch_type == 'Branches' else 'source_branch')}"
            get_user = f"{item.get('committer_email' if branch_type == 'Branches' else 'username')}"
            get_url = f"{item.get('project_url')}"
            logger.warning(
                f"{get_branch} by "
                f"{get_user}")
            send_awareness(get_branch_type, get_branch, get_user, get_url, dry_run=False)
    else:
        logger.warning(f'No stale {branch_type}')
        logger.warning('**Sparkle** Theres no clean like MrClean **Sparkle**')


def get_merge_request(ci_project_id, ci_default_branch, dry_run = False):
    GITLAB_API_BASE_URL = f"<your_gitlab_url_here_if_custom>/api/v4/projects/{ci_project_id}" # Change as needed for URL.
    branches = get_gitlab_data(f"{GITLAB_API_BASE_URL}/repository/branches")
    merge_requests = get_gitlab_data(f"{GITLAB_API_BASE_URL}/merge_requests?state=opened")

    stale_branches = filter_stale_branches(branches, ci_default_branch)
    stale_merge_requests = filter_stale_merge_requests(merge_requests)

    if dry_run:
        return "Dry run was successful"
    log_stale_items(stale_branches, "Branches", dry_run)
    log_stale_items(stale_merge_requests, "Merge Request", dry_run)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some arguments.")
    parser.add_argument("--ci_project_id", type=str, required=True, help="project id passed.")
    parser.add_argument("--ci_default_branch", type=str, required=False, help="getting default branch of repository")
    parser.add_argument("--dry_run", type=bool, required=False, help="perform a dry run")
    args = parser.parse_args()
    get_merge_request(args.ci_project_id, args.ci_default_branch, args.dry_run)