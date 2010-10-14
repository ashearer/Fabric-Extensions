"""
Utility functions for Fabric deployment scripts
Compatibile with Fabric 0.9.1 and 0.9.2, Python 2.5 and 2.6.
Temporary file handling works under both Windows and Unix-based OSes.

by Andrew Shearer <ashearerw@shearersoftware.com>
"""

from fabric import api as fapi

def run_prompted(command, password='', prompt='Password[^:]*: ', pty=True):
    """
    Re-use Fabric's sudo prompt mechanism for other password prompts
    (database, version control, etc.)
    
    prompt gives a regular expression matching the remote prompt. Fabric
    will add anchors to make it match an entire line.
    
    If the password param is non-empty, use it. Otherwise prompt locally.
    
    Returns the password (either default or user-entered), which the caller
    can then supply as the password parameter to subsequent _run_prompted
    calls involving the same system.
    
    Caveat: The prompt displayed locally is the same as the one displayed
    for sudo passwords ('Password for <username>@<host>:'), which may be
    misleading. But attempting to customize it would be too hacky, even
    for this function.
    """
    saved_prompt, saved_password = env.sudo_prompt, env.password
    env.sudo_prompt, env.password = prompt, password
    try:
        fapi.run(command, pty=pty)
        return env.password
    finally:
        env.sudo_prompt, env.password = saved_prompt, saved_password

def run_script(script, runner=None, password=None, prompt=None, pty=False):
    """
    Upload the given script content and either pipe it into the given command
    or, if no command is given, execute it directly (in this case, its shebang
    line should provide the command).
    If prompt is not empty, password prompts will be recognized and answered
    as described for _run_sudo.
    The advantage of using this command instead of passing the statements
    to "run" (or of using "run" and "echo" to pipe them to a script runner)
    is in security: they won't appear on the command line, so they won't
    appear momentarily in "ps" and won't be recorded in bash history, both
    helpful when including passwords. Also, there's less per-statement
    overhead.
    """
    temp_remote_file = 'temp-fabric-script'
    if runner:
        command = '%s < "%s"' % (runner, temp_remote_file)
        mode = 0600
    else:
        command = '"./%s"' % temp_remote_file
        mode = 0700
    try:
        put_data(script, temp_remote_file, mode)
        if prompt:
            run_prompted(command, password=password, prompt=prompt, pty=pty)
        else:
            fapi.run(command, pty=pty)
    finally:
        fapi.run('[ ! -f "%s" ] || rm -f "%s"' % (temp_remote_file,
            temp_remote_file))

def sudo_put_data(data, remote_path, uid='root', gid='root', mode=0600):
    """
    Create a privileged file with data provided by a string.
    The file will first be created in the current home directory, then moved
    into place with sudo, because the current user may not have sufficient
    permissions for the regular 'put' command to place it there directly.
    """
    import tempfile
    fd, name = tempfile.mkstemp()
    try:
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        remote_tempfile = 'temp-fabric-file'
        try:
            fapi.put(name, remote_tempfile, mode=0777)    # make remote tempfile
            sudo('mv "%(remote_tempfile)s" "%(remote_path)s"'
                 ' && chown %(uid)s:%(gid)s "%(remote_path)s"'
                 ' && chmod %(mode)o "%(remote_path)s"'
                % {'remote_path': remote_path, 'remote_tempfile': remote_tempfile,
                   'uid': uid, 'gid': gid, 'mode': mode}, pty=True)
        finally:
            # error cleanup: remove remote tempfile if it still exists
            run('[ ! -f "%(remote_tempfile)s" ]'
                ' || rm -f "%(remote_tempfile)s"'
                % {'remote_tempfile': remote_tempfile})
    finally:
        os.remove(name)

def put_data(data, remote_path, mode=0644):
    """
    Create a file with data provided by a string.
    """
    import tempfile
    fd, name = tempfile.mkstemp()
    try:
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        fapi.put(name, remote_path, mode=mode)
    finally:
        os.remove(name)
