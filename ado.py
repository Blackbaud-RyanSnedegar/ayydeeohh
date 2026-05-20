#!/usr/bin/env python3

import argparse
import requests
import base64
import json
import sys

class ADOTicketClient:
    def __init__(self, organization, project, pat):
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit"
        token = base64.b64encode(f":{pat}".encode()).decode()
        self.headers = {
            "Content-Type": "application/json-patch+json",
            "Authorization": f"Basic {token}"
        }

    def create(self, work_item_type, title, description, fields):
        url = f"{self.base_url}/workitems/${work_item_type}?api-version=7.1"

        payload = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description}
        ]

        for key, value in fields.items():
            payload.append({
                "op": "add",
                "path": f"/fields/{key}",
                "value": value
            })

        return self._request("POST", url, payload)

    def update(self, work_item_id, fields):
        url = f"{self.base_url}/workitems/{work_item_id}?api-version=7.1"

        payload = [
            {"op": "add", "path": f"/fields/{k}", "value": v}
            for k, v in fields.items()
        ]

        return self._request("PATCH", url, payload)

    def close(self, work_item_id):
        return self.update(work_item_id, {"System.State": "Closed"})

    def get(self, work_item_id):
        url = f"{self.base_url}/workitems/{work_item_id}?api-version=7.1"
        response = requests.get(url, headers=self.headers)
        self._check(response)
        return response.json()

    def _request(self, method, url, payload):
        response = requests.request(
            method,
            url,
            headers=self.headers,
            data=json.dumps(payload)
        )
        self._check(response)
        return response.json()

    def _check(self, response):
        if not response.ok:
            print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
            sys.exit(1)


# ------------------------------
# CLI ENTRYPOINT
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="ADO CLI Tool")

    # Global args
    parser.add_argument("--org", required=True, help="ADO organization")
    parser.add_argument("--project", required=True, help="ADO project")
    parser.add_argument("--pat", required=True, help="Personal Access Token")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # CREATE
    create_parser = subparsers.add_parser("create", help="Create work item")
    create_parser.add_argument("--type", required=True, help="Work item type (Task, Bug, etc)")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--description", default="")
    create_parser.add_argument("--field", action="append", help="Extra field (key=value)")

    # UPDATE
    update_parser = subparsers.add_parser("update", help="Update work item")
    update_parser.add_argument("--id", type=int, required=True)
    update_parser.add_argument("--field", action="append", required=True, help="key=value")

    # CLOSE
    close_parser = subparsers.add_parser("close", help="Close work item")
    close_parser.add_argument("--id", type=int, required=True)

    # GET
    get_parser = subparsers.add_parser("get", help="Get work item")
    get_parser.add_argument("--id", type=int, required=True)

    args = parser.parse_args()

    client = ADOTicketClient(args.org, args.project, args.pat)

    # --- Parse field inputs ---
    def parse_fields(field_list):
        fields = {}
        if field_list:
            for item in field_list:
                if "=" not in item:
                    print(f"Invalid field format: {item}", file=sys.stderr)
                    sys.exit(1)
                k, v = item.split("=", 1)
                fields[k] = v
        return fields

    # --- Command handling ---
    if args.command == "create":
        fields = parse_fields(args.field)
        result = client.create(args.type, args.title, args.description, fields)

    elif args.command == "update":
        fields = parse_fields(args.field)
        result = client.update(args.id, fields)

    elif args.command == "close":
        result = client.close(args.id)

    elif args.command == "get":
        result = client.get(args.id)

    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

