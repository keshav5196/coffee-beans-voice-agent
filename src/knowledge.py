"""Knowledge base for CoffeeBeans services and information.

Comprehensive information about CoffeeBeans Consulting based on coffeebeans.io
"""

from typing import Dict, List, Optional


class KnowledgeBase:
    """CoffeeBeans comprehensive knowledge base for the voice agent."""
    
    def __init__(self):
        self.company_info = self._load_company_info()
        self.services = self._load_services()
        self.case_studies = self._load_case_studies()
        self.value_propositions = self._load_value_propositions()
        self.objection_responses = self._load_objection_responses()
        self.qualifying_questions = self._load_qualifying_questions()
    
    def _load_company_info(self) -> Dict:
        """Load comprehensive company information."""
        return {
            "name": "CoffeeBeans Consulting",
            "tagline": "Brewing Innovations - Beyond Features, We Deliver Value",
            "founded": "2017",
            "headquarters": "Bengaluru, Karnataka, India",
            "us_presence": "Atlanta, Michigan, United States",
            "team_size": "168 employees",
            "founders": ["Santhosh Sagar Reddy", "Mitesh Bulsara", "Madhu Lakshmanan", "Naveen Kunapareddy"],
            "mission": "Technology-driven catalyst for business success",
            "vision": "Vision in Crafting, Design in Thinking - Intelligence Meets Innovation",
            "core_philosophy": "We intertwine thoughtful product strategies with revolutionary designs to craft experiences that resonate",
            "website": "coffeebeans.io",
            "email_format": "name@coffeebeans.io"
        }
    
    def _load_services(self) -> Dict:
        """Load detailed information about CoffeeBeans services."""
        return {
            "artificial_intelligence": {
                "name": "Artificial Intelligence",
                "tagline": "Intelligence Meets Innovation",
                "description": "We specialize in Generative AI, NLP, and Computer Vision, developing solutions that redefine technological innovation boundaries",
                "expertise": [
                    "Generative AI - Models that analyze and create",
                    "Natural Language Processing (NLP) - Enhance interactions and glean insights",
                    "Computer Vision - Interpret and act upon visual data",
                    "AI Interviewer - Automated recruitment solutions",
                    "Churn Prediction - Predictive analytics for customer retention"
                ],
                "pain_points": [
                    "ai pilots not scaling",
                    "ai deployment challenges",
                    "model creation to deployment",
                    "ai integration",
                    "machine learning implementation",
                    "predictive analytics needs"
                ],
                "outcomes": [
                    "Anticipate market changes",
                    "Optimize processes",
                    "Drive impactful decisions",
                    "Automated content creation",
                    "Enhanced user interactions"
                ],
                "key_message": "Data is the new currency, and AI is the mint. Organizations that master this currency will prosper in the AI-driven future"
            },
            "blockchain": {
                "name": "Blockchain",
                "tagline": "Security and Efficiency at Core",
                "description": "Cutting-edge Blockchain-based products using Hyperledger Fabric",
                "expertise": [
                    "Hyperledger Fabric development",
                    "Smart contracts",
                    "Decentralized applications",
                    "Supply chain blockchain solutions"
                ],
                "pain_points": [
                    "security concerns",
                    "transparency needs",
                    "supply chain visibility",
                    "trust protocols",
                    "fintech security"
                ],
                "domains": ["Fintech", "Healthcare", "Supply Chain Management"],
                "outcomes": [
                    "Enhanced security",
                    "Improved transparency",
                    "Streamlined operations",
                    "Democratized collaboration"
                ]
            },
            "big_data_analytics": {
                "name": "Big Data Analytics & Data Engineering",
                "tagline": "Transforming Data into Strategic Assets",
                "description": "End-to-end data pipelines, real-time streaming analytics, comprehensive data warehouses and lakes",
                "expertise": [
                    "Real-time streaming analytics",
                    "Data warehouse construction",
                    "Data lake architecture",
                    "ETL/ELT pipelines",
                    "Data governance frameworks",
                    "Scalable data infrastructure"
                ],
                "pain_points": [
                    "data quality issues",
                    "fragmented data",
                    "data silos",
                    "lack of data governance",
                    "scaling data infrastructure",
                    "real-time data processing"
                ],
                "outcomes": [
                    "Clean data pipelines",
                    "Unified data platform",
                    "Real-time insights",
                    "Improved data quality",
                    "Governed data assets"
                ]
            },
            "technology_advisory": {
                "name": "Technology Advisory & Consulting",
                "tagline": "Holistic Tech Empowerment",
                "description": "Custom solutions in software development, data engineering, DevOps, and digital transformation",
                "expertise": [
                    "Software development",
                    "Application modernization",
                    "DevOps implementation",
                    "Agile consulting",
                    "Product development",
                    "Mobile application development",
                    "UX/UI design",
                    "Business analysis",
                    "Process consulting",
                    "Product management"
                ],
                "pain_points": [
                    "legacy systems",
                    "digital transformation",
                    "agile adoption",
                    "devops maturity",
                    "cloud migration",
                    "technical debt"
                ],
                "outcomes": [
                    "Modernized infrastructure",
                    "Faster time to market",
                    "Improved agility",
                    "Enhanced collaboration",
                    "Scalable architecture"
                ]
            }
        }
    
    def _load_case_studies(self) -> List[Dict]:
        """Load client success stories and case studies."""
        return [
            {
                "client": "Supply Chain Management Platform",
                "industry": "Logistics & Supply Chain",
                "challenge": "Build unified platform for democratizing supply chain, allowing multiple participants to collaborate with visibility across shipping journey",
                "solution": "Single platform to onboard multiple service providers with complete transparency",
                "outcome": "Democratized supply chain collaboration with real-time visibility",
                "technologies": ["Blockchain", "Big Data", "Real-time Analytics"]
            },
            {
                "client": "Salam Kisan",
                "industry": "Agriculture Technology",
                "challenge": "Centralized end-to-end solution for agriculture value chain stakeholders",
                "solution": "Unified platform connecting farmers, dealers, and administrators",
                "outcome": "Empowered farmers and revolutionized farming industry operations",
                "impact": "Agricultural ecosystem transformation"
            },
            {
                "client": "The Quint",
                "industry": "Media & Publishing",
                "challenge": "Improve user engagement through personalized content",
                "solution": "WRU recommendation engine with hyper-personalized recommendations",
                "outcome": "Accurate recommendations, increased user engagement",
                "testimonial": "WRU recommendations have been very accurate and increased our user engagement"
            },
            {
                "client": "Ola",
                "industry": "Transportation & Mobility",
                "challenge": "Process transformation for organizational efficiency",
                "solution": "Comprehensive process restructuring with Agile methodologies",
                "outcome": "Faster delivery, smooth communication, streamlined prioritization, defined roles",
                "impact": "Complete organizational transformation"
            },
            {
                "client": "Insurance Industry Client",
                "industry": "Insurance & Fintech",
                "challenge": "AI and Gen AI integration for claims processing and customer experience",
                "solution": "Transformative AI implementation for streamlined operations",
                "outcome": "Enhanced claims processing, improved customer experiences, better risk assessment",
                "focus": "Gen AI revolutionizing insurance operations"
            }
        ]
    
    def _load_value_propositions(self) -> Dict:
        """Load key value propositions and differentiators."""
        return {
            "main_differentiators": [
                "Technology-driven catalyst for business success",
                "Holistic understanding of technology intersection",
                "From granularities of data to vast possibilities of AI",
                "Poised at vanguard of digital evolution",
                "Custom solutions tailored to unique business objectives"
            ],
            "client_types": [
                "Startups seeking innovative solutions",
                "Enterprises requiring digital transformation",
                "SaaS organizations needing scalability"
            ],
            "approach": [
                "Collaborative design and development",
                "Tangible results focus",
                "Innovative solutions emphasis",
                "Value creation priority",
                "Excellence commitment"
            ],
            "products": {
                "WRU": "Hyper-personalized recommendation engine powering major media houses",
                "FastNext": "AI recruitment platform matching talent based on technical skills, cultural fit, and career objectives"
            },
            "team_values": [
                "Positive attitude",
                "Sense of ownership",
                "Insatiable hunger to learn",
                "Cutting-edge technology expertise",
                "Good engineering practices"
            ]
        }
    
    def _load_objection_responses(self) -> Dict:
        """Load common objections and appropriate responses."""
        return {
            "too_expensive": {
                "response": "I understand budget is a key consideration. What's interesting is that our clients often find the ROI justifies the investment within months. For example, The Quint saw immediate engagement increases with our WRU recommendation engine. We focus on delivering tangible value, not just features. Would you be open to discussing a phased approach that aligns with your budget?",
                "key_points": ["ROI focus", "Proven results", "Flexible engagement models"]
            },
            "have_internal_team": {
                "response": "That's great that you have an internal team! Many of our best partnerships are with companies who have strong technical teams. We don't replace your team - we accelerate them. Like with Ola, we helped transform their processes while empowering their existing structure. We bring specialized expertise in AI, blockchain, and big data that complements your team's domain knowledge. Would it be valuable to explore how we could help your team move faster?",
                "key_points": ["Partnership not replacement", "Specialized expertise", "Acceleration focus"]
            },
            "not_right_time": {
                "response": "I appreciate you being upfront. Timing is important. However, I'd mention that technology investments often take 6-12 months to show full value. Companies that start planning now tend to be ahead when they're ready. Could we schedule a brief discovery call for when timing is better? That way, you'll have a clearer roadmap when you're ready to move forward.",
                "key_points": ["Future planning", "Competitive advantage", "Low-commitment next step"]
            },
            "need_to_think": {
                "response": "Absolutely, these are important decisions. What might help is if I send you some relevant case studies - perhaps our work with The Quint or our supply chain platform. Would it also be useful to schedule a brief consultation where we can discuss your specific challenges? No commitment, just exploring if there's a fit.",
                "key_points": ["Provide resources", "Low-pressure follow-up", "Value-first approach"]
            },
            "working_with_competitor": {
                "response": "I'm glad you're already investing in this area. Many clients work with us alongside other partners because we bring unique strengths - particularly our holistic approach that spans from data engineering to AI deployment. What specific challenges are you still facing with your current setup?",
                "key_points": ["Unique differentiators", "Complementary services", "Problem-focused"]
            },
            "too_busy": {
                "response": "I completely understand - everyone's stretched thin. That's actually why companies reach out to us - to accelerate without adding burden to their team. Would you prefer I send you a brief overview via email, or would a 15-minute call next week work better to see if we might save you time in the long run?",
                "key_points": ["Respect time", "Efficiency focus", "Flexible engagement"]
            }
        }
    
    def _load_qualifying_questions(self) -> List[Dict]:
        """Load qualification questions for different scenarios."""
        return [
            {
                "category": "Industry & Domain",
                "questions": [
                    "What industry are you in?",
                    "What's your primary business model?",
                    "Who are your main customers?"
                ]
            },
            {
                "category": "Current Technology State",
                "questions": [
                    "What's your current technology stack?",
                    "Are you using any AI or ML currently?",
                    "How do you currently handle data?",
                    "What cloud infrastructure are you on?"
                ]
            },
            {
                "category": "Pain Points",
                "questions": [
                    "What's the biggest technology challenge you're facing?",
                    "What's preventing you from scaling right now?",
                    "Are there any bottlenecks in your current processes?"
                ]
            },
            {
                "category": "Decision Making",
                "questions": [
                    "What's your role in technology decisions?",
                    "Who else would be involved in evaluating solutions?",
                    "What's your typical timeline for these decisions?"
                ]
            }
        ]
    
    def match_service_to_pain_point(self, pain_point: str) -> Optional[str]:
        """Match a pain point to the most relevant service."""
        pain_point_lower = pain_point.lower()
        
        # Check each service for matching pain points
        for service_key, service_info in self.services.items():
            pain_points = service_info.get("pain_points", [])
            if any(pp in pain_point_lower for pp in pain_points):

                
                return service_key
        
        # Default to AI if no specific match
        return "artificial_intelligence"
    
    def get_elevator_pitch(self, duration: str = "short") -> str:
        """Get elevator pitch of appropriate length."""
        if duration == "short":
            return (
                "CoffeeBeans is a technology consulting firm specializing in AI, Blockchain, and Big Data. "
                "We help startups and enterprises transform their operations through innovative solutions. "
                "We've worked with companies like The Quint, Ola, and Salam Kisan to deliver real business value."
            )
        else:  # detailed
            return (
                "CoffeeBeans Consulting is a technology-driven catalyst for business success, founded in 2017. "
                "We specialize in Artificial Intelligence, Blockchain, and Big Data Analytics. Our mission is simple: "
                "go beyond features to deliver real value. We work with startups, enterprises, and SaaS organizations, "
                "providing everything from AI solutions and data engineering to DevOps and digital transformation. "
                "Our team of 168 professionals has delivered transformative results for clients including The Quint, "
                "Ola, and various insurance and supply chain companies. We're based in Bengaluru with presence in "
                "the US, and we're passionate about turning cutting-edge technology into business outcomes."
            )
    
    def get_service_talking_points(self, service_key: str) -> Dict:
        """Get detailed talking points for a specific service."""
        service = self.services.get(service_key, {})
        return {
            "name": service.get("name"),
            "description": service.get("description"),
            "key_benefits": service.get("outcomes", []),
            "expertise_areas": service.get("expertise", []),
            "relevant_cases": self._get_relevant_case_studies(service_key)
        }
    
    def _get_relevant_case_studies(self, service_key: str) -> List[Dict]:
        """Get case studies relevant to a specific service."""
        relevant_cases = []
        
        service_to_tech_map = {
            "artificial_intelligence": ["AI", "ML", "Machine Learning", "Predictive"],
            "blockchain": ["Blockchain", "Supply Chain"],
            "big_data_analytics": ["Big Data", "Data", "Analytics"],
            "technology_advisory": ["Process", "Agile", "DevOps"]
        }
        
        keywords = service_to_tech_map.get(service_key, [])
        
        for case in self.case_studies:
            case_text = str(case).lower()
            if any(keyword.lower() in case_text for keyword in keywords):
                relevant_cases.append(case)
        
        return relevant_cases[:2]  # Return top 2 most relevant


# Global knowledge base instance
knowledge_base = KnowledgeBase()