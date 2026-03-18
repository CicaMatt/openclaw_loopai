#!/usr/bin/env python3
import argparse
import copy
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from urllib import error, parse, request

EXECUTION_ENDPOINT = (
    "http://looporchestra.sytes.net:4001/admin/prototype_execution/prototype_execution/"
)
UPLOAD_BASE_URL = "http://looporchestra.sytes.net:4001/nodes/input/upload"
FIXED_STORAGE_REF = "nodes_bucket"
FIXED_LOCAL_FILE_PATH = "upload/"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}

REQUEST_TEMPLATE = {
    "prototype_id": "69b862e0a6fbd73a6254e5be",
    "created_at": "2026-03-16T20:06:56.253000",
    "updated_at": "2026-03-16T20:06:56.253000",
    "prototype_name": "Test_Kidney_nexus",
    "prototype_description": "It Prototype",
    "prototype_subtitle": None,
    "prototype_players": [
        {"user_id": "626130f7c71f6b9e651c76be", "role": "owner"}
    ],
    "workflows": [
        {
            "workflow_name": "Test_Kidney_nexus",
            "workflow_id": "wf_id",
            "workflow_type": "prototype",
            "branches": [
                {
                    "branch_id": "677dt868a8pjr3p7uedynl",
                    "branch_name": "Branch 1",
                    "nodes": [
                        {
                            "node_category": "input",
                            "node_sub_category": "Data Reader",
                            "node_name": "NodeDataReader5",
                            "node_label": "Image Reader",
                            "node_description": "Reads one or more Images files",
                            "endpoints": [
                                {"position": 0, "endpoint": "/nodes/input/upload"},
                                {"position": 0, "endpoint": "/nodes/input/data-reader"}
                            ],
                            "allowed_node_types": [
                                "operator",
                                "ai_tool",
                                "evaluation_visualization",
                                "process_automation",
                                "output"
                            ],
                            "style": {
                                "icon": "<svg width=\"19\" height=\"23\" viewBox=\"0 0 19 23\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n <path d=\"M0.00173349 14.9961V17.8964V18.2963V18.3964C-0.00216686 18.3964 0.00173349 18.3964 0.00173349 18.4964C0.00173349 20.8966 4.0315 22.9968 9.00254 22.9968C13.974 22.9968 18.0033 20.8966 18.0033 18.4964V18.2963V17.9964V14.9961H0.00173349Z\" fill=\"#2B5F7C\"/>\n <path d=\"M18.0036 15.0004C18.0036 17.2097 13.9742 19.0007 9.00276 19.0007C4.03171 19.0007 0.00195312 17.2097 0.00195312 15.0004C0.00195312 12.7911 4.03171 11 9.00276 11C13.9742 11 18.0036 12.7911 18.0036 15.0004Z\" fill=\"#BDC3C7\"/>\n <path d=\"M0.00173349 9.99609V12.8964V13.2963V13.3964C-0.00216686 13.3964 0.00173349 13.3964 0.00173349 13.4964C0.00173349 15.8966 4.0315 17.9968 9.00254 17.9968C13.974 17.9968 18.0033 15.8966 18.0033 13.4964V13.2963V12.9964V9.99609H0.00173349Z\" fill=\"#2B5F7C\"/>\n <path d=\"M18.0036 9.99645C18.0036 12.2058 13.9742 13.9968 9.00276 13.9968C4.03171 13.9968 0.00195312 12.2058 0.00195312 9.99645C0.00195312 7.78715 4.03171 5.99609 9.00276 5.99609C13.9742 5.99609 18.0036 7.78715 18.0036 9.99645Z\" fill=\"#BDC3C7\"/>\n <path d=\"M0.0644587 13.4961C0.0184546 13.5961 0.00195312 13.7961 0.00195312 13.9961C0.00195312 16.1963 4.03171 17.9965 9.00276 17.9965C13.9742 17.9965 18.0036 16.1963 18.0036 13.9961C18.0036 13.7961 17.9866 13.5961 17.9416 13.4961C17.3875 15.3963 13.5922 16.9964 9.00276 16.9964C4.41295 16.9964 0.618308 15.3963 0.0644587 13.4961Z\" fill=\"#ECF0F1\"/>\n <path d=\"M0.00173349 4.99609V7.89638V8.29632V8.39642C-0.00216686 8.39642 0.00173349 8.3964 0.00173349 8.49641C0.00173349 10.8966 4.0315 12.9968 9.00254 12.9968C13.974 12.9968 18.0033 10.8966 18.0033 8.49641V8.29632V7.99636V4.99609H0.00173349Z\" fill=\"#2B5F7C\"/>\n <path d=\"M0.0644587 8.5C0.0184546 8.60001 0.00195312 8.80003 0.00195312 9.00004C0.00195312 11.2002 4.03171 13.0004 9.00276 13.0004C13.9742 13.0004 18.0036 11.2002 18.0036 9.00004C18.0036 8.80003 17.9866 8.60001 17.9416 8.5C17.3875 10.4002 13.5922 12.0003 9.00276 12.0003C4.41295 12.0003 0.618308 10.4002 0.0644587 8.5Z\" fill=\"#153547\"/>\n <path d=\"M9.00195 14.9961V22.9968C13.9734 22.9968 18.0028 20.8966 18.0028 18.4964V18.2963V17.9964V14.9961H9.00195Z\" fill=\"#2B5F7C\"/>\n <path d=\"M9.00195 10.9922V18.9929C13.9734 18.9929 18.0028 17.2017 18.0028 14.9925C18.0028 12.7832 13.9734 10.9922 9.00195 10.9922Z\" fill=\"#153547\"/>\n <path d=\"M9.00195 9.99609V17.9968C13.9734 17.9968 18.0028 15.9816 18.0028 13.4964V13.3089V12.9964V9.99609H9.00195Z\" fill=\"#2B5F7C\"/>\n <path d=\"M17.9408 13.4961C17.3867 15.4693 13.5914 16.9964 9.00195 16.9964V17.9965C13.9734 17.9965 18.0028 16.2053 18.0028 13.9961C18.0028 13.8267 17.9858 13.6599 17.9408 13.4961Z\" fill=\"#ECF0F1\"/>\n <path d=\"M9.00195 5.99609V13.9968C13.9734 13.9968 18.0028 12.2057 18.0028 9.99645C18.0028 7.78715 13.9734 5.99609 9.00195 5.99609Z\" fill=\"#ECF0F1\"/>\n <path d=\"M9.00195 4.99609V12.9968C13.9734 12.9968 18.0028 10.9816 18.0028 8.49641V8.30889V7.99636V4.99609H9.00195Z\" fill=\"#2B5F7C\"/>\n <path d=\"M17.9408 8.5C17.3867 10.4732 13.5914 12.0003 9.00195 12.0003V13.0004C13.9734 13.0004 18.0028 11.2092 18.0028 9.00004C18.0028 8.83063 17.9858 8.66381 17.9408 8.5Z\" fill=\"#153547\"/>\n <path d=\"M18.0036 4.99645C18.0036 7.20575 13.9742 8.99681 9.00276 8.99681C4.03171 8.99681 0.00195312 7.20575 0.00195312 4.99645C0.00195312 2.78715 4.03171 0.996094 9.00276 0.996094C13.9742 0.996094 18.0036 2.78715 18.0036 4.99645Z\" fill=\"#407C9E\"/>\n </svg>",
                                "notexecuted_border_color": "#407C9E",
                                "notexecuted_background_color": "#FFFFFF",
                                "executed_background_color": "#407C9E",
                                "executed_border_color": "#0F4873"
                            },
                            "data": {
                                "general_parameters": {
                                    "filename": "<image_path_here>",
                                    "storage_ref": "nodes_bucket"
                                },
                                "specific_parameters": {
                                    "type": "jpg",
                                    "sep": ",",
                                    "sheet_name": 0,
                                    "encoding": "latin-1",
                                    "columns": {}
                                }
                            },
                            "children": [
                                {
                                    "node_category": "build_ai_tool",
                                    "node_sub_category": "Loop Ready Model",
                                    "node_name": "kidney_cancer_detection_model",
                                    "node_label": "Kidney Cancer Detection",
                                    "node_description": "Kidney Cancer Detection",
                                    "endpoints": [
                                        {
                                            "position": 0,
                                            "endpoint": "/nodes/ai_tool/kidney-cancer-detection-model"
                                        }
                                    ],
                                    "allowed_node_types": [
                                        "operator",
                                        "ai_tool",
                                        "evaluation_visualization",
                                        "process_automation",
                                        "output"
                                    ],
                                    "style": {
                                        "icon": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 22 22\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n <path d=\"M12.0377 11.6211H11.2075V19.0928H12.0377V11.6211Z\" fill=\"#5B0228\"/>\n <path d=\"M19.3878 2.78234L18.8008 2.19531L12.5745 8.42161L13.1615 9.00863L19.3878 2.78234Z\" fill=\"#5B0228\"/>\n <path d=\"M11.086 11.087L10.499 10.5L2.1973 18.8017L2.78432 19.3887L11.086 11.087Z\" fill=\"#5B0228\"/>\n <path d=\"M10.2558 8.0073L5.68994 3.44141L5.10292 4.02843L9.6688 8.59433L10.2558 8.0073Z\" fill=\"#5B0228\"/>\n <path d=\"M18.9724 16.7263L12.7461 10.5L12.1591 11.087L18.3854 17.3133L18.9724 16.7263Z\" fill=\"#5B0228\"/>\n <path d=\"M19.9246 4.15094C21.0708 4.15094 22.0001 3.22172 22.0001 2.07547C22.0001 0.92922 21.0708 0 19.9246 0C18.7783 0 17.8491 0.92922 17.8491 2.07547C17.8491 3.22172 18.7783 4.15094 19.9246 4.15094Z\" fill=\"#D7B4C2\"/>\n <path d=\"M11.6228 21.9986C12.7691 21.9986 13.6983 21.0694 13.6983 19.9231C13.6983 18.7769 12.7691 17.8477 11.6228 17.8477C10.4766 17.8477 9.54736 18.7769 9.54736 19.9231C9.54736 21.0694 10.4766 21.9986 11.6228 21.9986Z\" fill=\"#EC5C70\"/>\n <path d=\"M2.07547 21.1705C3.22172 21.1705 4.15094 20.2413 4.15094 19.095C4.15094 17.9488 3.22172 17.0195 2.07547 17.0195C0.92922 17.0195 0 17.9488 0 19.095C0 20.2413 0.92922 21.1705 2.07547 21.1705Z\" fill=\"#D7B4C2\"/>\n <path d=\"M4.98112 4.56478C5.66887 4.56478 6.22641 4.00725 6.22641 3.3195C6.22641 2.63175 5.66887 2.07422 4.98112 2.07422C4.29337 2.07422 3.73584 2.63175 3.73584 3.3195C3.73584 4.00725 4.29337 4.56478 4.98112 4.56478Z\" fill=\"#FF84B7\"/>\n <path d=\"M18.2643 17.8499C18.9521 17.8499 19.5096 17.2924 19.5096 16.6047C19.5096 15.9169 18.9521 15.3594 18.2643 15.3594C17.5766 15.3594 17.019 15.9169 17.019 16.6047C17.019 17.2924 17.5766 17.8499 18.2643 17.8499Z\" fill=\"#FF84B7\"/>\n <path d=\"M11.6225 12.866C13.2272 12.866 14.5281 11.5651 14.5281 9.96035C14.5281 8.3556 13.2272 7.05469 11.6225 7.05469C10.0177 7.05469 8.7168 8.3556 8.7168 9.96035C8.7168 11.5651 10.0177 12.866 11.6225 12.866Z\" fill=\"#EC5C70\"/>\n </svg>",
                                        "notexecuted_border_color": "#EC5C70",
                                        "notexecuted_background_color": "#FFFFFF",
                                        "executed_background_color": "#EC5C70",
                                        "executed_border_color": "#AD3848"
                                    },
                                    "data": {
                                        "general_parameters": {
                                            "age": "",
                                            "localization": "",
                                            "dx_type": "",
                                            "sex": "",
                                            "input_df": "string",
                                            "secret_key": "string",
                                            "text_column_name": "",
                                            "model_path": "string",
                                            "storage_ref": "nodes_bucket",
                                            "computing_machines": [
                                                {
                                                    "machine_id": "sd8fs90d8f0d80s",
                                                    "machine_name": "Google - NVIDIA GeForce RTX 2070"
                                                },
                                                {
                                                    "machine_id": "v8fsd8fs9d8f0s",
                                                    "machine_name": "AWS - Nvidia Tesla v100 16GB"
                                                }
                                            ]
                                        },
                                        "specific_parameters": {
                                            "language": "english",
                                            "model_type": "large",
                                            "entity_types": "['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART','IBAN','BIC']"
                                        }
                                    },
                                    "children": [
                                        {
                                            "node_category": "build_ai_tool",
                                            "node_sub_category": "Loop Ready Model",
                                            "node_name": "image_analyzer_model",
                                            "node_label": "Image Analyzer",
                                            "node_description": "Image Analyzer",
                                            "endpoints": [
                                                {
                                                    "position": 0,
                                                    "endpoint": "/nodes/ai_tool/image-analyzer"
                                                }
                                            ],
                                            "allowed_node_types": [
                                                "operator",
                                                "ai_tool",
                                                "evaluation_visualization",
                                                "process_automation",
                                                "output"
                                            ],
                                            "style": {
                                                "icon": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 22 22\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n <path d=\"M12.0377 11.6211H11.2075V19.0928H12.0377V11.6211Z\" fill=\"#5B0228\"/>\n <path d=\"M19.3878 2.78234L18.8008 2.19531L12.5745 8.42161L13.1615 9.00863L19.3878 2.78234Z\" fill=\"#5B0228\"/>\n <path d=\"M11.086 11.087L10.499 10.5L2.1973 18.8017L2.78432 19.3887L11.086 11.087Z\" fill=\"#5B0228\"/>\n <path d=\"M10.2558 8.0073L5.68994 3.44141L5.10292 4.02843L9.6688 8.59433L10.2558 8.0073Z\" fill=\"#5B0228\"/>\n <path d=\"M18.9724 16.7263L12.7461 10.5L12.1591 11.087L18.3854 17.3133L18.9724 16.7263Z\" fill=\"#5B0228\"/>\n <path d=\"M19.9246 4.15094C21.0708 4.15094 22.0001 3.22172 22.0001 2.07547C22.0001 0.92922 21.0708 0 19.9246 0C18.7783 0 17.8491 0.92922 17.8491 2.07547C17.8491 3.22172 18.7783 4.15094 19.9246 4.15094Z\" fill=\"#D7B4C2\"/>\n <path d=\"M11.6228 21.9986C12.7691 21.9986 13.6983 21.0694 13.6983 19.9231C13.6983 18.7769 12.7691 17.8477 11.6228 17.8477C10.4766 17.8477 9.54736 18.7769 9.54736 19.9231C9.54736 21.0694 10.4766 21.9986 11.6228 21.9986Z\" fill=\"#EC5C70\"/>\n <path d=\"M2.07547 21.1705C3.22172 21.1705 4.15094 20.2413 4.15094 19.095C4.15094 17.9488 3.22172 17.0195 2.07547 17.0195C0.92922 17.0195 0 17.9488 0 19.095C0 20.2413 0.92922 21.1705 2.07547 21.1705Z\" fill=\"#D7B4C2\"/>\n <path d=\"M4.98112 4.56478C5.66887 4.56478 6.22641 4.00725 6.22641 3.3195C6.22641 2.63175 5.66887 2.07422 4.98112 2.07422C4.29337 2.07422 3.73584 2.63175 3.73584 3.3195C3.73584 4.00725 4.29337 4.56478 4.98112 4.56478Z\" fill=\"#FF84B7\"/>\n <path d=\"M18.2643 17.8499C18.9521 17.8499 19.5096 17.2924 19.5096 16.6047C19.5096 15.9169 18.9521 15.3594 18.2643 15.3594C17.5766 15.3594 17.019 15.9169 17.019 16.6047C17.019 17.2924 17.5766 17.8499 18.2643 17.8499Z\" fill=\"#FF84B7\"/>\n <path d=\"M11.6225 12.866C13.2272 12.866 14.5281 11.5651 14.5281 9.96035C14.5281 8.3556 13.2272 7.05469 11.6225 7.05469C10.0177 7.05469 8.7168 8.3556 8.7168 9.96035C8.7168 11.5651 10.0177 12.866 11.6225 12.866Z\" fill=\"#EC5C70\"/>\n </svg>",
                                                "notexecuted_border_color": "#EC5C70",
                                                "notexecuted_background_color": "#FFFFFF",
                                                "executed_background_color": "#EC5C70",
                                                "executed_border_color": "#AD3848"
                                            },
                                            "data": {
                                                "general_parameters": {
                                                    "input_df": "string",
                                                    "secret_key": "string",
                                                    "text_column_name": "",
                                                    "model_path": "string",
                                                    "storage_ref": "nodes_bucket",
                                                    "computing_machines": [
                                                        {
                                                            "machine_id": "sd8fs90d8f0d80s",
                                                            "machine_name": "Google - NVIDIA GeForce RTX 2070"
                                                        },
                                                        {
                                                            "machine_id": "v8fsd8fs9d8f0s",
                                                            "machine_name": "AWS - Nvidia Tesla v100 16GB"
                                                        }
                                                    ]
                                                },
                                                "specific_parameters": {
                                                    "language": "english",
                                                    "model_type": "large",
                                                    "entity_types": "['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART','IBAN','BIC']"
                                                }
                                            },
                                            "children": [
                                                {
                                                    "node_category": "build_ai_tool",
                                                    "node_sub_category": "Loop Ready Model",
                                                    "node_name": "x_ai_model",
                                                    "node_label": "X Ai",
                                                    "node_description": "X Ai",
                                                    "endpoints": [
                                                        {
                                                            "position": 0,
                                                            "endpoint": "/nodes/ai_tool/rag"
                                                        }
                                                    ],
                                                    "allowed_node_types": [
                                                        "operator",
                                                        "ai_tool",
                                                        "evaluation_visualization",
                                                        "process_automation",
                                                        "output"
                                                    ],
                                                    "style": {
                                                        "icon": "<svg width=\"22\" height=\"22\" viewBox=\"0 0 22 22\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">\n <path d=\"M12.0377 11.6211H11.2075V19.0928H12.0377V11.6211Z\" fill=\"#5B0228\"/>\n <path d=\"M19.3878 2.78234L18.8008 2.19531L12.5745 8.42161L13.1615 9.00863L19.3878 2.78234Z\" fill=\"#5B0228\"/>\n <path d=\"M11.086 11.087L10.499 10.5L2.1973 18.8017L2.78432 19.3887L11.086 11.087Z\" fill=\"#5B0228\"/>\n <path d=\"M10.2558 8.0073L5.68994 3.44141L5.10292 4.02843L9.6688 8.59433L10.2558 8.0073Z\" fill=\"#5B0228\"/>\n <path d=\"M18.9724 16.7263L12.7461 10.5L12.1591 11.087L18.3854 17.3133L18.9724 16.7263Z\" fill=\"#5B0228\"/>\n <path d=\"M19.9246 4.15094C21.0708 4.15094 22.0001 3.22172 22.0001 2.07547C22.0001 0.92922 21.0708 0 19.9246 0C18.7783 0 17.8491 0.92922 17.8491 2.07547C17.8491 3.22172 18.7783 4.15094 19.9246 4.15094Z\" fill=\"#D7B4C2\"/>\n <path d=\"M11.6228 21.9986C12.7691 21.9986 13.6983 21.0694 13.6983 19.9231C13.6983 18.7769 12.7691 17.8477 11.6228 17.8477C10.4766 17.8477 9.54736 18.7769 9.54736 19.9231C9.54736 21.0694 10.4766 21.9986 11.6228 21.9986Z\" fill=\"#EC5C70\"/>\n <path d=\"M2.07547 21.1705C3.22172 21.1705 4.15094 20.2413 4.15094 19.095C4.15094 17.9488 3.22172 17.0195 2.07547 17.0195C0.92922 17.0195 0 17.9488 0 19.095C0 20.2413 0.92922 21.1705 2.07547 21.1705Z\" fill=\"#D7B4C2\"/>\n <path d=\"M4.98112 4.56478C5.66887 4.56478 6.22641 4.00725 6.22641 3.3195C6.22641 2.63175 5.66887 2.07422 4.98112 2.07422C4.29337 2.07422 3.73584 2.63175 3.73584 3.3195C3.73584 4.00725 4.29337 4.56478 4.98112 4.56478Z\" fill=\"#FF84B7\"/>\n <path d=\"M18.2643 17.8499C18.9521 17.8499 19.5096 17.2924 19.5096 16.6047C19.5096 15.9169 18.9521 15.3594 18.2643 15.3594C17.5766 15.3594 17.019 15.9169 17.019 16.6047C17.019 17.2924 17.5766 17.8499 18.2643 17.8499Z\" fill=\"#FF84B7\"/>\n <path d=\"M11.6225 12.866C13.2272 12.866 14.5281 11.5651 14.5281 9.96035C14.5281 8.3556 13.2272 7.05469 11.6225 7.05469C10.0177 7.05469 8.7168 8.3556 8.7168 9.96035C8.7168 11.5651 10.0177 12.866 11.6225 12.866Z\" fill=\"#EC5C70\"/>\n </svg>",
                                                        "notexecuted_border_color": "#EC5C70",
                                                        "notexecuted_background_color": "#FFFFFF",
                                                        "executed_background_color": "#EC5C70",
                                                        "executed_border_color": "#AD3848"
                                                    },
                                                    "data": {
                                                        "general_parameters": {
                                                            "input_df": "string",
                                                            "secret_key": "string",
                                                            "text_column_name": "",
                                                            "model_path": "string",
                                                            "pdf_path": "/upload/2026-03-16_20.05.56_d1PtORaYYoNWDsbQg6qs/kidney_test2.jpeg",
                                                            "storage_ref": "nodes_bucket",
                                                            "computing_machines": [
                                                                {
                                                                    "machine_id": "sd8fs90d8f0d80s",
                                                                    "machine_name": "Google - NVIDIA GeForce RTX 2070"
                                                                },
                                                                {
                                                                    "machine_id": "v8fsd8fs9d8f0s",
                                                                    "machine_name": "AWS - Nvidia Tesla v100 16GB"
                                                                }
                                                            ]
                                                        },
                                                        "specific_parameters": {
                                                            "language": "english",
                                                            "model_type": "large",
                                                            "entity_types": "['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART','IBAN','BIC']"
                                                        }
                                                    },
                                                    "children": [],
                                                    "tracking": {
                                                        "run_id": "string",
                                                        "start": False,
                                                        "experiment_name": "string",
                                                        "workflow_name": "string",
                                                        "workflow_type": "experiment",
                                                        "workflow_id": "string",
                                                        "workflow_run_id": "string",
                                                        "tags": {
                                                            "additionalProp1": "string",
                                                            "additionalProp2": "string",
                                                            "additionalProp3": "string"
                                                        },
                                                        "parameters": {
                                                            "confidence_interpretation": "A confidence level of 99.99% indicates a high degree of certainty in the analysis, but it is essential to note that medical imaging analysis is not a definitive diagnostic tool.",
                                                            "recommended_next_steps": [
                                                                "Further medical evaluation, including imaging studies and laboratory tests, to confirm the diagnosis.",
                                                                "Consultation with a medical professional to discuss the results and determine the best course of action.",
                                                                "Consideration of additional diagnostic tests, such as biopsy or genetic testing, to gather more information."
                                                            ],
                                                            "references": [
                                                                {
                                                                    "title": "Kidney Cancer: Diagnosis and Treatment",
                                                                    "author": "American Cancer Society",
                                                                    "year": "2022",
                                                                    "url": "https://www.cancer.org/cancer/kidney-cancer/detection-diagnosis-staging.html"
                                                                },
                                                                {
                                                                    "title": "Imaging in Kidney Cancer",
                                                                    "author": "European Association of Urology",
                                                                    "year": "2020",
                                                                    "url": "https://uroweb.org/guideline/kidney-cancer/"
                                                                }
                                                            ],
                                                            "summary": "The provided medical image analysis suggests a high likelihood of kidney cancer, with a confidence level of 99.99%. The visual evidence points to a kidney tumor, and the class probabilities indicate a strong likelihood of kidney cancer.",
                                                            "visual_evidence": "The image analysis detected a kidney tumor, which is a common indicator of kidney cancer."
                                                        },
                                                        "metrics": {},
                                                        "artifacts": {
                                                            "input_file": True,
                                                            "output_file": False,
                                                            "input_dataframe": False,
                                                            "model_file": False
                                                        }
                                                    },
                                                    "node_name_dict": "x_ai_model",
                                                    "executed": False,
                                                    "node_id": "6946dff31cc02c3427815ae2",
                                                    "prototype_id": "69b862e0a6fbd73a6254e5be"
                                                }
                                            ],
                                            "tracking": {
                                                "run_id": "string",
                                                "start": False,
                                                "experiment_name": "string",
                                                "workflow_name": "string",
                                                "workflow_type": "experiment",
                                                "workflow_id": "string",
                                                "workflow_run_id": "string",
                                                "tags": {
                                                    "additionalProp1": "string",
                                                    "additionalProp2": "string",
                                                    "additionalProp3": "string"
                                                },
                                                "parameters": {
                                                    "cam_metrics": {
                                                        "coverage": 0.012755102040816327,
                                                        "center_ratio": 0.8249999997937499,
                                                        "lr_asym": 0.099999999975,
                                                        "tb_asym": 0.99999999975
                                                    },
                                                    "prediction": "kidney_tumor",
                                                    "cam_explanation": "The model focused on a localized region of the image, located centrally within the renal parenchyma, with asymmetric spatial distribution. In the context of a tumor prediction, this pattern suggests visually distinct renal regions that may correspond to localized structural alteration.",
                                                    "file_path": "[URL]http://looporchestra.sytes.net:4001/admin/admin/retrieve-image-file/nodes_bucket/626130f7c71f6b9e651c76be/69b862e0a6fbd73a6254e5be/87edd98d-8cb4-477f-8516-d3dbc77c242e.jpeg"
                                                },
                                                "metrics": {},
                                                "artifacts": {
                                                    "input_file": True,
                                                    "output_file": False,
                                                    "input_dataframe": False,
                                                    "model_file": False
                                                }
                                            },
                                            "node_name_dict": "image_analyzer_model",
                                            "executed": False,
                                            "node_id": "6946db821cc02c3427815adf",
                                            "prototype_id": "69b862e0a6fbd73a6254e5be"
                                        }
                                    ],
                                    "tracking": {
                                        "run_id": "string",
                                        "start": False,
                                        "experiment_name": "string",
                                        "workflow_name": "string",
                                        "workflow_type": "experiment",
                                        "workflow_id": "string",
                                        "workflow_run_id": "string",
                                        "tags": {
                                            "additionalProp1": "string",
                                            "additionalProp2": "string",
                                            "additionalProp3": "string"
                                        },
                                        "parameters": {
                                            "Inference time": "8.0548 s",
                                            "classes": "kidney_tumor",
                                            "confidence": 0.9999794960021973
                                        },
                                        "metrics": {},
                                        "artifacts": {
                                            "input_file": True,
                                            "output_file": False,
                                            "input_dataframe": False,
                                            "model_file": False
                                        }
                                    },
                                    "node_name_dict": "kidney_cancer_detection_model",
                                    "executed": False,
                                    "node_id": "6986172e677ea52be211de08",
                                    "prototype_id": "69b862e0a6fbd73a6254e5be"
                                }
                            ],
                            "tracking": {
                                "run_id": "string",
                                "start": False,
                                "experiment_name": "string",
                                "workflow_name": "string",
                                "workflow_type": "experiment",
                                "workflow_id": "string",
                                "workflow_run_id": "string",
                                "tags": {
                                    "additionalProp1": "string",
                                    "additionalProp2": "string",
                                    "additionalProp3": "string"
                                },
                                "parameters": {
                                    "File Path": "/upload/2026-03-16_09.31.20_ti3RRjX8SoRJWvUPiHQ8/kidney_test2.jpeg",
                                    "Sheet Name": 0,
                                    "Document Type": "jpg",
                                    "Document Size": "0.034 Mb"
                                },
                                "metrics": {},
                                "artifacts": {
                                    "input_file": True,
                                    "output_file": False,
                                    "input_dataframe": False,
                                    "model_file": False
                                },
                                "response": {
                                    "status": 200,
                                    "metadata": {
                                        "name": "NodeDataReader5",
                                        "type": "input.data-reader",
                                        "run_id": "8e4348850bdf4a3990e2a3597e3dc9b0",
                                        "workflow_name": "Test_Kidney_nexus",
                                        "workflow_type": "prototype",
                                        "workflow_id": "28",
                                        "workflow_run_id": "a79b2053d7754a93aeaf56cd42406e03"
                                    },
                                    "data": "626130f7c71f6b9e651c76be/69b862e0a6fbd73a6254e5be/kidney_test2.jpeg",
                                    "pdf_path": None
                                }
                            },
                            "node_name_dict": "NodeDataReader5",
                            "executed": False,
                            "node_id": "6936866fb56d784128f48718",
                            "prototype_id": "69b862e0a6fbd73a6254e5be"
                        }
                    ]
                }
            ],
            "external_nodes": []
        }
    ],
    "project_link_id": "",
    "concert_hall_id": "627392cbef51f1256835d0e8",
    "session_id": "6rh70xszeeie7ud251uvtk"
}


def _multipart_encode(field_name: str, file_path: Path):
    boundary = f"----OpenClawBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    parts = [
        f"--{boundary}\r\n".encode("utf-8"),
        (
            f'Content-Disposition: form-data; name="{field_name}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode("utf-8"),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
    ]
    return boundary, b"".join(parts)


def _normalize_upload_response(value):
    if isinstance(value, list):
        if not value:
            raise RuntimeError("Upload response was an empty list.")
        value = value[0]
    if not isinstance(value, dict):
        raise RuntimeError("Upload endpoint returned an unsupported JSON shape.")
    return value


def upload_image(local_image_path: str, telegram_user_id: str, timeout: int = 60) -> str:
    file_path = Path(local_image_path).expanduser().resolve()
    if not file_path.is_file():
        raise RuntimeError(f"Image file not found: {file_path}")

    query = parse.urlencode(
        {
            "storage_ref": FIXED_STORAGE_REF,
            "local_file_path": FIXED_LOCAL_FILE_PATH,
            "user_id": telegram_user_id,
        }
    )
    upload_url = f"{UPLOAD_BASE_URL}?{query}"
    boundary, body = _multipart_encode("file", file_path)
    req = request.Request(
        upload_url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            response_body = resp.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload failed with HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Upload request failed: {e}") from e

    try:
        parsed = json.loads(response_body)
    except json.JSONDecodeError as e:
        raise RuntimeError("Upload endpoint returned a non-JSON response.") from e

    parsed = _normalize_upload_response(parsed)
    remote_dir = parsed.get("path")
    filename = parsed.get("filename")
    if not isinstance(remote_dir, str) or not remote_dir:
        raise RuntimeError("Upload response is missing 'path'.")
    if not isinstance(filename, str) or not filename:
        raise RuntimeError("Upload response is missing 'filename'.")

    return f"{remote_dir}{filename}"


def _replace_image_placeholder(obj, uploaded_image_path: str):
    if isinstance(obj, dict):
        return {key: _replace_image_placeholder(value, uploaded_image_path) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_replace_image_placeholder(item, uploaded_image_path) for item in obj]
    if obj == "<image_path_here>":
        return uploaded_image_path
    return obj


def build_payload(uploaded_image_path: str):
    return _replace_image_placeholder(copy.deepcopy(REQUEST_TEMPLATE), uploaded_image_path)


def call_pipeline_execution(uploaded_image_path: str, timeout: int = 120):
    payload_obj = build_payload(uploaded_image_path)
    payload = json.dumps(payload_obj).encode("utf-8")
    req = request.Request(
        EXECUTION_ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Execution failed with HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise RuntimeError(f"Execution request failed: {e}") from e

    parsed_body = None
    try:
        parsed_body = json.loads(body)
    except json.JSONDecodeError:
        parsed_body = body

    return {
        "uploaded_image_path": uploaded_image_path,
        "endpoint": EXECUTION_ENDPOINT,
        "http_status": status,
        "content_type": content_type,
        "response": parsed_body,
    }


def find_latest_inbound_image() -> str:
    inbound_dir = Path("/home/node/.openclaw/media/inbound").resolve()
    if not inbound_dir.is_dir():
        raise RuntimeError(
            "Inbound media directory not found: /home/node/.openclaw/media/inbound. "
            "Pass --image-path explicitly if the image is stored elsewhere."
        )

    candidates = [
        path
        for path in inbound_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not candidates:
        raise RuntimeError(
            "No supported image files found in /home/node/.openclaw/media/inbound. "
            "Pass --image-path explicitly if needed."
        )

    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return str(latest)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Upload a local image with the same flow as the kidney cancer skill, replace "
            "the <image_path_here> placeholder inside the fixed prototype payload, then "
            "call the prototype execution endpoint and print the raw response as JSON."
        )
    )
    parser.add_argument(
        "image_path",
        nargs="?",
        help=(
            "Local image path to upload first. If omitted, the tool selects the most "
            "recent supported image from /home/node/.openclaw/media/inbound."
        ),
    )
    parser.add_argument(
        "--telegram-user-id",
        default=os.environ.get("TELEGRAM_USER_ID"),
        help="Telegram user id used as the upload endpoint's user_id query parameter.",
    )
    parser.add_argument("--timeout", type=int, default=120, help="Execution timeout in seconds.")
    parser.add_argument("--upload-timeout", type=int, default=60, help="Upload timeout in seconds.")
    args = parser.parse_args()

    if not args.telegram_user_id:
        raise RuntimeError(
            "Missing Telegram user id. Pass --telegram-user-id or set TELEGRAM_USER_ID."
        )

    local_image_path = args.image_path or find_latest_inbound_image()
    uploaded_image_path = upload_image(
        local_image_path=local_image_path,
        telegram_user_id=str(args.telegram_user_id),
        timeout=args.upload_timeout,
    )
    result = call_pipeline_execution(uploaded_image_path, timeout=args.timeout)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
