import pygit2
import semver


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


# =====
# TESTS
# =====


def test_version(repo_path, version_module):
    repo = pygit2.Repository(repo_path)

    tags = [ref.split("/")[-1] for ref in repo.references if "/tags/" in ref]

    versions = []
    for tag in tags:
        try:
            versions.append(semver.VersionInfo.parse(tag[1:]))
        except ValueError:
            # if tag is not following semver do not append
            pass

    last_version = max(versions)
    assert version_module.major == last_version.major
    assert version_module.short_version == f"{last_version.major}.{last_version.minor}"
    assert version_module.version == str(last_version)
    assert version_module.version == version_module.full_version.split("-")[0]


def test_released(repo_path, version_module):
    repo = pygit2.Repository(repo_path)

    # define release detectors
    release_branches = ["master", "release", "hotfix"]

    def is_tag_branch(branch_name):
        if branch_name[0] != "v":
            return False

        try:
            semver.VersionInfo.parse(branch_name[1:])
            return True
        except ValueError:
            return False

    # get repo info
    branch_name = "/".join(repo.head.name.split("/")[2:])

    full_version = semver.VersionInfo.parse(version_module.full_version)

    # perform checks
    if branch_name.split("/")[0] in release_branches or is_tag_branch(branch_name):
        assert version_module.is_released
        assert full_version.prerelease is None
    else:
        assert not version_module.is_released
        assert full_version.prerelease == "develop"
