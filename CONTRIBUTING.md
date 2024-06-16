# Contributing Guidelines

This document outlines how you can contribute

## Branch Naming Convention

Please follow this naming convention for your branches:

- Feature branches: `feature/<feature-name>`
- Bugfix branches: `bugfix/<bugfix-name>`
- Hotfix branches: `hotfix/<hotfix-name>`
- General branches: `general/<general-name>`
- Documentation branches: `doc/<documentation-name>`
- Test branches: `test/<test-name>`

Replace `<feature-name>`, `<bugfix-name>`, `<hotfix-name>`, `<general-name>`, `<documentation-name>`, or `<test-name>` with a short description.

## Protected Branches

- `master` - Used as the production branch
- `staging` - Used as the pre-production branch

### Here are some rules to follow about protected branches

1. All tests **must** pass before merging into protected branches.
2. Before merging, a review from someone other than the one pushing must pass.
3. **Only hotfixes** are allowed to be directly merged into `master`.

## Pull Requests

Please follow these steps for creating a pull request:

1. Create a branch from `staging` with proper name formatting **(Unless you're making a hotfix)**.
2. If code you added changes previous functionality, update documentation.
3. Keep commits appropriate and on topic of what you're pushing.
4. Make sure your code lints.
5. Make sure your code passes CodeQL.
6. Make sure your PR is merging into the correct branch.
7. After the PR is merged, delete the branch to keep the repository clean.

## Compiling a Release

Here are the steps to compiling a release:

**Increment build version** 

1. Make sure that you've checked out the `master` branch.
2. Make sure that all PRs are merged, tests are passing, and versions are updated.
3. Access and download the security program.
4. Within the security program, enter the API_KEY.
5. Run the module, selecting the `./Updater` directory in the repo.
6. Once finished, copy and store **locally** the password and salt.
7. Move the created `creds` file into `./Compile Info/include`.
8. In `./Updater/source/creds.py`, enter the local password and salt.
9. Run `auto-py-to-exe`, selecting the information in `./Compile Info`.
10. Double check all fields and then compile as a directory.
11. Store the resulting build directory somewhere other than the repo directory.
12. Delete all current changes in the local checked out `master` branch **(Nothing should be committed here)**.
13. Run `install creator`, using the resulting build directory as the source files.
14. Create a release on GitHub and upload the resulting installer.
