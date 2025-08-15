from typing import Any, Dict

from src.core.config import configs

PAR_MAPPING: Dict[str, Any] = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "uuid": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "epar_name": {"type": "keyword"},
            "ai_summary": {"type": "text"},
            "status": {"type": "keyword"},
            "budget_analyst": {"type": "keyword"},
            "request_type": {"type": "keyword"},
            "project_number": {"type": "keyword"},
            "justification": {"type": "text"},
            "description": {"type": "text"},
            "master_project_name": {"type": "keyword"},
            "award_sponsor": {"type": "keyword"},
            "location": {"type": "keyword"},
            "total_project_budget": {"type": "float"},
            "fund_name": {"type": "keyword"},
            "project_name": {"type": "keyword"},
            "program_code": {"type": "keyword"},
            "account_group": {"type": "keyword"},
            "project_status": {"type": "keyword"},
            "account_detail": {"type": "keyword"},
            "project_type": {"type": "keyword"},
            "icrs_exempt": {"type": "boolean"},
            "icrs_rate": {"type": "float"},
            "funding_source": {"type": "keyword"},
            "current_project_end_date": {"type": "date"},
            "request_end_date": {"type": "date"},
            "reason_for_extension": {"type": "keyword"},
            "asset_type": {"type": "keyword"},
            "improvement_type": {"type": "keyword"},
            "project_manager": {"type": "keyword"},
            "recipient_project_number": {"type": "keyword"},
            "award_type": {"type": "keyword"},
            "contract_number": {"type": "keyword"},
            "bridge_number": {"type": "keyword"},
            "gis_route_id": {"type": "keyword"},
            "beginning_point": {"type": "keyword"},
            "end_point": {"type": "keyword"},
            "fap_number": {"type": "keyword"},
            "award": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "sponsor": {"type": "keyword"},
                    "award_name": {"type": "keyword"},
                },
            },
            "cost_center": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "cost_center": {"type": "keyword"},
                    "cost_center_name": {"type": "keyword"},
                    "cost_center_parent1": {"type": "keyword"},
                    "cost_center_parent1_desc": {"type": "keyword"},
                },
            },
            "fhwa": {
                "type": "object",
                "properties": {
                    "program_code": {"type": "keyword"},
                    "project_number": {"type": "keyword"},
                    "soar_grant": {"type": "keyword"},
                    "soar_project_no": {"type": "keyword"},
                    "stip_reference": {"type": "keyword"},
                    "categories": {"type": "keyword"},
                },
            },
            "master_project": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "master_project_number": {"type": "integer"},
                    "master_project_name": {"type": "keyword"},
                },
            },
            "organization": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "project_organization": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
            "project_location": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "location": {"type": "keyword"},
                },
            },
            "fund": {
                "properties": {
                    "id": {"type": "integer"},
                    "fund_number": {"type": "integer"},
                    "fund_name": {"type": "keyword"},
                }
            },
            "budget_info": {
                "type": "nested",
                "properties": {
                    "id": {"type": "integer"},
                    "par_id": {"type": "integer"},
                    "task_name": {"type": "keyword"},
                    "budget_items": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "integer"},
                            "account": {"type": "keyword"},
                            "parent_task_number": {"type": "keyword"},
                            "parent_task_name": {"type": "keyword"},
                            "subtask_number": {"type": "keyword"},
                            "lifetime_budget": {"type": "float"},
                            "initial_allotment": {"type": "float"},
                            "expenditures": {"type": "float"},
                            "obligations": {"type": "float"},
                            "commitments": {"type": "float"},
                            "current_balance": {"type": "float"},
                            "lifetime_balance": {"type": "float"},
                            "proposed_budget": {"type": "float"},
                            "change_amount": {"type": "float"},
                            "budget_info_id": {"type": "integer"},
                            "comment": {"type": "keyword"},
                        },
                    },
                },
            },
            "par_activities": {
                "type": "nested",
                "properties": {
                    "id": {"type": "integer"},
                    "activity": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "date": {"type": "date"},
                    "user": {"type": "keyword"},
                    "comments": {"type": "keyword"},
                },
            },
            "award_associations": {
                "type": "nested",
                "properties": {
                    "id": {"type": "integer"},
                    "award_type": {
                        "properties": {
                            "id": {"type": "integer"},
                            "code": {"type": "keyword"},
                            "description": {"type": "keyword"},
                        }
                    },
                },
            },
            "par_budget_analysis": {
                "type": "nested",
                "properties": {
                    "id": {"type": "integer"},
                    "par_budget_analysis_fund": {
                        "type": "nested",
                        "properties": {
                            "fund_type": {"type": "keyword"},
                            "ce": {"type": "float"},
                            "construction": {"type": "float"},
                            "feasibility_studies": {"type": "float"},
                            "design": {"type": "float"},
                            "rights_of_way": {"type": "float"},
                            "equipment": {"type": "float"},
                            "is_requested_fund": {"type": "boolean"},
                        },
                    },
                },
            },
        }
    }
}


R100_MAPPING: Dict[str, Any] = {
    "mappings": {
        "properties": {
            "actual_idcr_earned_as_of_mar": {"type": "float"},
            "budget_analyst": {"type": "keyword"},
            "difs_project_name": {"type": "keyword"},
            "difs_project_number": {"type": "long"},
            "fmis_end_date": {
                "type": "date",
                "format": "yyyy-MM-dd||strict_date_optional_time||epoch_millis",
            },
            "idcr_exempt": {"type": "boolean"},
            "monthly_data": {
                "type": "nested",
                "properties": {
                    "Oct-23": {"type": "float"},
                    "Nov-23": {"type": "float"},
                    "Dec-23": {"type": "float"},
                    "Jan-24": {"type": "float"},
                    "Feb-24": {"type": "float"},
                    "Mar-24": {"type": "float"},
                    "Apr-24": {"type": "float"},
                    "May-24": {"type": "float"},
                    "Jun-24": {"type": "float"},
                    "Jul-24": {"type": "float"},
                    "Aug-24": {"type": "float"},
                    "Sep-24": {"type": "float"},
                    "Oct-24": {"type": "float"},
                    "Nov-24": {"type": "float"},
                    "Dec-24": {"type": "float"},
                    "Jan-25": {"type": "float"},
                    "Feb-25": {"type": "float"},
                    "Mar-25": {"type": "float"},
                },
            },
            "service_type": {"type": "keyword"},
        },
    },
}

PAR_INDEX_MAPPING_LLM = {
    "r085": {
        "mappings": {
            "properties": {
                "award_sponsor": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "budget_info": {
                    "properties": {
                        "budget_items": {
                            "properties": {
                                "account": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "change_amount": {"type": "float"},
                                "comment": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "commitments": {"type": "float"},
                                "created_at": {"type": "date"},
                                "current_balance": {"type": "float"},
                                "expenditures": {"type": "float"},
                                "id": {"type": "long"},
                                "initial_allotment": {"type": "float"},
                                "lifetime_balance": {"type": "float"},
                                "lifetime_budget": {"type": "float"},
                                "obligations": {"type": "float"},
                                "parent_task_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "parent_task_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "proposed_budget": {"type": "float"},
                                "subtask_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "created_at": {"type": "date"},
                        "id": {"type": "long"},
                        "task_name": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "updated_at": {"type": "date"},
                        "uuid": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                    }
                },
                "created_at": {"type": "date"},
                "description": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "epar_name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "fund_name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "id": {"type": "long"},
                "justification": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "location": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "master_project_name": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "par_activities": {
                    "properties": {
                        "activity": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "comments": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "created_at": {"type": "date"},
                        "date": {"type": "date"},
                        "id": {"type": "long"},
                        "status": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "updated_at": {"type": "date"},
                        "user": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "uuid": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                    }
                },
                "project_details": {
                    "properties": {
                        "account": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "account_detail": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "account_group": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "account_parent1": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "asset_type": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "award": {
                            "properties": {
                                "award_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "sponsor": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "award_type": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "award_types": {
                            "properties": {
                                "code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "description": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "id": {"type": "long"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "beginning_point": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "bridge_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "budget_analyst": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "contract_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "cost_center": {
                            "properties": {
                                "cost_center": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "cost_center_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "cost_center_parent1": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "cost_center_parent1_desc": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "current_project_end_date": {"type": "date"},
                        "end_point": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "fap_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "fhwa_categories": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "program_code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "project_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_grant": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_project_no": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "stip_reference": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "fhwa_program_code": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "program_code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "project_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_grant": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_project_no": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "stip_reference": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "fhwa_project_number": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "program_code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "project_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_grant": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_project_no": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "stip_reference": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "fhwa_soar_grant": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "program_code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "project_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_grant": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_project_no": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "stip_reference": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "fhwa_soar_project_no": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "program_code": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "project_number": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_grant": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "soar_project_no": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "stip_reference": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "fund_number": {"type": "long"},
                        "funding_source": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "gis_route_id": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "icrs_exempt": {"type": "boolean"},
                        "icrs_rate": {"type": "float"},
                        "id": {"type": "long"},
                        "improvement_type": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "master_project": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "master_project_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "master_project_number": {"type": "long"},
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "organization": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "project_organization": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "owner_agency": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "par_budget_analysis": {
                            "properties": {
                                "additional_funds": {
                                    "properties": {
                                        "ce": {"type": "float"},
                                        "construction": {"type": "float"},
                                        "created_at": {"type": "date"},
                                        "design": {"type": "float"},
                                        "equipment": {"type": "float"},
                                        "feasibility_studies": {"type": "float"},
                                        "federal_fund": {
                                            "properties": {
                                                "fund_advance_construction": {
                                                    "type": "float"
                                                },
                                                "fund_available": {"type": "float"},
                                                "fund_code": {
                                                    "type": "text",
                                                    "fields": {
                                                        "keyword": {
                                                            "type": "keyword",
                                                            "ignore_above": 256,
                                                        }
                                                    },
                                                },
                                                "fund_obligations": {"type": "float"},
                                                "fund_pending_obligations": {
                                                    "type": "float"
                                                },
                                                "fund_pending_unobligated_balance": {
                                                    "type": "float"
                                                },
                                                "fund_unobligated_balance": {
                                                    "type": "float"
                                                },
                                                "id": {"type": "long"},
                                                "uuid": {
                                                    "type": "text",
                                                    "fields": {
                                                        "keyword": {
                                                            "type": "keyword",
                                                            "ignore_above": 256,
                                                        }
                                                    },
                                                },
                                            }
                                        },
                                        "id": {"type": "long"},
                                        "rights_of_way": {"type": "float"},
                                        "updated_at": {"type": "date"},
                                        "uuid": {
                                            "type": "text",
                                            "fields": {
                                                "keyword": {
                                                    "type": "keyword",
                                                    "ignore_above": 256,
                                                }
                                            },
                                        },
                                    }
                                },
                                "created_at": {"type": "date"},
                                "dc_rate": {"type": "float"},
                                "fa_rate": {"type": "float"},
                                "id": {"type": "long"},
                                "justification": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "par_id": {"type": "long"},
                                "part_rate": {"type": "float"},
                                "project_details_id": {"type": "long"},
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "program_code": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "program_parent1": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "program_parent1_description": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "project_location": {
                            "properties": {
                                "created_at": {"type": "date"},
                                "id": {"type": "long"},
                                "location": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                                "updated_at": {"type": "date"},
                                "uuid": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256,
                                        }
                                    },
                                },
                            }
                        },
                        "project_manager": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "project_name": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "project_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "project_status": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "project_type": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "reason_for_extension": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "recipient_project_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                        "request_end_date": {"type": "date"},
                        "uuid": {
                            "type": "text",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            },
                        },
                    }
                },
                "request_type": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "status": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "total_project_budget": {"type": "float"},
                "updated_at": {"type": "date"},
                "uuid": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
            }
        }
    }
}

R100_INDEX_MAPPING_LLM = {
    "r100": {
        "mappings": {
            "properties": {
                "FY24": {"type": "float"},
                "FY25": {"type": "float"},
                "actual_idcr_earned_as_of_mar": {"type": "float"},
                "average": {"type": "float"},
                "budget_analyst": {"type": "keyword"},
                "difs_project_name": {"type": "keyword"},
                "difs_project_number": {"type": "long"},
                "fmis_end_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd||strict_date_optional_time||epoch_millis",
                },
                "forecast_monthly_data": {
                    "dynamic": "true",
                    "properties": {
                        "Apr-25": {"type": "float"},
                        "Aug-25": {"type": "float"},
                        "Jul-25": {"type": "float"},
                        "Jun-25": {"type": "float"},
                        "May-25": {"type": "float"},
                        "Sep-25": {"type": "float"},
                    },
                },
                "idcr_exempt": {"type": "boolean"},
                "monthly_data": {
                    "properties": {
                        "Apr-24": {"type": "float"},
                        "Aug-24": {"type": "float"},
                        "Dec-23": {"type": "float"},
                        "Dec-24": {"type": "float"},
                        "Feb-24": {"type": "float"},
                        "Feb-25": {"type": "float"},
                        "Jan-24": {"type": "float"},
                        "Jan-25": {"type": "float"},
                        "Jul-24": {"type": "float"},
                        "Jun-24": {"type": "float"},
                        "Mar-24": {"type": "float"},
                        "Mar-25": {"type": "float"},
                        "May-24": {"type": "float"},
                        "Nov-23": {"type": "float"},
                        "Nov-24": {"type": "float"},
                        "Oct-23": {"type": "float"},
                        "Oct-24": {"type": "float"},
                        "Sep-24": {"type": "float"},
                    }
                },
                "projected_fy25_idcr": {"type": "float"},
                "service_type": {"type": "keyword"},
                "total_forecast_expenditure": {"type": "float"},
                "total_forecast_idcr": {"type": "float"},
                "variance": {"type": "float"},
            }
        }
    }
}

R025_INDEX_MAPPING_LLM = {
    "r025": {
        "mappings": {
            "properties": {
                "account": {"type": "keyword"},
                "account_category_description_parent_level_3": {"type": "keyword"},
                "account_category_parent_level_3": {"type": "keyword"},
                "account_description": {"type": "keyword"},
                "account_group_description_parent_level_1": {"type": "keyword"},
                "account_group_parent_level_1": {"type": "keyword"},
                "account_group_parent_level_1_description": {"type": "keyword"},
                "adjustment_budget": {"type": "float"},
                "agency": {"type": "keyword"},
                "agency_description": {"type": "keyword"},
                "appropriated_fund": {"type": "keyword"},
                "appropriated_fund_description": {"type": "keyword"},
                "available_budget": {"type": "float"},
                "award": {"type": "keyword"},
                "award_description": {"type": "keyword"},
                "budget_reservations": {"type": "float"},
                "commitment": {"type": "float"},
                "cost_center": {"type": "keyword"},
                "cost_center_description": {"type": "keyword"},
                "cost_center_description_parent_level_1": {"type": "keyword"},
                "cost_center_description_parent_level_2": {"type": "keyword"},
                "cost_center_parent_level_1": {"type": "keyword"},
                "cost_center_parent_level_1_description": {"type": "keyword"},
                "cost_center_parent_level_2": {"type": "keyword"},
                "cost_center_parent_level_2_description": {"type": "keyword"},
                "expenditure": {"type": "float"},
                "fund": {"type": "keyword"},
                "fund_description": {"type": "keyword"},
                "initial_budget": {"type": "float"},
                "obligation": {"type": "float"},
                "program": {"type": "keyword"},
                "program_description": {"type": "keyword"},
                "program_description_parent_level_1": {"type": "keyword"},
                "program_description_parent_level_2": {"type": "keyword"},
                "program_parent_level_1": {"type": "keyword"},
                "program_parent_level_1_description": {"type": "keyword"},
                "program_parent_level_2": {"type": "keyword"},
                "program_parent_level_2_description": {"type": "keyword"},
                "project": {"type": "keyword"},
                "project_description": {"type": "keyword"},
                "total_budget": {"type": "float"},
            }
        }
    }
}


# Index name
PAR_INDEX = configs.ELASTICSEARCH_DEFAULT_INDEX

# Mapping configurations
INDEX_MAPPINGS = {PAR_INDEX: PAR_MAPPING}
