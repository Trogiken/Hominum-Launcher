# Hominum-Updater

![Pylint](https://github.com/Trogiken/Hominum-Updater/actions/workflows/pylint.yml/badge.svg)
[![CodeQL](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Trogiken/Hominum-Updater/actions/workflows/github-code-scanning/codeql)

Manage client game configurations remotely, securely, and autonomously

## Remote Configuration

This yaml file lives on a private repository where it serves as the control for clients

:heavy_plus_sign: The key's values **can** extended

:heavy_minus_sign: The key's values **cannot** be extended

### startup :heavy_minus_sign:

* server_ip `server.com, x.x.x.x` - The Ip address of the server. Used for auto join functionality

* game `vanilla, fabric, quilt, forge` - The corresponding key in the _games_ section. This determines the game type used

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

### paths :heavy_plus_sign:

```yaml
paths:
  sync/config:
    is_dir: True
    exclude: []
    delete_others: True
    root: "config"
    overwrite: False
  sync/mods:
    is_dir: True
    exclude: []
    delete_others: True
    root: "mods"
    overwrite: False
  sync/resourcepacks:
    is_dir: True
    exclude: []
    delete_others: False
    root: "resourcepacks"
    overwrite: False
  sync/shaderpacks:
    is_dir: True
    exclude: []
    delete_others: False
    root: "shaderpacks"
    overwrite: False
  sync/options.txt:
    is_dir: False
    root: "options.txt"
    overwrite: False
  sync/servers.dat:
    is_dir: False
    root: "servers.dat"
    overwrite: True
```

### altnames :heavy_plus_sign:

```yaml
altnames:
  "Lilyotv4642": "Not Lesbian"
  "wasntMe_guy": "Biddie Nom"
```

### bulletin :heavy_plus_sign:

```yaml
bulletin:
  column_0:
    "Server Info": ["Ip Address: hominum.mcserver.us", "Version: 1.20.1", "Forge: 47.3.0"]
  column_1:
    "Content Update": ["Slight Difficuly Tweak - See new mod info in updated wiki PDF on discord"]
```
