from enum import Enum

class ResourceLifecycleStatus(Enum):
  # Initial Lifecycle Status
  # Given when the resource is first created and is waiting to be provisioned
  PENDING = "Pending"

  # Transitional Lifecycle Status
  # Given once Terraform begins provisioning the resource
  PROVISIONING = "Provisioning"

  # Transitional Error Lifecycle Status
  # Given in the event the resource provisioning fails
  PROVISIONING_ERROR = "Provisioning Error"

  # Provisioned Lifecycle State
  # Given once the resource has been successfully provisioned and is available
  PROVISIONED = "Provisioned"

  # Transitional Lifecycle Status
  # Given once the resource is marked for destruction
  PURGING = "Purging"

  # Transitional Error Lifecycle Status
  # Given in the event the resource destruction fails
  PURGE_ERROR = "Purge Error"

  # Final Lifecycle Status
  # Given once the resource has been successfully destroyed
  PURGED = "Purged"
