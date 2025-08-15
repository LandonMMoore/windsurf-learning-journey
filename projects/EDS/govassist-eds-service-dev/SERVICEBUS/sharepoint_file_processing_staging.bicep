param namespaces_sb_govt_assist_name string = 'sb-govt-assist'

resource servicebus_namespace 'Microsoft.ServiceBus/namespaces@2024-01-01' existing = {
  name: namespaces_sb_govt_assist_name
}

resource sharepoint_file_processing_staging 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: servicebus_namespace
  name: 'sharepoint_file_processing_staging'
  location: 'eastus2'
  properties: {
    maxMessageSizeInKilobytes: 256
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: true
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: false
    enableBatchedOperations: true
    duplicateDetectionHistoryTimeWindow: 'PT3M'
    maxDeliveryCount: 50
    status: 'Active'
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    enablePartitioning: false
    enableExpress: false
  }
}
