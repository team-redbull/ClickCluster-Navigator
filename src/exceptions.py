"""
Custom exception hierarchy for OpenShift Cluster Navigator.
Provides semantic error types for better error handling and debugging.
"""
from typing import Optional


class ClusterNavigatorException(Exception):
    """Base exception for all Cluster Navigator errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# ============== Cluster-related Exceptions ==============

class ClusterException(ClusterNavigatorException):
    """Base exception for cluster-related errors."""
    pass


class ClusterNotFoundError(ClusterException):
    """Raised when a cluster is not found."""

    def __init__(self, cluster_id: str, details: Optional[str] = None):
        self.cluster_id = cluster_id
        message = f"Cluster with ID '{cluster_id}' not found"
        super().__init__(message, details)


class ClusterAlreadyExistsError(ClusterException):
    """Raised when attempting to create a cluster that already exists."""

    def __init__(self, cluster_name: str, site: str, details: Optional[str] = None):
        self.cluster_name = cluster_name
        self.site = site
        message = f"Cluster '{cluster_name}' already exists in site '{site}'"
        super().__init__(message, details)


class InvalidClusterNameError(ClusterException):
    """Raised when cluster name validation fails."""

    def __init__(self, cluster_name: str, reason: str):
        self.cluster_name = cluster_name
        self.reason = reason
        message = f"Invalid cluster name '{cluster_name}': {reason}"
        super().__init__(message, reason)


class ClusterDeletionError(ClusterException):
    """Raised when cluster deletion fails."""

    def __init__(self, cluster_id: str, reason: str):
        self.cluster_id = cluster_id
        self.reason = reason
        message = f"Failed to delete cluster '{cluster_id}': {reason}"
        super().__init__(message, reason)


class SegmentsManagerClusterProtectedError(ClusterException):
    """Raised when attempting to modify/delete a Segments Manager cluster."""

    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        message = "Cannot delete Segments Manager clusters. Only manual clusters can be deleted."
        super().__init__(message)


# ============== Validation Exceptions ==============

class ValidationError(ClusterNavigatorException):
    """Base exception for validation errors."""
    pass


class InvalidCIDRError(ValidationError):
    """Raised when network segment CIDR validation fails."""

    def __init__(self, segment: str, reason: str):
        self.segment = segment
        self.reason = reason
        message = f"Invalid CIDR notation in segment '{segment}': {reason}"
        super().__init__(message, reason)


# ============== Authentication Exceptions ==============

class AuthenticationError(ClusterNavigatorException):
    """Base exception for authentication errors."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when authentication credentials are invalid."""

    def __init__(self):
        message = "Invalid credentials"
        super().__init__(message)


class UnauthorizedError(AuthenticationError):
    """Raised when user is not authorized for an operation."""

    def __init__(self, operation: str):
        self.operation = operation
        message = f"Unauthorized to perform operation: {operation}"
        super().__init__(message)


# ============== Data Access Exceptions ==============

class DataAccessError(ClusterNavigatorException):
    """Base exception for data access errors."""
    pass


class CacheReadError(DataAccessError):
    """Raised when cache read operation fails."""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        message = f"Failed to read cache from '{file_path}': {reason}"
        super().__init__(message, reason)


class CacheWriteError(DataAccessError):
    """Raised when cache write operation fails."""

    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        message = f"Failed to write cache to '{file_path}': {reason}"
        super().__init__(message, reason)


# ============== External API Exceptions ==============

class ExternalAPIError(ClusterNavigatorException):
    """Base exception for external API errors."""
    pass


class SegmentsManagerAPIError(ExternalAPIError):
    """Raised when Segments Manager API request fails."""

    def __init__(self, endpoint: str, status_code: Optional[int] = None, details: Optional[str] = None):
        self.endpoint = endpoint
        self.status_code = status_code
        message = f"Segments Manager API error for endpoint '{endpoint}'"
        if status_code:
            message += f" (HTTP {status_code})"
        super().__init__(message, details)


class SegmentsManagerUnavailableError(ExternalAPIError):
    """Raised when Segments Manager is unavailable."""

    def __init__(self, reason: Optional[str] = None):
        message = "Segments Manager is currently unavailable"
        super().__init__(message, reason)
