#!/usr/bin/env python3
"""
Demo script for National Dairy Farm MCP Server

Demonstrates various operations and use cases.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
from client import DairyFarmMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DairyFarmDemo:
    """Demo scenarios for the Dairy Farm MCP Server."""
    
    def __init__(self, client: DairyFarmMCPClient):
        self.client = client
        self.demo_data = {
            "farm_id": None,
            "coop_id": None,
            "user_id": None,
            "evaluation_id": None
        }
    
    async def run_full_demo(self):
        """Run all demo scenarios."""
        print("🐄 National Dairy Farm MCP Server Demo")
        print("=" * 50)
        
        scenarios = [
            ("Server Health Check", self.demo_health_check),
            ("List Available Operations", self.demo_list_operations),
            ("Cooperative Management", self.demo_coop_management),
            ("Farm Management", self.demo_farm_management),
            ("User Management", self.demo_user_management),
            ("Evaluation Workflow", self.demo_evaluation_workflow),
            ("Search Operations", self.demo_search_operations),
            ("Analytics & Reporting", self.demo_analytics),
            ("LCA Reports", self.demo_lca_reports),
            ("Attachment Management", self.demo_attachments)
        ]
        
        for title, scenario in scenarios:
            print(f"\n📋 {title}")
            print("-" * 30)
            
            try:
                await scenario()
                print("✅ Scenario completed successfully")
            except Exception as e:
                print(f"❌ Scenario failed: {e}")
                logger.error(f"Demo scenario '{title}' failed", exc_info=True)
            
            # Pause between scenarios
            await asyncio.sleep(1)
        
        print(f"\n🎉 Demo completed!")
    
    async def demo_health_check(self):
        """Demonstrate health check."""
        health = await self.client.health_check()
        print(f"Server status: {health.get('status', 'unknown')}")
        
        if health.get('dairy_farm_api_connected'):
            print("✅ Connected to Dairy Farm API")
        else:
            print("❌ Not connected to Dairy Farm API")
    
    async def demo_list_operations(self):
        """Demonstrate listing operations."""
        operations = await self.client.list_operations()
        print(f"Available operations: {len(operations)}")
        
        # Show first few operations
        for op in operations[:5]:
            print(f"  • {op['name']}: {op['description']}")
        
        if len(operations) > 5:
            print(f"  ... and {len(operations) - 5} more operations")
    
    async def demo_coop_management(self):
        """Demonstrate cooperative management."""
        print("Creating a new cooperative...")
        
        # Create cooperative
        create_result = await self.client.execute_operation("create_coop", {
            "name": "Demo Cooperative",
            "description": "A demonstration cooperative for testing",
            "contact_info": {
                "email": "demo@example.com",
                "phone": "555-0123"
            }
        })
        
        if create_result.get("success"):
            print("✅ Cooperative created")
            # Extract coop_id if available
            if create_result.get("result", {}).get("id"):
                self.demo_data["coop_id"] = create_result["result"]["id"]
        else:
            print("❌ Failed to create cooperative")
        
        # List cooperatives
        list_result = await self.client.execute_operation("list_coops", {
            "page": 0,
            "size": 10
        })
        
        if list_result.get("success"):
            coops = list_result.get("result", {})
            print(f"Listed {coops.get('totalElements', 0)} cooperatives")
    
    async def demo_farm_management(self):
        """Demonstrate farm management."""
        print("Managing farm data...")
        
        # Create farm
        farm_data = {
            "name": "Demo Farm",
            "location": {
                "address": "123 Farm Road",
                "city": "Dairy City",
                "state": "WI",
                "zip": "12345"
            },
            "contact_info": {
                "owner": "John Farmer",
                "email": "john@demofarm.com",
                "phone": "555-0456"
            }
        }
        
        if self.demo_data.get("coop_id"):
            farm_data["coop_id"] = self.demo_data["coop_id"]
        
        create_result = await self.client.execute_operation("create_farm", farm_data)
        
        if create_result.get("success"):
            print("✅ Farm created")
            if create_result.get("result", {}).get("id"):
                self.demo_data["farm_id"] = create_result["result"]["id"]
        
        # List farms
        list_result = await self.client.execute_operation("list_farms", {
            "page": 0,
            "size": 10,
            "sort": "name"
        })
        
        if list_result.get("success"):
            farms = list_result.get("result", {})
            print(f"Listed {farms.get('totalElements', 0)} farms")
        
        # Update farm if we have an ID
        if self.demo_data.get("farm_id"):
            update_result = await self.client.execute_operation("update_farm", {
                "farm_id": self.demo_data["farm_id"],
                "name": "Updated Demo Farm",
                "location": farm_data["location"]
            })
            
            if update_result.get("success"):
                print("✅ Farm updated")
    
    async def demo_user_management(self):
        """Demonstrate user management."""
        print("Managing users...")
        
        # Create user
        user_data = {
            "username": "demo_user",
            "email": "demo.user@example.com",
            "role": "farm_evaluator",
            "permissions": ["read_farms", "create_evaluations"]
        }
        
        if self.demo_data.get("coop_id"):
            user_data["coop_id"] = self.demo_data["coop_id"]
        
        create_result = await self.client.execute_operation("create_user", user_data)
        
        if create_result.get("success"):
            print("✅ User created")
            if create_result.get("result", {}).get("id"):
                self.demo_data["user_id"] = create_result["result"]["id"]
        
        # List users
        list_result = await self.client.execute_operation("list_users", {
            "page": 0,
            "size": 10,
            "role": "farm_evaluator"
        })
        
        if list_result.get("success"):
            users = list_result.get("result", {})
            print(f"Listed {users.get('totalElements', 0)} users")
    
    async def demo_evaluation_workflow(self):
        """Demonstrate evaluation workflow."""
        print("Running evaluation workflow...")
        
        if not self.demo_data.get("farm_id"):
            print("⚠️ No farm available for evaluation")
            return
        
        # Create evaluation
        evaluation_data = {
            "farm_id": self.demo_data["farm_id"],
            "evaluation_type": "animal_care",
            "scheduled_date": "2024-02-01",
            "notes": "Annual animal care evaluation"
        }
        
        if self.demo_data.get("user_id"):
            evaluation_data["evaluator_id"] = self.demo_data["user_id"]
        
        create_result = await self.client.execute_operation("create_evaluation", evaluation_data)
        
        if create_result.get("success"):
            print("✅ Evaluation created")
            if create_result.get("result", {}).get("id"):
                self.demo_data["evaluation_id"] = create_result["result"]["id"]
        
        # List evaluations
        list_result = await self.client.execute_operation("list_evaluations", {
            "farm_id": self.demo_data["farm_id"],
            "status": "scheduled"
        })
        
        if list_result.get("success"):
            evaluations = list_result.get("result", {})
            print(f"Listed {evaluations.get('totalElements', 0)} evaluations")
        
        # Update evaluation (simulate completion)
        if self.demo_data.get("evaluation_id"):
            update_result = await self.client.execute_operation("update_evaluation", {
                "evaluation_id": self.demo_data["evaluation_id"],
                "status": "completed",
                "results": {
                    "animal_care_score": 95,
                    "compliance_status": "excellent",
                    "recommendations": ["Continue current practices"]
                },
                "completion_date": "2024-02-01"
            })
            
            if update_result.get("success"):
                print("✅ Evaluation completed")
    
    async def demo_search_operations(self):
        """Demonstrate search capabilities."""
        print("Testing search operations...")
        
        # Search farms
        search_result = await self.client.execute_operation("search_farms", {
            "q": "demo",
            "page": 0,
            "size": 10,
            "filters": {"state": "WI"}
        })
        
        if search_result.get("success"):
            results = search_result.get("result", {})
            print(f"Found {results.get('totalElements', 0)} farms matching 'demo'")
        
        # Search evaluations
        if self.demo_data.get("farm_id"):
            eval_search = await self.client.execute_operation("search_evaluations", {
                "q": "animal_care",
                "filters": {"farm_id": self.demo_data["farm_id"]},
                "page": 0,
                "size": 5
            })
            
            if eval_search.get("success"):
                results = eval_search.get("result", {})
                print(f"Found {results.get('totalElements', 0)} evaluations matching 'animal_care'")
    
    async def demo_analytics(self):
        """Demonstrate analytics capabilities."""
        print("Generating analytics...")
        
        if self.demo_data.get("farm_id"):
            # Farm analytics
            farm_analytics = await self.client.execute_operation("get_farm_analytics", {
                "farm_id": self.demo_data["farm_id"],
                "metrics": ["milk_production", "animal_welfare", "environmental_impact"],
                "period": "last_year",
                "aggregation": "monthly"
            })
            
            if farm_analytics.get("success"):
                print("✅ Farm analytics generated")
        
        if self.demo_data.get("coop_id"):
            # Cooperative analytics
            coop_analytics = await self.client.execute_operation("get_coop_analytics", {
                "coop_id": self.demo_data["coop_id"],
                "metrics": ["total_farms", "evaluation_compliance", "certification_status"],
                "period": "current_year"
            })
            
            if coop_analytics.get("success"):
                print("✅ Cooperative analytics generated")
        
        # Evaluation trends
        trends = await self.client.execute_operation("get_evaluation_trends", {
            "period": "last_6_months",
            "metrics": ["compliance_scores", "certification_rates"]
        })
        
        if trends.get("success"):
            print("✅ Evaluation trends analyzed")
    
    async def demo_lca_reports(self):
        """Demonstrate Life Cycle Analysis reports."""
        print("Managing LCA reports...")
        
        if not self.demo_data.get("farm_id"):
            print("⚠️ No farm available for LCA report")
            return
        
        # Create LCA report
        lca_data = {
            "farm_id": self.demo_data["farm_id"],
            "report_type": "carbon_footprint",
            "year": 2023,
            "data": {
                "milk_production": 1000000,  # kg per year
                "feed_consumption": 500000,  # kg per year
                "energy_usage": 50000,      # kWh per year
                "methane_emissions": 1500   # kg CO2 equivalent
            },
            "methodology": "IPCC_2006"
        }
        
        create_result = await self.client.execute_operation("create_lca_report", lca_data)
        
        if create_result.get("success"):
            print("✅ LCA report created")
        
        # List LCA reports
        list_result = await self.client.execute_operation("list_lca_reports", {
            "farm_id": self.demo_data["farm_id"],
            "report_type": "carbon_footprint",
            "year": 2023
        })
        
        if list_result.get("success"):
            reports = list_result.get("result", {})
            print(f"Listed {reports.get('totalElements', 0)} LCA reports")
    
    async def demo_attachments(self):
        """Demonstrate attachment management."""
        print("Managing attachments...")
        
        if not self.demo_data.get("farm_id"):
            print("⚠️ No farm available for attachments")
            return
        
        # List attachments for farm
        list_result = await self.client.execute_operation("list_attachments", {
            "entity_type": "farm",
            "entity_id": self.demo_data["farm_id"],
            "page": 0,
            "size": 10
        })
        
        if list_result.get("success"):
            attachments = list_result.get("result", {})
            print(f"Listed {attachments.get('totalElements', 0)} attachments")
        
        # Note: File upload would require actual file handling
        print("📎 File upload operations require actual file data")
    
    def print_operation_result(self, operation: str, result: Dict[str, Any]):
        """Pretty print operation result."""
        print(f"\n📊 {operation} Result:")
        if result.get("success"):
            print("✅ Success")
            if result.get("result"):
                print(json.dumps(result["result"], indent=2)[:500] + "...")
        else:
            print("❌ Failed")
            if result.get("error"):
                print(f"Error: {result['error']}")


async def main():
    """Run the demo."""
    import argparse
    
    parser = argparse.ArgumentParser(description="National Dairy Farm MCP Demo")
    parser.add_argument("--server", default="http://localhost:8001", 
                       help="MCP server URL")
    parser.add_argument("--token", help="Authentication token")
    parser.add_argument("--scenario", 
                       choices=["health", "operations", "coops", "farms", "users", 
                               "evaluations", "search", "analytics", "lca", "attachments", "all"],
                       default="all", help="Demo scenario to run")
    
    args = parser.parse_args()
    
    # Create client
    client = DairyFarmMCPClient(
        mcp_server_url=args.server,
        auth_token=args.token
    )
    
    demo = DairyFarmDemo(client)
    
    try:
        if args.scenario == "all":
            await demo.run_full_demo()
        elif args.scenario == "health":
            await demo.demo_health_check()
        elif args.scenario == "operations":
            await demo.demo_list_operations()
        elif args.scenario == "coops":
            await demo.demo_coop_management()
        elif args.scenario == "farms":
            await demo.demo_farm_management()
        elif args.scenario == "users":
            await demo.demo_user_management()
        elif args.scenario == "evaluations":
            await demo.demo_evaluation_workflow()
        elif args.scenario == "search":
            await demo.demo_search_operations()
        elif args.scenario == "analytics":
            await demo.demo_analytics()
        elif args.scenario == "lca":
            await demo.demo_lca_reports()
        elif args.scenario == "attachments":
            await demo.demo_attachments()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())