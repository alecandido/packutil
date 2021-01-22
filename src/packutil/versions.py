import pygit2


def mkversion(major, minor, micro):
    return "%d.%d.%d" % (major, minor, micro)


def is_released(repo_path):
    repo = pygit2.Repository(repo_path)

    # determine ids of tagged commits
    tags_commit_sha = [
        repo.resolve_refish("/".join(r.split("/")[2:]))[0].id
        for r in repo.references
        if "/tags/" in r
    ]
    return "main" in repo.head.name or repo.head.target in tags_commit_sha


def write_version_py(major, minor, micro, is_released, filename):
    cnt = """
# THIS FILE IS GENERATED FROM SETUP.PY
major = %(major)d
short_version = '%(short_version)s'
version = '%(version)s'
full_version = '%(full_version)s'
is_released = %(isreleased)s
"""
    version = mkversion(major, minor, micro)
    fullversion = version
    if not is_released:
        fullversion += "-develop"

    a = open(filename, "w")
    try:
        a.write(
            cnt
            % {
                "major": major,
                "short_version": "%d.%d" % (major, minor),
                "version": version,
                "full_version": fullversion,
                "isreleased": str(is_released),
            }
        )
    finally:
        a.close()
