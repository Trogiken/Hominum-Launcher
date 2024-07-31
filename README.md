# Hominum-Launcher

![Pylint](https://github.com/Trogiken/Hominum-Updater/actions/workflows/pylint.yml/badge.svg)
[![CodeQL](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql)

Manage client game configurations remotely, securely, and autonomously.

## Table of Contents

1. [Remote Configuration](#remote-configuration)
2. [Startup](#startup)
3. [Games](#games)
4. [Paths](#paths)
5. [Altnames](#altnames)
6. [Bulletin](#bulletin)

## Remote Configuration

This YAML file lives on a private repository where it serves as the control for clients.

:heavy_plus_sign: The key's values **can** be extended.

:heavy_minus_sign: The key's values **cannot** be extended.

## Startup

- **server_ip**: The IP address of the server. Used for auto-join functionality. If a falsy value is used, the auto-join feature will be disabled.
  - Data type: `string`
  - Allowed values: `server.com`, `x.x.x.x`, `""`, `~`
- **server_port**: The port address of the server. Used for auto-join functionality. Default is 25565.
  - Data type: `integer`
  - Allowed values: `22567`, `~`
- **game**: The corresponding key in the _games_ section. This determines the game type used.
  - Data type: `string`
  - Allowed values: `vanilla`, `fabric`, `quilt`, `forge`, `neoforge`

```yaml
startup:
  server_ip: "1.1.1.1"
  server_port: 25565
  game: "forge"
```

## Games

- **vanilla** - Vanilla Game Type
  - **mc_version**: The version of Minecraft. Latest is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
- **fabric** -  Fabric Game Type
  - **mc_version**: The version of Minecraft. Latest is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
  - **loader_version**: The version of the Fabric loader. Latest is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
- **quilt** - Quilt Game Type
  - **mc_version**: The version of Minecraft. Latest is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
  - **loader_version**: The version of the Fabric loader (uses the same loader as Fabric). Latest is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
- **forge** - Forge Game Type
  - **mc_version**: The version of Minecraft. If this is null, the Forge version will be forced to be recommended.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`
  - **forge_version**: The version of Forge. Recommended is default.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x", recommended, latest`
- **neoforge** - Neoforge Game Type
  - **mc_version**: The version of Minecraft.
    - Data type: string
    - Allowed values: `"", ~, "x.x.x"`

```yaml
games:
  vanilla:
    mc_version: "1.20.1"
  fabric:
    mc_version: "1.20.6"
    loader_version: "0.16.0"
  quilt:
    mc_version: "1.20.6"
    loader_version: ~
  forge:
    mc_version: "1.20.1"
    forge_version: "47.3.0"
  neoforge:
    mc_version: "1.20.1"
```

## Paths

- **path/to/remote/directory** - The relative URL path to the directory to sync
  - **is_dir**: Is the path a directory?
    - Data type: boolean
    - Allowed values: `True, False`
  - **exclude**: Relative URL paths to exclude from syncing.
    - Data type: array of strings
    - Allowed values: `[path/to/remote/dir, path/to/remote/file]`
  - **delete_others**: Delete any other file in the local directory that's not on the remote (obeys the exclude paths).
    - Data type: boolean
    - Allowed values: `True, False`
  - **root**: The directory path that will be stored locally. This is stored in the game data folder.
    - Data type: string
    - Allowed values: `relative/datafolder/path/to/folder/location`
  - **overwrite**: If a local path matches a remote path, should the local file be overwritten?
    - Data type: boolean
    - Allowed values: `True, False`
- **path/to/remote/file**- The relative URL path to the file to sync
  - is_dir: Is the path a directory?
    - Data type: boolean
    - Allowed values: `True, False`
  - root: The file path that will be stored locally. This is stored in the game data folder.
    - Data type: string
    - Allowed values: `relative/datafolder/path/to/file/location`
  - overwrite: If a local path matches a remote path, should the local file be overwritten?
    - Data type: boolean
    - Allowed values: `True, False`

```yaml
paths:
  sync/config:
    is_dir: True
    exclude: ["config/modconfig/dir"]
    delete_others: True
    root: "config"  # This is placed in the root of the game data folder
    overwrite: False
  sync/options.txt:
    is_dir: False
    root: "options.txt"  # This is placed in the root of the game data folder
    overwrite: False
```

## Altnames

Spoofs the player's username to an alternate name in the launcher.
To disable this feature, set the key as follows: `altnames: ~`

```yaml
altnames:
  "UsernameOfPlayer": "NewUsernameOfPlayer"
```

## Bulletin

Creates the layout and information to display in the bulletin.
To disable this feature, set the key as follows: `bulletin: ~`

```yaml
bulletin:
  column_0:
    "Example Section": ["Line 1", "Line 2", "..."]
  column_1:
    "Example Section 1": ["Line 1", "Line 2"]
    "Example Section 2": ["Line 1", "Line 2"]
```
