param namespaces_sb_govt_assist_name string = 'sb-govt-assist'

resource servicebus_namespace 'Microsoft.ServiceBus/namespaces@2024-01-01' existing = {
  name: namespaces_sb_govt_assist_name
}

resource sharepoint_file_procession 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: servicebus_namespace
  name: 'sharepoint_file_procession'
  location: 'eastus2'
  properties: {
    maxMessageSizeInKilobytes: 256
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: true
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: false
    enableBatchedOperations: true
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    maxDeliveryCount: 50
    status: 'Active'
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    enablePartitioning: false
    enableExpress: false
  }
}
