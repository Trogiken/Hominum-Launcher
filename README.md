# Hominum-Launcher

![Pylint](https://github.com/Trogiken/Hominum-Updater/actions/workflows/pylint.yml/badge.svg)
[![CodeQL](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql)

Manage client game configurations remotely, securely, and autonomously

## Remote Configuration

This yaml file lives on a private repository where it serves as the control for clients

:heavy_plus_sign: The key's values **can** extended

:heavy_minus_sign: The key's values **cannot** be extended

### startup :heavy_minus_sign:

* server_ip `server.com, x.x.x.x, "", ~` - The Ip address of the server. Used for auto join functionality.
If falsy value used, the auto join feature will be disabled

* server_port `22567, ~` - The port address of the server. Used for auto join functionality. Default is 25565

* game `vanilla, fabric, quilt, forge, neoforge` - The corresponding key in the _games_ section. This determines the game type used

#### Startup Example

```yaml
startup:
  server_ip: "1.1.1.1"
  server_port: 25565
  game: "forge"
```

### games :heavy_minus_sign:

* vanilla - Vanilla Game Type
  * mc_version `"", ~, "x.x.x"` - The version of minecraft. Latest is default

* fabric - Fabric Game Type
  * mc_version `"", ~, "x.x.x"` - The version of minecraft. Latest is default
  * loader_version `"", ~, "x.x.x"` - The version of the fabric loader. Latest is default

* quilt - Quilt Game Type
  * mc_version `"", ~, "x.x.x"` - The version of minecraft. Latest is default
  * loader_version `"", ~, "x.x.x"` - The version of the fabric loader (Uses same loader as fabric). Latest is default

* forge - Forge Game Type
  * mc_version `"", ~, "x.x.x"` - The version of minecraft. If this is null, forge version will be force to be recommended
  * forge_version `"", ~, "x.x.x", recommended, latest` - The version of forge. Recommended is default

* neoforge - Neoforge Game Type
  * mc_version `"", ~, "x.x.x"` - The version of minecraft

#### Games Example

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

### paths :heavy_plus_sign:

* `path/to/remote/directory` - The relative url path to the directory to sync
  * is_dir `True, False` - Is the path a directory
  * exclude `[path/to/remote/dir, path/to/remote/file]` - Relative url paths to exclude from syncing
  * delete_others `True, False` - Delete any other file in the local directory that's not on the remote (Obeys the exclude paths)
  * root `ExampleLocalDirName` - The directory path that will be stored locally. This is stored in the game data folder
  * overwrite `True, False` - If a local path matches a remote path, should the local file be overwritten
* `path/to/remote/file` - The relative url path to the file to sync
  * is_dir `True, False` - Is the path a directory
  * root `ExampleFileName` - The file path that will be stored locally. This is stored in the game data folder
  * overwrite `True, False` - If a local path matches a remote path, should the local file be overwritten

#### Paths Example

```yaml
paths:
  sync/config:
    is_dir: True
    exclude: ["config/modconfig/dir"]
    delete_others: True
    root: "config"
    overwrite: False
  sync/options.txt:
    is_dir: False
    root: "options.txt"
    overwrite: False
```

### altnames :heavy_plus_sign:

Spoofs the players username to a alternate name in the launcher. To disable this feature set the key as follows: `altnames: ~`

#### Altnames Example

```yaml
altnames:
  "UsernameOfPlayer": "NewUsernameOfPlayer"
```

### bulletin :heavy_plus_sign:

Creates the layout and information to display in the bulletin

#### Bulletin Example

```yaml
bulletin:
  column_0:
    "Example Section": ["Line 1", "Line 2", "..."]
  column_1:
    "Example Section 1": ["Line 1", "Line 2"]
    "Example Section 2": ["Line 1", "Line 2"]
```
