# MrClean

Implementation currently for Gitlab only.

This repository focuses on cleaning your repository from the stale branches and merge requests on your repository by 
alerting the user who owns the stale branches on slack via pmxbot.

It includes: 

- Grabbing stale branches from your repository up to 6 months
- Grabbing merge requests from your repository up to three months with no conflicts.


## How to implement it in your project

### Manual implementation on each different repo

To use MrClean you will need to implement the following code in your gitlab-ci.yml file like so:

``` yml
mrclean:
  stage: .pre
  image: <your_image_here_as_based_on_where_you_pushed_your_changes_of_mrclean>
  variables:
    PROJECT_ID: ${CI_PROJECT_ID}
  script:
    - python3 /app/src/gitlab_api.py --ci_project_id ${PROJECT_ID}
```

### Manual implementation on each different repo

How to integrate with your project

#### Step 1
###### ======

Navigate to your pulled and pushed MrClean repository

#### Step 2
###### ======

Now navigate to Build→ Pipeline schedules (current location for pipelines schedules gitlab updated).

#### Step 3
###### ======

Once presented with the scheduled jobs, click on the New schedule button.

#### Step 4
###### ======

Give your description a useful name, something which uses your projects name as this will help others know whose project is integrating MrClean as well as if the project has already been added.

Choose your custom interval pattern, I personally set MrClean check repositories every Friday morning. You can use https://crontab.guru/ to configure your custom pattern.

Use the target branch as main, this is the main branch of MrClean and not your projects.

Enter two new variables, one called *DEFAULT_BRANCH*, which takes your default branch of the project, and the second *PROJECT_ID*, which takes your projects ID. You can find these values in your projects overview.

Once done, hit the Save pipeline schedule

#### Step 5
###### ======

Verify MrClean works with your project by clicking the play button. Once the pipeline is ran (may need to refresh page after pressing play to see pipeline job running), check the logs and verify the job is running, and then check slack once the job is done to verify you received a message from pmxbot.


### Future additions to the MrClean project
#### Setup one message per project

~~The idea is to have one message per project, so that when pmxbot gives you all the stale branches/mrs, its done all as one message and not separate ones.~~ [x]

#### Setup automatic deletion

The idea is to have a script in MrClean to delete the stale branches/merge requests after 7days, this could be done by storing the stale branches/merge requests in a db or possibly retrieving the artifacts from the pipeline 7 days ago and checking if the branch/merge request still exists and then deleting it before running the check after the 7days expired. [ ]