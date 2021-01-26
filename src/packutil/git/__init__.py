import semver

from . import flow

main_branch = ["master", "main", "trunk"]
# define release detectors
release_branches = main_branch + ["release", "hotfix"]


def ref_name(ref):
    return flow.Branch(ref)


def get_tags(repo):
    return ["/".join(r.split("/")[2:]) for r in repo.references if "/tags/" in r]


def is_tag_branch(branch, prefix="v"):
    if branch.name[0 : len(prefix)] != prefix:
        return False

    try:
        semver.VersionInfo.parse(branch.name[len(prefix) :])
        return True
    except ValueError:
        return False
