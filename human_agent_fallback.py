"""
Human Agent Fallback System for Motorcycle Dealership
Routes complex queries to human agents when AI cannot handle them adequately
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
import time
import os

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"

class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    BREAK = "break"

class EscalationReason(Enum):
    TECHNICAL_ISSUE = "technical_issue"
    COMPLEX_QUERY = "complex_query"
    CUSTOMER_COMPLAINT = "customer_complaint"
    PRICE_NEGOTIATION = "price_negotiation"
    CUSTOM_REQUIREMENTS = "custom_requirements"
    LANGUAGE_BARRIER = "language_barrier"
    EMERGENCY = "emergency"

@dataclass
class HumanAgent:
    id: str
    name: str
    email: str
    phone: str
    expertise: List[str]  # ["sales", "service", "finance", "complaints"]
    languages: List[str]
    status: AgentStatus = AgentStatus.AVAILABLE
    current_chats: int = 0
    max_chats: int = 5
    last_activity: str = ""

    def __post_init__(self):
        if not self.last_activity:
            self.last_activity = datetime.now().isoformat()

@dataclass
class EscalatedQuery:
    id: str
    customer_id: str
    query: str
    complexity: QueryComplexity
    reason: EscalationReason
    agent_id: str = ""
    status: str = "pending"  # pending, assigned, resolved, closed
    created_time: str = ""
    assigned_time: str = ""
    resolved_time: str = ""
    priority: int = 1  # 1-5, 5 being highest
    notes: str = ""

    def __post_init__(self):
        if not self.created_time:
            self.created_time = datetime.now().isoformat()

class HumanAgentFallback:
    """
    Manages human agent fallback system for complex queries
    """

    def __init__(self):
        self.agents = []
        self.escalated_queries = []
        self.complexity_thresholds = {
            "max_retries": 3,
            "confidence_threshold": 0.7,
            "response_time_threshold": 30  # seconds
        }
        self.initialize_agents()
        self.agent_assignment_thread = None
        self.start_agent_assignment()

    def initialize_agents(self):
        """Initialize human agents"""
        self.agents = [
            HumanAgent(
                id="agent_1",
                name="Rajesh Kumar",
                email="rajesh@everylingua.com",
                phone="+91-9876543211",
                expertise=["sales", "test_rides", "finance"],
                languages=["hi", "en", "mr"],
                max_chats=5
            ),
            HumanAgent(
                id="agent_2",
                name="Priya Sharma",
                email="priya@everylingua.com",
                phone="+91-9876543212",
                expertise=["service", "maintenance", "complaints"],
                languages=["en", "hi", "ta"],
                max_chats=4
            ),
            HumanAgent(
                id="agent_3",
                name="Amit Patel",
                email="amit@everylingua.com",
                phone="+91-9876543213",
                expertise=["sales", "custom_requirements", "price_negotiation"],
                languages=["en", "hi", "gu"],
                max_chats=6
            ),
            HumanAgent(
                id="agent_4",
                name="Sneha Reddy",
                email="sneha@everylingua.com",
                phone="+91-9876543214",
                expertise=["service", "emergency", "complaints"],
                languages=["en", "hi", "te", "kn"],
                max_chats=4
            )
        ]

    def start_agent_assignment(self):
        """Start background thread for agent assignment"""
        if self.agent_assignment_thread is None or not self.agent_assignment_thread.is_alive():
            self.agent_assignment_thread = threading.Thread(target=self._agent_assignment_loop, daemon=True)
            self.agent_assignment_thread.start()

    def _agent_assignment_loop(self):
        """Background loop to assign pending queries to available agents"""
        while True:
            try:
                self.assign_pending_queries()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in agent assignment loop: {e}")
                time.sleep(30)

    def assign_pending_queries(self):
        """Assign pending queries to available agents"""
        pending_queries = [q for q in self.escalated_queries if q.status == "pending"]

        for query in pending_queries:
            agent = self.find_best_agent(query)
            if agent:
                self.assign_query_to_agent(query, agent)

    def find_best_agent(self, query: EscalatedQuery) -> Optional[HumanAgent]:
        """Find the best available agent for a query"""
        available_agents = [agent for agent in self.agents
                          if agent.status == AgentStatus.AVAILABLE
                          and agent.current_chats < agent.max_chats]

        if not available_agents:
            return None

        # Score agents based on expertise and language match
        best_agent = None
        best_score = -1

        for agent in available_agents:
            score = 0

            # Expertise match
            for expertise in query.reason.value.split('_'):
                if expertise in agent.expertise:
                    score += 2

            # Language match (assuming query language is detected)
            if hasattr(query, 'language') and query.language in agent.languages:
                score += 1

            # Priority boost for critical queries
            if query.priority >= 4:
                score += 1

            # Prefer agents with fewer active chats
            score += (agent.max_chats - agent.current_chats) * 0.5

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent

    def assign_query_to_agent(self, query: EscalatedQuery, agent: HumanAgent) -> bool:
        """Assign a query to an agent"""
        try:
            query.agent_id = agent.id
            query.status = "assigned"
            query.assigned_time = datetime.now().isoformat()

            agent.current_chats += 1
            agent.last_activity = datetime.now().isoformat()

            # In real implementation, notify agent via email/SMS/push notification
            self.notify_agent_assignment(agent, query)

            return True
        except Exception as e:
            print(f"Error assigning query to agent: {e}")
            return False

    def notify_agent_assignment(self, agent: HumanAgent, query: EscalatedQuery):
        """Notify agent about new assignment"""
        notification_message = f"""
New customer query assigned to you:

Query ID: {query.id}
Customer ID: {query.customer_id}
Priority: {query.priority}/5
Reason: {query.reason.value.replace('_', ' ').title()}

Query: {query.query}

Please respond within 15 minutes.

Access the query at: http://localhost:5000/agent/{query.id}
"""

        print(f"Notification sent to {agent.name}: {agent.email}")
        # In real implementation, send email/SMS/push notification

    def should_escalate_to_human(self, query: str, ai_response: str = "",
                               confidence: float = 0.0, response_time: float = 0.0) -> Tuple[bool, EscalationReason]:
        """
        Determine if a query should be escalated to a human agent
        Returns (should_escalate, reason)
        """

        # Check for explicit escalation keywords
        escalation_keywords = [
            "speak to human", "talk to agent", "customer service", "complaint",
            "not satisfied", "wrong information", "confused", "help me",
            "emergency", "urgent", "problem", "issue", "broken", "not working"
        ]

        if any(keyword in query.lower() for keyword in escalation_keywords):
            return True, EscalationReason.CUSTOMER_COMPLAINT

        # Check for complex financial queries
        financial_keywords = [
            "negotiate", "discount", "bargain", "lower price", "best price",
            "offer", "deal", "finance", "loan", "emi", "installment"
        ]

        if any(keyword in query.lower() for keyword in financial_keywords):
            return True, EscalationReason.PRICE_NEGOTIATION

        # Check for custom requirements
        custom_keywords = [
            "custom", "modify", "special", "specific", "particular",
            "requirement", "need", "want", "looking for", "prefer"
        ]

        if any(keyword in query.lower() for keyword in custom_keywords):
            return True, EscalationReason.CUSTOM_REQUIREMENTS

        # Check for technical issues
        technical_keywords = [
            "not working", "broken", "error", "problem", "issue",
            "malfunction", "defect", "damage", "repair", "fix"
        ]

        if any(keyword in query.lower() for keyword in technical_keywords):
            return True, EscalationReason.TECHNICAL_ISSUE

        # Check AI confidence and response time
        if confidence < self.complexity_thresholds["confidence_threshold"]:
            return True, EscalationReason.COMPLEX_QUERY

        if response_time > self.complexity_thresholds["response_time_threshold"]:
            return True, EscalationReason.COMPLEX_QUERY

        # Check for emergency keywords
        emergency_keywords = [
            "emergency", "urgent", "immediately", "asap", "help",
            "accident", "stuck", "stranded", "danger", "safety"
        ]

        if any(keyword in query.lower() for keyword in emergency_keywords):
            return True, EscalationReason.EMERGENCY

        return False, None

    def escalate_query(self, customer_id: str, query: str, reason: EscalationReason,
                      priority: int = 1, language: str = "en") -> Dict:
        """Escalate a query to human agent"""
        try:
            query_id = f"ESC_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            escalated_query = EscalatedQuery(
                id=query_id,
                customer_id=customer_id,
                query=query,
                complexity=QueryComplexity.CRITICAL if priority >= 4 else QueryComplexity.COMPLEX,
                reason=reason,
                priority=priority
            )

            if hasattr(escalated_query, 'language'):
                escalated_query.language = language

            self.escalated_queries.append(escalated_query)

            return {
                "success": True,
                "query_id": query_id,
                "message": "Query escalated to human agent. You will receive a response shortly.",
                "estimated_wait_time": self.get_estimated_wait_time()
            }

        except Exception as e:
            print(f"Error escalating query: {e}")
            return {
                "success": False,
                "message": "Failed to escalate query. Please try again later."
            }

    def get_estimated_wait_time(self) -> str:
        """Get estimated wait time for human agent response"""
        available_agents = len([agent for agent in self.agents
                              if agent.status == AgentStatus.AVAILABLE
                              and agent.current_chats < agent.max_chats])

        pending_queries = len([q for q in self.escalated_queries if q.status == "pending"])

        if available_agents == 0:
            return "15-30 minutes"
        elif pending_queries == 0:
            return "2-5 minutes"
        else:
            wait_time = (pending_queries / available_agents) * 10
            return f"{int(wait_time)}-{int(wait_time * 1.5)} minutes"

    def get_agent_response(self, query_id: str) -> Optional[Dict]:
        """Get response from human agent for a query"""
        for query in self.escalated_queries:
            if query.id == query_id and query.status == "resolved":
                return {
                    "query_id": query_id,
                    "response": "Response from human agent",  # In real implementation, get from agent
                    "agent_name": next((agent.name for agent in self.agents if agent.id == query.agent_id), "Unknown"),
                    "response_time": query.resolved_time
                }
        return None

    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """Update agent status"""
        try:
            for agent in self.agents:
                if agent.id == agent_id:
                    agent.status = status
                    agent.last_activity = datetime.now().isoformat()
                    return True
            return False
        except Exception as e:
            print(f"Error updating agent status: {e}")
            return False

    def get_agent_dashboard_data(self) -> Dict:
        """Get data for agent dashboard"""
        return {
            "total_agents": len(self.agents),
            "available_agents": len([a for a in self.agents if a.status == AgentStatus.AVAILABLE]),
            "busy_agents": len([a for a in self.agents if a.status == AgentStatus.BUSY]),
            "total_queries": len(self.escalated_queries),
            "pending_queries": len([q for q in self.escalated_queries if q.status == "pending"]),
            "resolved_queries": len([q for q in self.escalated_queries if q.status == "resolved"]),
            "agents": [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "status": agent.status.value,
                    "current_chats": agent.current_chats,
                    "expertise": agent.expertise
                }
                for agent in self.agents
            ]
        }

    def resolve_query(self, query_id: str, agent_response: str) -> bool:
        """Mark a query as resolved with agent response"""
        try:
            for query in self.escalated_queries:
                if query.id == query_id:
                    query.status = "resolved"
                    query.resolved_time = datetime.now().isoformat()

                    # Update agent chat count
                    for agent in self.agents:
                        if agent.id == query.agent_id:
                            agent.current_chats = max(0, agent.current_chats - 1)
                            break

                    return True
            return False
        except Exception as e:
            print(f"Error resolving query: {e}")
            return False

# Global human agent fallback instance
human_agent_fallback = HumanAgentFallback()

def should_escalate_to_human(query: str, ai_response: str = "",
                           confidence: float = 0.0, response_time: float = 0.0) -> Tuple[bool, EscalationReason]:
    """Check if query should be escalated to human agent"""
    return human_agent_fallback.should_escalate_to_human(query, ai_response, confidence, response_time)

def escalate_query(customer_id: str, query: str, reason: EscalationReason,
                  priority: int = 1, language: str = "en") -> Dict:
    """Escalate query to human agent"""
    return human_agent_fallback.escalate_query(customer_id, query, reason, priority, language)

def get_agent_response(query_id: str) -> Optional[Dict]:
    """Get response from human agent"""
    return human_agent_fallback.get_agent_response(query_id)

def get_agent_dashboard() -> Dict:
    """Get agent dashboard data"""
    return human_agent_fallback.get_agent_dashboard_data()

def update_agent_status(agent_id: str, status: AgentStatus) -> bool:
    """Update agent status"""
    return human_agent_fallback.update_agent_status(agent_id, status)

def resolve_query(query_id: str, agent_response: str) -> bool:
    """Resolve a query with agent response"""
    return human_agent_fallback.resolve_query(query_id, agent_response)
