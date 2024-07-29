# Contributing Guidelines

This document outlines how you can contribute

## Branch Naming Convention

Please follow this naming convention for your branches:

- Feature branches: `feature/<feature-name>`
- Bugfix branches: `bugfix/<bugfix-name>`
- Patch branches: `patch/<patch-name>`
- Hotfix branches: `hotfix/<hotfix-name>`
- General branches: `general/<general-name>`
- Documentation branches: `doc/<documentation-name>`
- Test branches: `test/<test-name>`

Replace `<feature-name>`, `<bugfix-name>`, `patch/<patch-name>`, `<hotfix-name>`, `<general-name>`, `<documentation-name>`, or `<test-name>` with a short description.

## Protected Branches

- `master` - Used as the production branch **Use quash and merge**
- `staging` - Used as the pre-production branch  **Use squash and merge**

### Here are some rules to follow about protected branches

1. All tests **must** pass before merging into protected branches.
2. Before merging, a review from someone other than the one pushing must pass.
3. **Only hotfixes** are allowed to be directly merged into `master`.
4. All commits to staging, no matter the size, **must** increment the build version.

## Pull Requests

Please follow these steps for creating a pull request:

1. Update local packages
2. Create a branch from `staging` with proper name formatting.
3. If code you added changes previous functionality, update documentation.
4. Keep commits appropriate and on topic of what you're pushing.
5. Make sure your code passes linting and CodeQL
6. Make sure your PR is merging into the correct branch.
7. After the PR is merged, delete the branch to keep the repository clean.
