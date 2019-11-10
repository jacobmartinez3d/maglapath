### Python str wrapper for resolving tokenized paths.

#### Why:

Hard-coded paths in your code is bad. Particularly for corss-platform Windows-Linux pipelines.
#### How:

Paths are instead externalized to a json where, the keys in the json act as the token-names. Maglapath will recursively resolve tokenized paths by choosing the os-specific path you define in the json.

### A token can be described in the following form:

OS-Specific: In this form the current OS's native path separator will be used.

    ```
    <token_name>
    ```

Forced-forward-slash: For situations when you need paths to be resolved with forward-slashes even on Windows (Nuke, Touch Designer)

    ```
    </token_name>
    ```
