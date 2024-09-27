from unittest import mock
from src.gitlab_api import get_merge_request, filter_stale_branches, filter_stale_merge_requests


@mock.patch('requests.get', autospec=True)
def test_branches_and_mrs(mock_get):
    mock_branches_response = mock.Mock()
    mock_branches_response.json.return_value = [
        {
            "name": "branch1",
            "web_url": "https://gitlab.hotmail.net/sst/mrclean/-/tree/feature/GRYP-11364_setup_stale_mr",
            "commit": {
                "created_at": "2023-09-12T08:11:03.000+01:00",
                "committer_email": "kevin@hotmail.com",
            },
        },
        {
            "name": "branch2",
            "web_url": "https://gitlab.net/sst/mrclean/-/tree/feature/setup_stale_mr",
            "commit": {
                "created_at": "2024-01-12T08:11:03.000+01:00",
                "committer_email": "kevin@hotmail.com",
            },
        },
    ]
    mock_branches_response.status_code = 200

    mock_mrs_response = mock.Mock()
    mock_mrs_response.json.return_value = [
        {
            "source_branch": "mr1",
            "web_url": "https://gitlab.net/sst/mrclean/-/merge_requests/1",
            "updated_at": "2024-03-09T08:56:04.501Z",
            "author": {
                "username": "kevin@hotmail.com",
            },
        },
        {
            "source_branch": "mr2",
            "web_url": "https://gitlab.net/sst/mrclean/-/merge_requests/2",
            "updated_at": "2024-01-09T08:56:04.501Z",
            "author": {
                "username": "kevin@hotmail.com",
            },
        },
    ]
    mock_mrs_response.status_code = 200

    def side_effect(url, *args, **kwargs):
        if "repository/branches" in url:
            return mock_branches_response
        elif "merge_requests" in url:
            return mock_mrs_response
        return None

    mock_get.side_effect = side_effect

    result = get_merge_request(3861, dry_run = True, ci_default_branch = "main")

    assert result is not None


def test_filter_stale_branches():
    branches = [
        {
            'name': 'feature-branch-1',
            'commit': {
                'created_at': "2023-09-12T08:11:03.000+01:00",
                'committer_email': 'kevin@hotmail.com'
            },
            'web_url': 'https://gitlab.example.com/project/branch1'
        },
        {
            'name': 'feature-branch-2',
            'commit': {
                'created_at': "2023-09-12T08:11:03.000+01:00",
                'committer_email': 'kevin@hotmail.com'
            },
            'web_url': 'https://gitlab.example.com/project/branch2'
        },
        {
            'name': 'main',
            'commit': {
                'created_at': "2024-01-12T08:11:03.000+01:00",
                'committer_email': 'kevin@hotmail.com'
            },
            'web_url': 'https://gitlab.example.com/project/main'
        },
    ]
    ci_default_branch = 'main'

    stale_branches = filter_stale_branches(branches, ci_default_branch)

    assert len(stale_branches) == 2
    assert stale_branches[0]['name'] == 'feature-branch-1'
    assert stale_branches[0]['committer_email'] == 'kevin@hotmail.com'
    assert stale_branches[0]['project_url'] == 'https://gitlab.example.com/project/branch1'

def test_filter_stale_mrs():
    mrs = [
        {
            "source_branch": "mr1",
            "web_url": "https://gitlab.hotmail.net/sst/mrclean/-/merge_requests/1",
            "updated_at": "2024-01-09T08:56:04.501Z",
            "author": {
                "username": "kevin@hotmail.com",
            },
        },
        {
            "source_branch": "mr2",
            "web_url": "https://gitlab.hotmail.net/sst/mrclean/-/merge_requests/2",
            "updated_at": "2024-01-09T08:56:04.501Z",
            "author": {
                "username": "kevin@hotmail.com",
            },
        },
    ]

    stale_mrs = filter_stale_merge_requests(mrs, dry_run=False)

    assert len(stale_mrs) == 2
    assert stale_mrs[0]['source_branch'] == 'mr1'
    assert stale_mrs[0]['username'] == 'kevin@hotmail.com'
    assert stale_mrs[0]['project_url'] == 'https://gitlab.hotmail.net/sst/mrclean/-/merge_requests/1'

