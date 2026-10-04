"""
KALATRACE
Version Management System

Foundation Layer
Documento 71
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared.enums import VersionStatus, ChangeType


# ==========================================================
# Version Core
# ==========================================================

@dataclass(frozen=True)
class Version:

    major: int = 1
    minor: int = 0
    patch: int = 0

    status: VersionStatus = VersionStatus.INITIAL

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


    def __str__(self):
        return (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )


    def to_dict(self):
        return {
            "version": str(self),
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "status": self.status.value,
            "created_at":
                self.created_at.isoformat()
        }



# ==========================================================
# Version Builder
# ==========================================================

class VersionBuilder:


    @staticmethod
    def initial():

        return Version()



    @staticmethod
    def increment_patch(version):

        return Version(
            major=version.major,
            minor=version.minor,
            patch=version.patch + 1,
            status=VersionStatus.ACTIVE
        )



    @staticmethod
    def increment_minor(version):

        return Version(
            major=version.major,
            minor=version.minor + 1,
            patch=0,
            status=VersionStatus.ACTIVE
        )



    @staticmethod
    def increment_major(version):

        return Version(
            major=version.major + 1,
            minor=0,
            patch=0,
            status=VersionStatus.ACTIVE
        )



# ==========================================================
# Version History
# ==========================================================

@dataclass(frozen=True)
class VersionChange:


    change_type: ChangeType

    description: str

    author: str = "KALATRACE"

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


    def to_dict(self):

        return {

            "change_type":
                self.change_type.value,

            "description":
                self.description,

            "author":
                self.author,

            "created_at":
                self.created_at.isoformat()

        }



@dataclass
class VersionRecord:


    current_version: Version = field(
        default_factory=VersionBuilder.initial
    )


    history: list[VersionChange] = field(
        default_factory=list
    )


    def register_change(self, change):

        self.history.append(change)



    def get_history(self):

        return [
            item.to_dict()
            for item in self.history
        ]



# ==========================================================
# Version Comparison
# ==========================================================

class VersionComparator:


    @staticmethod
    def compare(first, second):

        first_tuple = (
            first.major,
            first.minor,
            first.patch
        )

        second_tuple = (
            second.major,
            second.minor,
            second.patch
        )


        if first_tuple < second_tuple:
            return -1


        if first_tuple > second_tuple:
            return 1


        return 0



    @staticmethod
    def is_newer(current, candidate):

        return (
            VersionComparator.compare(
                current,
                candidate
            ) == -1
        )



    @staticmethod
    def is_compatible(old, new):

        return (
            old.major ==
            new.major
        )



# ==========================================================
# Utilities
# ==========================================================

def parse_version(value):

    parts = value.split(".")

    if len(parts) != 3:
        raise ValueError(
            "Formato esperado MAJOR.MINOR.PATCH"
        )


    return Version(
        major=int(parts[0]),
        minor=int(parts[1]),
        patch=int(parts[2])
    )



def create_initial_version():

    return VersionBuilder.initial()



__all__ = [

    "Version",
    "VersionBuilder",
    "VersionChange",
    "VersionRecord",
    "VersionComparator",
    "parse_version",
    "create_initial_version"

]