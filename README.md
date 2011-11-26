# Fabric Utilities #


Helpers for the Fabric deployment system for securely configuring servers.

Problem: you need to configure server applications 
through an automated script, but prefer to avoid passing sensitive passwords
directly through the command line. The
command line isn't guaranteed to be secure—passwords given as arguments may be saved to disk in the shell 
command history, appear to other logged-in users running `ps`, etc. 

Or you need to connect to a remote service (like source control) during deployment, but would rather not leave the passwords in plain text files on the server. If the server were ever compromised, the fewer sensitive passwords lying around in various places the better.

Solutions: `run_prompted` and `run_script`. (Along with two helpers, `sudo_put_data` and `put_data`).

## run_prompted ##

Extends Fabric's sudo prompt mechanism to many other types of
password prompts. You could use it to supply a root user password
while setting up or connecting to a database, or to supply a version control
system with a password for a remote source code repository.

### Usage ###

    run_prompted(command, password='', prompt='Password[^:]*: ', pty=True)

`prompt` gives a regular expression matching the remote prompt. Fabric
will add anchors to make it match an entire line.

If the `password` param is non-empty, use it as the password.
Otherwise prompt locally.

Returns the password (either default or user-entered), which the caller
can then supply as the password parameter to subsequent `run_prompted`
calls involving the same system.


### Caveat ###

The prompt displayed locally is the same as the one displayed
for sudo passwords ('Password for *username*@*host*:'), which may be
misleading. But attempting to customize it would be too hacky, even
for this function.


## run_script ##

Runs a (multi-line) string as a script on the server. The string could be
a shell script or some other type of content that can be run by an
an interpreter. This command saves the script as a temporary file on the server,
runs it, and deletes it afterwards.

Password prompts raised by the script, directly or indirectly, can be answered as in run_prompted above.

The advantage of using this command instead of passing the statements
to "run" (or of using "run" and "echo" to pipe them to a script runner)
is in security: they won't appear on the command line, so they won't
appear momentarily in "ps" and won't be recorded in bash history, both
helpful when including passwords. Also, there's less per-statement
overhead. Keep in mind that the script will be briefly saved to the server
(and since the filename is constant, this command can't be run twice
concurrently, not that it should normally be an issue).

### Usage ###

    run_script(script, runner=None, password=None, prompt=None, pty=False)

Upload the given script content and either pipe it into the given command
or, if no command is given, execute it directly (in this case, its shebang
line should provide the command).

If prompt is not empty, password prompts will be recognized and answered
as described for run_prompted.


## sudo_put_data ##

Creates a privileged file with data provided by a string.
(Fabric's regular put command requires a local file to upload.)

The file will first be created in the current home directory, then moved
into place with sudo, because the current user may not have sufficient
permissions for the regular 'put' command to place it there directly.

### Usage ###

    sudo_put_data(data, remote_path, uid='root', gid='root', mode=0600):


## put_data ##

Creates a regular file on the server with data provided by a string.
(Fabric's regular put command requires a local file to upload.)

### Usage ###

    put_data(data, remote_path, mode=0644)

## Requirements ##

Fabric 0.9.1 through 1.2. (Newer versions have not been tested.) Python 2.5 through 2.7. Mac OS, Linux/Unix, or Windows.

## License ##

BSD 2-clause license. See LICENSE file.


## Contact ##

Find this [project on GitHub](https://github.com/ashearer/Fabric-Extensions).

Written by Andrew Shearer. [Email](ashearerw@shearersoftware.com) / [Web site](http://www.ashearer.com/).


