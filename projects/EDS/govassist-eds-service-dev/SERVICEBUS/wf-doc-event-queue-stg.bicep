param namespaces_sb_govt_assist_name string = 'sb-govt-assist'

resource servicebus_namespace 'Microsoft.ServiceBus/namespaces@2024-01-01' existing = {
  name: namespaces_sb_govt_assist_name
}

resource wf_doc_event_queue_stg 'Microsoft.ServiceBus/namespaces/queues@2024-01-01' = {
  parent: servicebus_namespace
  name: 'wf-doc-event-queue-stg'
  location: 'eastus2'
  properties: {
    maxMessageSizeInKilobytes: 256
    lockDuration: 'PT1M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: false
    enableBatchedOperations: true
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    maxDeliveryCount: 10
    status: 'Active'
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    enablePartitioning: false
    enableExpress: false
  }
}
